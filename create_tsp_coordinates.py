# coding: utf-8

import csv
import numpy as np
from sklearn.manifold import MDS
import argparse


def load_cost_matrix(input_file: str) -> np.ndarray:
    """
    CSVファイルからコスト行列を読み込む

    Args:
        input_file: 入力CSVファイル名

    Returns:
        コスト行列（numpy配列）
    """
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        cost_matrix = []
        for row in reader:
            cost_matrix.append([int(val) for val in row])

    return np.array(cost_matrix)


def estimate_coordinates(cost_matrix: np.ndarray, invalid_cost: int = 1000000) -> np.ndarray:
    """
    コスト行列から2次元座標を推定する（多次元尺度構成法を使用）

    Args:
        cost_matrix: コスト行列
        invalid_cost: 無効なエッジのコスト値

    Returns:
        2次元座標の配列（shape: (n_points, 2)）
    """
    # 無効なコストを持つエッジを最大の有効コストの10倍に置き換え
    # （MDSは距離行列として扱うため、極端に大きい値は避ける）
    distance_matrix = cost_matrix.copy().astype(float)
    valid_costs = distance_matrix[distance_matrix < invalid_cost]
    max_valid_cost = valid_costs.max() if len(valid_costs) > 0 else 100

    distance_matrix[distance_matrix >= invalid_cost] = max_valid_cost * 10

    # 対称行列にする（往路と復路の平均を取る）
    distance_matrix = (distance_matrix + distance_matrix.T) / 2

    # MDSで2次元座標に変換
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42, max_iter=1000)
    coordinates = mds.fit_transform(distance_matrix)

    return coordinates


def save_coordinates(coordinates: np.ndarray, output_file: str):
    """
    座標をCSVファイルに保存する

    Args:
        coordinates: 2次元座標の配列
        output_file: 出力CSVファイル名
    """
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['point_id', 'x', 'y'])  # ヘッダー
        for i, (x, y) in enumerate(coordinates):
            writer.writerow([i, f'{x:.6f}', f'{y:.6f}'])

    print(f'座標データを {output_file} に出力しました')
    print(f'地点数: {len(coordinates)}')


def main():
    parser = argparse.ArgumentParser(
        description='TSPコスト行列から各地点の2次元座標を推定する（MDS使用）'
    )
    parser.add_argument('-i', '--input', type=str, default='input_tsp_cost.csv',
                        help='入力CSVファイル名（デフォルト: input_tsp_cost.csv）')
    parser.add_argument('-o', '--output', type=str, default='tsp_coordinates.csv',
                        help='出力CSVファイル名（デフォルト: tsp_coordinates.csv）')
    parser.add_argument('-c', '--invalid-cost', type=int, default=1000000,
                        help='無効なエッジのコスト値（デフォルト: 1000000）')

    args = parser.parse_args()

    # コスト行列の読み込み
    print(f'コスト行列を {args.input} から読み込んでいます...')
    cost_matrix = load_cost_matrix(args.input)
    print(f'読み込み完了: {cost_matrix.shape[0]} x {cost_matrix.shape[1]}')

    # 座標の推定
    print('多次元尺度構成法(MDS)で座標を推定しています...')
    coordinates = estimate_coordinates(cost_matrix, args.invalid_cost)

    # 座標の保存
    save_coordinates(coordinates, args.output)


if __name__ == '__main__':
    main()
