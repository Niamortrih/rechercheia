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
        r = self.connection.command(line="load_tree " + self.filename)
        board = os.path.basename(self.filename).split("_")[0]
        r = self.connection.command(line="set_board " + board)
        r = self.connection.command(line="show_effective_stack")
        self.effstack = float(r[0])
        r = self.connection.command(line="show_tree_params")
        self.pot = float(r[1].split()[-1])
        print(self.pot)
        self.make_spr()
        set_ranges(self.connection)
        self.targets = self.get_targets()
        self.strip = get_range(self.connection, "IP")
        self.tabip = str_to_tab(self.strip)
        self.stroop = get_range(self.connection, "OOP")
        self.taboop = str_to_tab(self.stroop)
        self.rivers = get_rivers(self.connection, self.strip, self.stroop, self.nbriver, self.parser.list_hands)
        self.eqip = get_calc_eq(self.connection, "IP")
        self.eqoop = get_calc_eq(self.connection, "OOP")
        self.eqs = get_eqs(self.connection, self.tabip, self.strip, self.taboop, self.parser.list_hands)
        self.ponderip,self.ponderoop = get_ponder(self.eqs,self.eqoop,self.tabip,self.taboop,self.parser.inter)
        self.make_range_vs_range(4)
        self.sepip = split_range(self.tabip, self.ponderip, self.nsep)
        self.sepoop = split_range(self.taboop, self.ponderoop, self.nsep)
        print("SPOT", self.data)
        return self.data

    def get_targets(self):
        r = self.connection.command(line="calc_ev OOP r:0:b20")
        return str_to_tab(r[0])

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







