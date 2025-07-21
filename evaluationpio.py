import os
from Solver import Solver
import math
import numpy as np
import random
import traceback

def print_lines(lines):
    for line in lines:
        print(line)

def fts(lst):
    return ' '.join(str(x) for x in lst)


def hand_value(hand):
    r = connection.command(line="show_hand_order")
    hands = r[0].split()
    for i in range(1326):
        if (hands[i] == hand):
            return i
    return -1

def make_range_combo(val):
    sr = ""
    for i in range(1326):
        if i != val:
            sr += "0 "
        else:
            sr += "1 "
    return sr

def get_range(pos):
    r = connection.command(line="show_range " + pos + " r:0:c")
    tab = []
    for n in r[0].split():
        tab.append(float(n))
    return tab

def get_eqs(pos):
    r = connection.command(line="calc_eq " + pos)
    tab = []
    for n in r[0].split():
        if n[0] == "0" or n[0] == "1" or 1:
            tab.append(float(n))
        else:
            tab.append(0.0)
    return tab

def set_ranges():
    for pos in ["IP","OOP"]:
        r = connection.command(line="show_range " + pos + " r:0:c")
        r = connection.command(line="set_range " + pos + " " + r[0])

def separate_ranges(hands, rng, eqs, nums, tranche):
    somr = sum(rng)
    rngs = []
    j = 0
    nexttab = [0.0] * 1326
    nexts = 0

    topr = 4

    for i in range(tranche):
        goal = somr / (tranche - topr)
        if i < (topr+1):
            goal /= (topr+1)
        s = nexts
        nexts = 0
        tab = nexttab
        nexttab = [0.0] * 1326
        while (s < goal and j < 1326 and rng[j] > 0.0 and math.isfinite(eqs[j])):
            s += rng[j]
            tab[nums[j]] = rng[j]
            if (s > goal):
                l = s - goal
                tab[nums[j]] -= l
                nexttab[nums[j]] = l
                nexts = l
            j += 1
        rngs.append(fts(tab))
    return rngs

def get_sep(rng, pos, tranche):
    eqs = get_eqs(pos)
    r = connection.command(line="show_hand_order")
    hands = r[0].split()
    nums = range(1326)
    combined = sorted(
        zip(eqs, rng, hands, nums),
        key=lambda x: x[0] if math.isfinite(x[0]) else -float('inf'),
        reverse=True
    )
    eqs, rip, hands, nums = zip(*combined)
    # for i in range(1326):
    #     print(hands[i], rip[i], eqip[i], nums[i])
    #     print(sum(rip[:i+1]))
    res = separate_ranges(hands, rip, eqs, nums, tranche)
    return res


def make_fight(sepip,sepoop,a,b):
    ip = sepip[a].split()
    oop = sepoop[b].split()
    r = connection.command(line="set_range IP " + sepip[a])
    r = connection.command(line="set_range OOP " + sepoop[b])
    r = connection.command(line="calc_eq IP")
    eqip = r[0].split()

    seq = 0
    sr = 0
    for i in range(1326):
        n = float(eqip[i])
        if math.isfinite(n):
            f = float(ip[i])
            seq += n * f
            sr += f
    res = seq / sr
    return res

def have_common_card(hand1, hand2):
    cards1 = {hand1[:2], hand1[2:]}
    cards2 = {hand2[:2], hand2[2:]}
    return not cards1.isdisjoint(cards2)


def get_blocking(combo,rng,hands):
    sp = 0
    sb = 0
    tab = rng.split()
    for i in range(1326):
        f = float(tab[i])
        if f > 0:
            sp += f
            if have_common_card(hands[i],combo):
                sb += f
    return sb / sp

def get_random_river(num):
    r = connection.command(line="show_children r:0:c:c")
    # print_lines(r)
    nbt = len(r) / 7
    t = random.randint(0,nbt-1)
    turn = r[t*7+1] + ":c:c"
    r = connection.command(line="show_children " + turn)
    nbt = len(r) / 7
    t = random.randint(0, nbt - 1)
    river = r[t * 7 + 1]
    # print(river)
    r = connection.command(line="calc_eq_node IP " + river)
    rng = r[0].split()
    # print(rng[num])
    return rng[num]


def get_random_hands(rng,n,vil,tranche,cbets,rip,roop):
    nums = []
    r = connection.command(line="show_hand_order")
    hands = r[0].split()

    while len(nums) < n:
        r = random.randint(0,1325)
        if (rng[r] > 0.1 and r not in nums):
            nums.append((r))

    tab = []
    for num in nums:
        tt = []
        tt.append(hands[num])
        ip = make_range_combo(num)
        for i in range(tranche):
            res = make_fight([ip],vil,0,i)
            tt.append(res)
            # print(hands[num],res)
            block = get_blocking(hands[num], vil[i], hands)
            tt.append(block)

        r = connection.command(line="set_range IP " + ip)

        for j in range(tranche):
            r = connection.command(line="set_range OOP " + vil[j])
            river = [0] * 10
            iter = 100
            i = -1
            while i < iter:
                res = float(get_random_river(num))
                if(math.isfinite(res)):
                    entier = int(res * 10)
                    if entier == 10:
                        entier = 9
                    river[entier] += 1/iter
                    i += 1
            tt += river

        tt.append(float(cbets[num]))

        tab.append(tt)
        print(tt)
        fr = [0] * 10


    return tab

def make_results(file, tranche):
    r = connection.command(line="load_tree Randoms/" + file)
    print_lines(r)
    print(file)

    r = connection.command(line="calc_ev IP r:0:c:b20")
    cbets = r[0].split()

    # r = connection.command(line="show_strategy r:0:c")
    # cbets = r[2].split()

    r = connection.command(line="calc_global_freq r:0:c:c")
    freq = 1 - float(r[0])

    board = file.split("_")[0]
    r = connection.command(line="set_board " + board)
    set_ranges()

    rip = get_range("IP")
    roop = get_range("OOP")

    r = connection.command(line="show_range OOP r:0:c")
    rop = r[0]

    sepip = get_sep(rip, "IP", tranche)
    sepoop = get_sep(roop, "OOP", tranche)

    tab = []
    for i in range(tranche):
        # print("------------IP", i * 10, "%------------")
        for j in range(tranche):
            res = make_fight(sepip, sepoop, i, j)
            # print("IP", i * 10, "% VS OOP", j * 10, "% :", res)
            tab.append(res)
    print("FREQ", freq)

    nbhands = 20

    hands = get_random_hands(rip,nbhands,sepoop,tranche,cbets,rip,rop)
    return tab,freq,hands


def build_dataset_from_folder(folder_path):
    tranche = 12
    X = []
    y = []
    names = []
    c = 0

    for filename in os.listdir(folder_path):
        try:
            file_path = os.path.join(folder_path, filename)
            if not os.path.isfile(file_path):
                continue  # Ignore les dossiers


            print(file_path, "(", c, "/ 94", ")")
            tab, freq, hands = make_results(filename, tranche)
            if len(tab) != tranche * tranche:
                continue

            for hand in hands:
                name = filename + " " + hand[0]
                input_vec = list(tab) + list(map(float, hand[1:-1]))
                target = float(hand[-1])

                X.append(input_vec)
                y.append(target)
                names.append(name)

            print("GOOD")
            c += 1
        except Exception as e:
            print("Erreur :", e)
            traceback.print_exc()  # Affiche la pile avec les lignes

    return np.array(X), np.array(y), np.array(names)




connection = Solver(solver="D:\Jesolver\jesolver_pro_avx2_1085.exe")
print("Solver connected successfully")

r = connection.command(line="set_isomorphism 0 0")


X, y, names = build_dataset_from_folder("D:\Jesolver\Randoms")
np.savez_compressed("dataset_cbet.npz", X=X, y=y, names=names)


