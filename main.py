# coding: utf-8


import csv
import time
import random
from typing import List
import multiprocessing
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


def calc_fit(use_parallel: bool=False):
    ranking_props = load_ranking_props('ranking_rate.csv')
    # knapsack_weight = 65
    # obj_weight = [10, 12, 7, 9, 21, 16]
    # obj_price = [120, 130, 80, 100, 250, 185]
    # nqueen = NQueen(10000, 500, 10, .25, 'ranking', ranking_props, 'order', 'shuffle', use_parallel=use_parallel, n_workers=multiprocessing.cpu_count() // 2)
    nqueen = NQueen(10000, 1000, 10, .1, 'roulette', ranking_props, 'order', 'shuffle', use_parallel=use_parallel, n_workers=multiprocessing.cpu_count())
    start_time = time.time()
    nqueen.fit()
    end_time = time.time()
    nqueen.output_all_result_to_csv()
    print()
    print(f'処理時間: {end_time - start_time:.4f}秒')


if __name__ == '__main__':

    print('=' * 5 + '逐次処理' + '=' * 5)
    calc_fit(use_parallel=False)
    print('=' * 5 + '逐次処理' + '=' * 5)
    print('=' * 5 + '並列処理' + '=' * 5)
    calc_fit(use_parallel=True)
    print('=' * 5 + '並列処理' + '=' * 5)
