# coding: utf-8


import os
import shutil
import random
from typing import List


from ga import GA


MAX_PATTERN = [1, None, None,
               2, 10, 4, 40, 92,
               352, 724, 2680,
               14200, 73712, 365596,
               2279184,
               14772512, 95815104,
               666909624, 4968057848,
               39029188884,
               314666222712,
               2691008701644,
               24233937684440,
               227514171973736]


class NQueen(GA):

    def __init__(self, gen: int, N: int, queen_num: int, mutation_props: float, select_func: str = 'roulette',
                 ranking_props: List[float] = [], cross_func: str = 'random', mutation_func: str = 'point', verbose: bool = False):
        super().__init__(gen, N, queen_num, mutation_props, select_func, ranking_props, cross_func, mutation_func)
        self.queen_num = queen_num
        self.evaluate_result = []
        self.fitting_results = []
        self.total_loop = 0
        self.output_individual_dir = 'output_individual'
        self.output_all_results = 'output_all_result.csv'
        self.verbose = verbose

    def init_individual(self) -> None:
        self.individual = [random.sample(
            range(self.queen_num), self.queen_num) for _ in range(self.N)]
        return None

    def __init_chrome(self) -> List[int]:
        return random.sample(range(self.queen_num), self.queen_num)

    def evaluate(self) -> None:
        self.evaluate_result = [self.evaluate_func(
            individual) for individual in self.individual]
        return None

    def evaluate_func(self, individual: List[int]) -> float:
        return 1 / (1 + self.__count_duplicate(individual))

    def __count_duplicate(self, individual: list[int]) -> int:
        total_count = 0
        for i, row in enumerate(individual):
            total_count += sum(1 for pos in individual if pos == row) - 1

            for j in range(i + 1, len(individual)):
                if i + row == j + individual[j]:
                    total_count += 1
                if i - row == j - individual[j]:
                    total_count += 1
        return total_count

    def fit(self) -> None:
        gen = 0
        self.__init_output_individual()
        self.init_individual()
        self.evaluate()
        if self.verbose:
            print('====== init individual ======')
            self.__print_individual_evaluate()
        while gen < self.gen:
            result_num = len(self.fitting_results)
            if result_num == MAX_PATTERN[self.queen_num - 1]:
                break
            self.step()
            if self.verbose:
                self.__print_individual_evaluate()
            if 1. in self.evaluate_result:
                for i, evaluate in enumerate(self.evaluate_result):
                    if self.individual[i] in self.fitting_results:
                        self.individual[i] = self.__init_chrome()
                        continue
                    if evaluate == 1.:
                        self.fitting_results.append(self.individual[i])
                        self.individual[i] = self.__init_chrome()
            print(f'====== {gen + 1} step, result: {result_num} =======\r', end='')
            gen += 1
        self.total_loop = gen
        self.fitting_results = tuple(set([tuple(result) for result in self.fitting_results]))
        return None

    def __print_individual_evaluate(self) -> None:
        for i, (individual, evaluate) in enumerate(zip(self.individual, self.evaluate_result)):
            print(f'{i}: {individual}, {evaluate}')
        return None

    def __print_init_individual(self) -> None:
        for i, individual in enumerate(self.individual):
            print(f'{i}: {individual}')
        return None

    def __init_output_individual(self) -> None:
        if os.path.exists(self.output_individual_dir):
            shutil.rmtree(self.output_individual_dir)
        os.makedirs(self.output_individual_dir)
        return None

    def output_individual_to_csv(self, step: int) -> None:
        with open(os.path.join(self.output_individual_dir, f'{step}.csv'), 'w') as f:
            for individual in self.individual:
                f.write(f"{','.join(list(map(str, individual)))}\n")
        return None

    def output_all_result_to_csv(self) -> None:
        with open(self.output_all_results, 'w') as f:
            for result in self.fitting_results:
                f.write(f"{','.join(tuple(map(str, result)))}\n")

    def output_board(self) -> None:
        # queen_num = len(board_array)
        # board = [list('.' * queen_num) for _ in range(queen_num)]
        # for i in range(len(board_array)):
        #     board[board_array[i]][i] = 'O'
        # for line in board:
        #     print(' '.join(line))
        # return None
        pass
