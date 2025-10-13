# coding: utf-8


import csv
import time
import random
import os
from typing import List
import multiprocessing
from nqueen import NQueen
from knapsack import Knapsack
from onemax import OneMax
from tsp import TSP
from utils import load_ranking_props, load_tsp_cost, load_tsp_coordinates


def calc_fit(use_parallel: bool = False, coordinate_file: str = None, show_route_interval: int = None, enable_gui: bool = False):
    """
    TSP問題を遺伝的アルゴリズムで解く

    Args:
        use_parallel: 並列処理を使用するか
        coordinate_file: 座標ファイルのパス（Noneの場合は座標を使用しない）
        show_route_interval: 経路を表示するステップ間隔（Noneの場合は表示しない）
        enable_gui: GUIでリアルタイム表示するか
    """
    ranking_props = load_ranking_props('ranking_rate.csv')
    tsp_cost = load_tsp_cost('input_tsp_cost.csv')

    # 座標ファイルが指定されていて存在する場合は読み込む
    coordinates = None
    if coordinate_file is not None and os.path.exists(coordinate_file):
        coordinates = load_tsp_coordinates(coordinate_file)
        print(f'座標データを {coordinate_file} から読み込みました（{len(coordinates)}地点）')
    elif coordinate_file is not None:
        print(f'警告: 座標ファイル {coordinate_file} が見つかりません。座標なしで実行します。')

    tsp = TSP(1000, 200, len(tsp_cost[0]), tsp_cost, .1, 'ranking', ranking_props, 'order', 'point',
              use_parallel=use_parallel, n_workers=multiprocessing.cpu_count(),
              coordinates=coordinates, show_route_interval=show_route_interval)
    start_time = time.time()
    tsp.fit()
    end_time = time.time()
    tsp.output_result_individual_to_csv()

    # GIFアニメーションを作成
    if coordinates is not None and show_route_interval is not None:
        tsp.create_gif(output_filename='tsp_route_evolution.gif', duration=500)

    print()
    print(f'処理時間: {end_time - start_time: .4f}秒')


if __name__ == '__main__':

    print('=' * 5 + '逐次処理' + '=' * 5)
    # 座標ファイルを指定して実行
    # 座標ファイルが存在しない場合は、先に create_tsp_coordinates.py を実行してください
    # enable_gui=True: GUIでリアルタイム表示（毎ステップ更新）
    # show_route_interval=5: 5ステップごとに画像を保存
    calc_fit(use_parallel=False, coordinate_file='tsp_coordinates.csv', show_route_interval=5)
    print('=' * 5 + '逐次処理' + '=' * 5)
    # print('=' * 5 + '並列処理' + '=' * 5)
    # calc_fit(use_parallel=True, coordinate_file='tsp_coordinates.csv', show_route_interval=5, enable_gui=True)
    # print('=' * 5 + '並列処理' + '=' * 5)
