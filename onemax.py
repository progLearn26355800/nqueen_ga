# coding: utf-8


import os
import shutil
import random
from typing import List


from ga import GA


def _evaluate_one_max(individual: List[int]):
    total = sum(individual)
    return total / len(individual)


class OneMax(GA):
    def __init__(self, gen: int, N: int, N_length: int,
                 mutation_props: float, select_func: str = 'roulette',
                 ranking_props: List[float] = [], cross_func: str = 'random', mutation_func: str = 'point',
                 use_parallel: bool = False, n_workers: int = None):
        super().__init__(gen, N, N_length, mutation_props, select_func, ranking_props, cross_func, mutation_func, use_parallel, n_workers)
        self.N_length = N_length
        self.fitting_results = []
        self.output_csv_dir = 'output_result_csv'

    def init_individual(self) -> None:
        self.individual = [random.choices(range(2), k=self.N_length) for _ in range(self.N)]
        return None

    def evaluate_func(self, individual: List[int]) -> float:
        return _evaluate_one_max(individual)

    def _get_evaluate_wrapper(self):
        return _evaluate_one_max

    def fit(self) -> None:
        gen = 0
        self.__init_output_result_csv()
        self.init_individual()
        self.evaluate()
        while gen < self.gen:
            self.step()
            print(f'====== {gen + 1} step =======\r', end='')
            self.__output_result_step_csv(gen)
            if 1. in self.evaluate_result:
                break
            gen += 1
        self.total_loop = gen
        return None

    def __print_individual_evaluate(self) -> None:
        for i, (individual, evaluate) in enumerate(zip(self.individual, self.evaluate_result)):
            print(f'{i}: {individual}, {evaluate}')
        return None

    def __init_output_result_csv(self) -> None:
        if os.path.exists(self.output_csv_dir):
            shutil.rmtree(self.output_csv_dir)
        os.makedirs(self.output_csv_dir)
        return None

    def __output_result_step_csv(self, step: int) -> None:
        with open(os.path.join(self.output_csv_dir, f'{step}.csv'), 'w') as f:
            for i, (individual, evaluate) in enumerate(zip(self.individual, self.evaluate_result)):
                f.write(f'{','.join(list(map(str, individual)))},{evaluate}\n')
