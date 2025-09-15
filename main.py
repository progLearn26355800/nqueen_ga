# coding: utf-8


import csv
import random
from typing import List
from nqueen import NQueen


def output_board(board_array: List[int]) -> None:
    queen_num = len(board_array)
    board = [list('.' * queen_num) for _ in range(queen_num)]
    for i in range(len(board_array)):
        board[board_array[i]][i] = 'O'
    for line in board:
        print(' '.join(line))
    return None


def count_duplicate(individual: List[int]) -> int:
    total_count = 0
    for i, row in enumerate(individual):
        total_count += sum(1 for pos in individual if pos == row) - 1
        print(total_count)

        for j in range(i + 1, len(individual)):
            print(f'{i=}, {row=}, {j=}')
            if (i + row) == (j + individual[j]):
                total_count += 1
                print(f'plus dup: {total_count=}')
            if i - row == j - individual[j]:
                total_count += 1
                print(f'minus dup: {total_count=}')
            print(total_count)
    return total_count


def order_crossover(parent1, parent2):
    n = len(parent1)
    # ランダムに2点を選択
    point1, point2 = sorted(random.sample(range(n), 2))

    # 子個体の初期化
    child = [-1] * n

    # 親1から部分配列をコピー
    child[point1:point2] = parent1[point1:point2]

    # 親2から残りの要素を順番に埋める
    pointer = point2
    pointer
    for value in parent2[point2:] + parent2[:point2]:
        if value not in child:
            child[pointer % n] = value
            pointer += 1

    return child


def load_ranking_rate(input_file: str) -> List[float]:
    ranking_props = []
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            rate = float(row[0])
            num = int(row[1])
            ranking_props += [rate] * num
    return ranking_props


if __name__ == '__main__':

    ranking_props = load_ranking_rate('ranking_rate.csv')
    nqueen = NQueen(10000, 100, 9, .2, 'ranking', ranking_props, 'order', 'point')
    nqueen.fit()
    nqueen.output_all_result_to_csv()
    # parent1 = [0, 1, 2, 3, 4, 5, 6, 7]
    # parent2 = [1, 3, 7, 2, 5, 6, 0, 4]
    # print(order_crossover(parent1, parent2))
    # print(order_crossover(parent2, parent1))
