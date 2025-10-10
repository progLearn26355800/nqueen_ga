# coding: utf-8


import csv
import random
from typing import List
from nqueen import NQueen
from knapsack import Knapsack
from onemax import OneMax


def load_ranking_props(input_file: str) -> List[float]:
    ranking_props = []
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            props = float(row[0])
            num = int(row[1])
            ranking_props += [props] * num
    return ranking_props


if __name__ == '__main__':

    ranking_props = load_ranking_props('ranking_rate.csv')
    # knapsack_weight = 65
    # obj_weight = [10, 12, 7, 9, 21, 16]
    # obj_price = [120, 130, 80, 100, 250, 185]
    nqueen = NQueen(10000, 200, 8, .25, 'ranking', ranking_props, 'order', 'shuffle')
    nqueen.fit()
    nqueen.output_all_result_to_csv()
    # one_max = OneMax(25, 20, 10, .4, 'roulette', ranking_props, 'random', 'random_bit')
    # one_max.fit()
