import os
from Solver import Solver
import math
import numpy as np
import random



def print_lines(lines):
    for line in lines:
        print(line)

def make_random_range():
    rng = ""
    for i in range(1326):
        r = random.randint(1,6)
        if (r == 1):
            val = str(random.uniform(0.1,1))
            rng += val
        else:
            rng += "0"
        rng += " "
    return rng

def generate_board():
    ranks = '23456789TJQKA'
    suits = 'shdc'  # ordre souhaité
    deck = [r + s for r in ranks for s in suits]
    while True:
        flop = random.sample(deck, 3)
        values = [card[0] for card in flop]
        if len(set(values)) < 3:
            flop.sort(key=lambda c: (ranks.index(c[0]), -suits.index(c[1])), reverse=True)
        else:
            flop.sort(key=lambda c: ranks.index(c[0]), reverse=True)
        return ''.join(flop)


for i in range(100000):

    connection = Solver(solver="D:\Jesolver\jesolver_pro_avx2_1085.exe")
    print("------------------------Solver connected successfully----------------------------------------")

    r = connection.command(line="load_tree Boards/5s3h3d.cfr")
    print_lines(r)

    r = connection.command(line="set_isomorphism 0 0")
    print_lines(r)

    r = connection.command(line="repeat 3 bonjour")
    print_lines(r)

    r = connection.command(line="set_accuracy 0.05")  # 0.5% du pot
    print_lines(r)

    board = generate_board()
    r = connection.command(line="set_board " + board)
    print_lines(r)

    rng = make_random_range()
    r = connection.command(line="set_range IP " + rng)
    print_lines(r)

    rng = make_random_range()
    r = connection.command(line="set_range OOP " + rng)
    print_lines(r)

    deep = str(random.randint(5,5) * 20)
    r = connection.command(line="set_eff_stack " + deep)
    print_lines(r)

    r = connection.command(line="set_pot 0 0 40")
    print_lines(r)

    r = connection.command(line="build_tree")
    print_lines(r)

    r = connection.command(line="go 300 seconds block")
    print_lines(r)

    r = connection.command(line="wait_for_solver")
    print_lines(r)

    print("DUMPING")
    name = "Randoms/" + board + "_" + "6" + ".cfr"
    r = connection.command(line="dump_tree " + name + " no_rivers")
    print_lines(r)

    r = connection.command(line="free_tree")
    print_lines(r)