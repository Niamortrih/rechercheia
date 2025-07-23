import math
import numpy as np
import random


def print_lines(lines):
    for line in lines:
        print(line)

def get_intersection_matrix(hands):
    n = len(hands)
    matrix = np.ones((n, n), dtype=np.bool_)

    # Pré-extraire les cartes de chaque main
    cards = [set([hand[:2], hand[2:]]) for hand in hands]

    for i in range(n):
        for j in range(i + 1, n):
            if cards[i] & cards[j]:  # intersection non vide → cartes en commun
                matrix[i, j] = 0
                matrix[j, i] = 0  # symétrie

    return matrix

def card_in_hand(card, hand):
    return card == hand[:2] or card == hand[2:]

def set_ranges(connection):
    for pos in ["IP","OOP"]:
        r = connection.command(line="show_range " + pos + " r:0")
        r = connection.command(line="set_range " + pos + " " + r[0])

def set_range(connection, pos, str):
    r = connection.command(line="set_range " + pos + " " + str)

def get_range(connection, pos):
    r = connection.command(line="show_range " + pos + " r:0")
    return r[0]

def str_to_tab(s):
    arr = np.fromstring(s, sep=' ', dtype=np.float32)
    arr[~np.isfinite(arr)] = 0.0
    return arr

def str_to_tab_nan(s):
    return np.fromstring(s, sep=' ', dtype=np.float32)

def get_calc_eq(connection, pos):
    r = connection.command(line="calc_eq " + pos)
    return str_to_tab(r[0])

def get_eqs(connection, tabp, strip, taboop, hands):
    oop = bytearray(b'0 ' * 1325 + b'0')
    last = 0
    bigtab = np.zeros((1326, 1326), dtype=np.float32)

    set_range(connection, "IP", strip)

    for i in range(1326):
        if taboop[i] > 0:
            oop[last * 2] = ord('0')
            oop[i * 2] = ord('1')
            last = i
            set_range(connection, "OOP", oop.decode())
            bigtab[i] = get_calc_eq(connection, "IP")
            # print(i, hands[i])
            # for j in range(22):
            #     print(hands[j], bigtab[i][j])
            # print("---")
    return bigtab.T

def get_eqs_ponder(eqs, eqr, tabr, inter):
    total_weights = eqr * tabr  # pondération finale des mains de B
    masked_weights = total_weights * inter  # matrice pondérée selon compatibilité

    numerators = np.sum(eqs * masked_weights, axis=1)
    denominators = np.sum(masked_weights, axis=1)

    with np.errstate(divide='ignore', invalid='ignore'):
        result = np.divide(numerators, denominators, out=np.zeros_like(numerators), where=denominators != 0)

    return result

def get_ponder(eqs,eqoop,tabip,taboop,inter):
    eqip1 = get_eqs_ponder(eqs, eqoop, taboop, inter)
    eqoop1 = get_eqs_ponder(1 - eqs.T, eqip1, tabip, inter)
    eqip2 = get_eqs_ponder(eqs, eqoop1, taboop, inter)
    eqoop2 = get_eqs_ponder(1 - eqs.T, eqip2, tabip, inter)
    eqip3 = get_eqs_ponder(eqs, eqoop2, taboop, inter)
    eqoop3 = get_eqs_ponder(1 - eqs.T, eqip3, tabip, inter)
    return eqip3,eqoop3

import numpy as np

def split_range(tabip, ponderip, n):
    tabip = np.asarray(tabip, dtype=np.float32)
    ponderip = np.asarray(ponderip, dtype=np.float32)

    sorted_indices = np.argsort(-ponderip)  # Tri décroissant
    total_weight = np.sum(tabip)
    chunk_size = total_weight / n

    result = np.zeros((n, 1326), dtype=np.float32)
    current_chunk = 0
    accumulated = 0.0

    for idx in sorted_indices:
        weight = tabip[idx]
        while weight > 0 and current_chunk < n:
            remaining = chunk_size - accumulated
            to_take = min(weight, remaining)
            result[current_chunk, idx] += to_take
            accumulated += to_take
            weight -= to_take
            if np.isclose(accumulated, chunk_size) or accumulated > chunk_size:
                current_chunk += 1
                accumulated = 0.0

    return result

def print_range_chunks(result, list_hand, seuil=0.001):
    """
    Affiche les mains présentes dans chaque tranche (> seuil).

    :param result: np.array de shape (n, 1326), résultat du découpage
    :param list_hand: liste de 1326 strings représentant les mains (ex: 'AsKs')
    :param seuil: seuil de présence pour afficher une main (ex: 0.001)
    :return: liste des tranches, chacune contenant les mains sélectionnées
    """
    n = result.shape[0]
    tranches = []
    for i in range(n):
        mains = [list_hand[j] for j in range(1326) if result[i, j] > seuil]
        print(f"Tranche {i+1} ({len(mains)} mains) : {' '.join(mains)}")
        tranches.append(mains)
    return tranches

def range_vs(eqs, rip, roop, inter):
    weights = np.outer(rip, roop) * inter
    numerator = np.sum(eqs * weights)
    denominator = np.sum(weights)
    if denominator == 0:
        return 0.0
    return numerator / denominator

def hand_range(n):
    return '0 ' * n + '1' + ' 0' * (1325 - n)

def hand_vs_range(eqs, hand_id, range_weights, inter):
    mask = inter[hand_id]  # vecteur booléen (1326,) → mains compatibles avec hand_id
    eq_line = eqs[hand_id]
    masked_weights = range_weights * mask  # pondération uniquement des mains compatibles

    numerator = np.sum(eq_line * masked_weights)
    denominator = np.sum(masked_weights)

    if denominator == 0:
        return 0.0
    return 1 - numerator / denominator

def get_random_river(connection):
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
    # r = connection.command(line="calc_eq_node IP " + river)
    # rng = r[0].split()
    # # print(rng[num])
    return river

def get_rivers(connection, strip, stroop, n, list_hand):
    tab = []
    for i in range(n):
        river = get_random_river(connection)
        r = connection.command(line="calc_eq_node OOP " + river)
        rng = str_to_tab_nan(r[0])  # doit retourner un array (1326,)
        tab.append(rng)  # on accumule les lignes

    return np.array(tab, dtype=np.float32)  # shape (n, 1326)

def blocker(hand_id, range_weights, inter):
    mask = inter[hand_id]  # mains compatibles avec la main hand_id
    total_weight = np.sum(range_weights)
    compatible_weight = np.sum(range_weights * mask)

    if total_weight == 0:
        return 0.0
    return  1 - compatible_weight / total_weight
