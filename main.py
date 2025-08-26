# coding: utf-8


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
    for col, row in enumerate(individual):
        row_count = sum(1 for pos in individual if pos == row) - 1
        total_count += row_count
        for comp_col, comp_row in enumerate(individual):
            if comp_col == col:
                continue
            if (col + row) == (comp_col + comp_row):
                total_count += 1
            if abs(col - row) == abs(comp_col - comp_row):
                total_count += 1
    return total_count


if __name__ == '__main__':

    # nqueen = NQueen(100, 10, .1, 'ranking', 4, [.8, .5, .5, .3, .2, .1, .1, .1, .05, .05])
    # nqueen.fit()
    print(count_duplicate([3, 0, 1, 2]))
    output_board([3, 0, 1, 2])

