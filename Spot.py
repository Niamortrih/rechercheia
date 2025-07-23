import subprocess
import os
import pathlib
import math
from functions import *
import time



def fts(lst):
    return ' '.join(str(x) for x in lst)

class Spot(object):
    def __init__(self, filename, parser):
        self.filename = filename
        self.parser = parser
        self.connection = parser.connection
        self.data = []
        self.nsep = 12
        self.nbriver = 300

    def make(self):
        print(self.filename)
        r = self.connection.command(line='load_tree "' + self.filename + '"')
        board = os.path.basename(self.filename).split(self.parser.config["separator"])[0]
        r = self.connection.command(line="set_board " + board)
        r = self.connection.command(line="show_effective_stack")
        self.effstack = float(r[0])
        r = self.connection.command(line="show_tree_params")
        self.pot = float(r[1].split()[-1])
        self.make_spr()
        set_ranges(self.connection)
        self.make_targets()
        self.strip = get_range(self.connection, "IP")
        self.tabip = str_to_tab(self.strip)
        self.stroop = get_range(self.connection, "OOP")
        self.taboop = str_to_tab(self.stroop)
        self.rivers = get_rivers(self.connection, self.strip, self.stroop, self.nbriver, self.parser.list_hands)
        self.eqip = get_calc_eq(self.connection, "IP")
        self.eqoop = get_calc_eq(self.connection, "OOP")
        self.eqs = get_eqs(self.connection, self.tabip, self.strip, self.taboop, self.parser.list_hands)
        self.ponderip,self.ponderoop = get_ponder(self.eqs,self.eqoop,self.tabip,self.taboop,self.parser.inter)
        self.make_range_vs_range(5)
        self.sepip = split_range(self.tabip, self.ponderip, self.nsep)
        self.sepoop = split_range(self.taboop, self.ponderoop, self.nsep)
        print("SPOT", self.data)
        return self.data

    def make_targets(self):
        self.targets = []
        self.bets = []
        r = self.connection.command(line="show_children r:0")
        nbc = int(len(r) / 7)
        for i in range(nbc):
            child = r[i * 7 + 1]
            res = self.connection.command(line="calc_ev OOP " + child)
            # print(child)
            # print(str_to_tab(res[0]))
            self.targets.append(str_to_tab(res[0]))
            bet = child.split(":")[-1]
            val = 0
            if bet[0] == "b":
                val = round(float(bet[1:]) / self.pot,3)
            self.bets.append(val)


    def make_range_vs_range(self, n):
        sepip = split_range(self.tabip, self.ponderip, n)
        sepoop = split_range(self.taboop, self.ponderoop, n)
        for i in range(n):
            for j in range(n):
                res = range_vs(self.eqs, sepip[i], sepoop[j], self.parser.inter)
                self.data.append(res)
                # print(i, "VS", j, ":", res)

    def make_spr(self):
        spr = self.effstack / self.pot
        self.data.append(spr)
        minbet = 20 / self.pot
        self.data.append(minbet)







