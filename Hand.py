import subprocess
import os
import pathlib
import random
import math
import numpy as np
from scipy.stats import skew, kurtosis
from functions import *

def print_lines(lines):
    for line in lines:
        print(line)

class Hand(object):
    def __init__(self, parser, spot, num):
        self.parser = parser
        self.spot = spot
        self.data = []
        self.num = num
        self.hand_name = self.parser.list_hands[num]
        self.make_targets()
        self.connection = parser.connection
        self.strrng = hand_range(num)
        self.tabrng = str_to_tab(self.strrng)


    def make(self):
        self.make_vs_ranges()
        self.make_rivers()
        return self.data

    def make_vs_ranges(self):
        for i in range(self.spot.nsep):
            res = hand_vs_range(self.spot.eqs.T, self.num, self.spot.sepip[i], self.parser.inter.T)
            self.data.append(res)
            block = blocker(self.num,self.spot.sepip[i],self.parser.inter.T)
            self.data.append(block)
            # print(i, res)

    def make_rivers(self):
        rivers = self.spot.rivers[:, self.num]
        self.data.append(np.nanmean(rivers))
        self.data.append(np.nanstd(rivers))
        for i in range(5,100,5):
            self.data.append(np.nanpercentile(rivers, i))
        self.data.append(skew(rivers, nan_policy='omit'))
        self.data.append(kurtosis(rivers, nan_policy='omit'))

    def make_targets(self):
        self.targets = []
        for tab in self.spot.targets:
            self.targets.append(tab[self.num])