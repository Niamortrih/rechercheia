import subprocess
import os
import pathlib
import traceback
from Spot import Spot
from Hand import Hand
import random
import numpy as np
from functions import *

def print_lines(lines):
    for line in lines:
        print(line)

class Parser(object):
    def __init__(self, connection, config):
        self.config = config
        r = connection.command(line="set_isomorphism 1 0")
        self.connection = connection
        self.folder = config["folder"]
        self.spot_data = []
        self.hand_data = []
        self.hand_by_spot = 50
        r = connection.command(line="show_hand_order")
        self.list_hands = r[0].split()
        self.inter = get_intersection_matrix(self.list_hands)
        self.X = []
        self.y = []
        self.names = []
        self.aff = True
        self.feature = 0

    import os
    import random
    import traceback

    def make(self):
        counter = 1
        file_paths = []

        # Collecte tous les chemins de fichiers récursivement
        for dirpath, _, filenames in os.walk(self.folder):
            for filename in filenames:
                file_paths.append(os.path.join(dirpath, filename))

        random.shuffle(file_paths)

        for file_path in file_paths:
            if counter < 40000001:
                try:
                    filename = os.path.basename(file_path)
                    print("----- SPOT", counter, ":", filename, "-----")
                    spot = Spot(file_path, self)  # on passe bien le chemin complet ici
                    results_spot = spot.make()
                    hs = self.generate_all_hands(spot.taboop)
                    # print("LEN HANDS", len(hs))
                    for h in hs:
                        hand = Hand(self, spot, h)
                        results_hand = hand.make()
                        for i in range(len(spot.targets)):
                            option = spot.bets[i]
                            target = hand.targets[i]
                            inputs = list(results_spot) + list(results_hand) + [option]
                            name = filename + " " + hand.hand_name + " " + str(option)
                            self.aff = False
                            self.X.append(inputs)
                            self.y.append(target)
                            self.names.append(name)

                    counter += 1
                    if counter % int(self.config["saves"]) == 0:
                        self.save_temp(counter)

                except Exception as e:
                    print("Erreur :", e)
                    traceback.print_exc()

    def save(self):
        X = np.array(self.X)
        y = np.array(self.y)
        names = np.array(self.names)
        np.savez_compressed("dataset1.npz", X=X, y=y, names=names)

    def save_temp(self, n):
        X = np.array(self.X)
        y = np.array(self.y)
        names = np.array(self.names)
        name = "dataset_tmp_" + str(n) + ".npz"
        np.savez_compressed(name, X=X, y=y, names=names)

    def add_spot_data(self, instruction, params):
        self.spot_data.append((instruction, params))

    def add_hand_data(self, instruction, params):
        self.hand_data.append((instruction, params))

    def generate_hands(self, rng):
        nums = []
        r = self.connection.command(line="show_hand_order")
        hands = r[0].split()
        while len(nums) < self.hand_by_spot:
            r = random.randint(0, 1325)
            if (rng[r] > 0.15 and r not in nums):
                nums.append((r))
        return nums

    def generate_all_hands(self, rng):
        nums = []
        for i in range(1326):
            if rng[i] > 0.05:
                # print(i)
                nums.append(i)
        return nums