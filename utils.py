# coding: UTF-8


import csv
from typing import List


def load_ranking_props(input_file: str) -> List[float]:
    ranking_props = []
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            props = float(row[0])
            num = int(row[1])
            ranking_props += [props] * num
    return ranking_props


def load_tsp_cost(input_file: str) -> List[float]:
    tsp_cost = []
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        tsp_cost = tuple([tuple([int(cost) for cost in row]) for row in reader])
    return tsp_cost
