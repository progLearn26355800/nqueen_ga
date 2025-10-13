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


def load_tsp_coordinates(input_file: str) -> List[tuple]:
    """
    TSP問題の座標データをCSVファイルから読み込む

    Args:
        input_file: 座標データのCSVファイルパス（ヘッダー付き）

    Returns:
        座標データのリスト [(x1, y1), (x2, y2), ...]
    """
    coordinates = []
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # ヘッダーをスキップ
        for row in reader:
            # point_id, x, y の形式を想定
            x, y = float(row[1]), float(row[2])
            coordinates.append((x, y))
    return coordinates
