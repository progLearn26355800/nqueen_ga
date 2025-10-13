# coding: utf-8


import csv
import random
import argparse


def create_tsp_cost_matrix(n: int, max_invalid_edges: int = None, output_file: str = 'input_tsp_cost.csv'):
    """
    TSP問題のコストマトリックスを生成してCSVファイルに出力する

    Args:
        n: 地点数（N x N の行列を作成）
        max_invalid_edges: 10000を設定する要素の数（Noneの場合は総要素数の5%）
        output_file: 出力CSVファイル名
    """
    # N x N の2次元リストを作成
    cost_matrix = []
    max_cost = 100

    for i in range(n):
        row = []
        for j in range(n):
            if i == j:
                # 対角線上の要素（自分自身への距離）は0に設定
                row.append(0)
            else:
                # 1以上1000以下のランダムな整数
                row.append(random.randint(1, max_cost))
        cost_matrix.append(row)

    # ランダムに要素を10000に設定（対角線以外）
    if max_invalid_edges is None:
        # デフォルト: 総要素数の5%程度を無効化
        max_invalid_edges = max(1, int(n * n * 0.05))

    invalid_count = 0
    while invalid_count < max_invalid_edges:
        i = random.randint(0, n - 1)
        j = random.randint(0, n - 1)

        # 対角線上でなく、まだ10000でない要素を選択
        if i != j and cost_matrix[i][j] != max_cost * 10000:
            cost_matrix[i][j] = max_cost * 10000
            invalid_count += 1

    # CSVファイルに出力
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        for row in cost_matrix:
            writer.writerow(row)

    print(f'TSPコストマトリックス ({n} x {n}) を {output_file} に出力しました')
    print(f'無効なエッジ（コスト=10000）の数: {invalid_count}個')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TSP問題のコストデータを生成')
    parser.add_argument('-n', '--size', type=int, default=10, help='地点数（デフォルト: 10）')
    parser.add_argument('-e', '--invalid-edges', type=int, default=None,
                        help='10000を設定する要素の数（デフォルト: 総要素数の5%%）')
    parser.add_argument('-o', '--output', type=str, default='input_tsp_cost.csv',
                        help='出力ファイル名（デフォルト: input_tsp_cost.csv）')
    parser.add_argument('-s', '--seed', type=int, default=None,
                        help='乱数シード（デフォルト: なし）')

    args = parser.parse_args()

    # 乱数シードの設定
    if args.seed is not None:
        random.seed(args.seed)

    create_tsp_cost_matrix(args.size, args.invalid_edges, args.output)
