# coding: utf-8


import random
from typing import List, Tuple


class NQueen:

    def __init__(self, gen: int, N: int, mutation_props: float, select: str, queen_num: int,
                 ranking_props: List[float] = []):
        self.gen = gen
        self.N = N
        self.mutation_props = mutation_props
        select_func_dict = {
            'roulette': self.roulette,
            'ranking': self.ranking
        }
        self.select_func = select_func_dict[select]
        self.queen_num = queen_num
        self.evaluate_result = []
        self.fitting_results = []
        self.total_loop = 0
        self.ranking_props = ranking_props

    def __init_individual(self) -> None:
        self.individual = [random.sample(
            range(self.queen_num), self.queen_num) for _ in range(self.N)]
        return None

    def evaluate(self) -> None:
        self.evaluate_result = [self.__evaluate_func(
            individual) for individual in self.individual]
        return None

    def __evaluate_func(self, individual: List[int]) -> float:
        return 1 / (1 + self.__count_duplicate(individual))

    def __count_duplicate(self, individual: list[int]) -> int:
        total_count = 0
        for i, row in enumerate(individual):
            row_count = sum(1 for pos in individual if pos == row) - 1
            total_count += row_count
            for j in range(i + 1, len(individual)):
                if (i + row) == (j + individual[j]):
                    total_count += 1
                if abs(i - row) == abs(j - individual[j]):
                    total_count += 1
        return total_count

    def roulette(self) -> List[int]:
        evaluate_sum = sum(self.evaluate_result)
        select_props = [(evaluate / evaluate_sum) for evaluate in self.evaluate_result]
        select_index = random.choices(
            range(self.N), k=self.N, weights=select_props)
        return select_index

    def ranking(self) -> List[int]:
        print(self.evaluate_result)
        print(list(range(len(self.evaluate_result))))
        sort_evaluate = sorted(range(len(self.evaluate_result)), key=self.evaluate_result.__getitem__, reverse=True)
        print(sort_evaluate)
        select_index = random.choices(
            sort_evaluate, k=self.N, weights=self.ranking_props
        )
        print(select_index)
        return select_index

    def cross(self) -> None:
        pairs = self.__create_random_pairs()
        for pair in pairs:
            cross_point = random.choices(range(2), k=self.queen_num)
            for i in range(self.queen_num):
                if cross_point[i] == 1:
                    self.individual[pair[0]][i], self.individual[pair[1]
                                                                 ][i] = self.individual[pair[1]][i], self.individual[pair[0]][i]
        return None

    def __create_random_pairs(self) -> List[Tuple[int]]:
        individual_index = list(range(self.N))
        random.shuffle(individual_index)
        pairs = []
        for i in range(0, len(individual_index) - 1, 2):
            if i + 1 < len(individual_index):
                pairs.append((individual_index[i], individual_index[i + 1]))
        return pairs

    def mutation(self) -> None:
        for N in range(self.N):
            mutation_props_list = [random.random()
                                   for _ in range(self.queen_num)]
            for i in range(self.queen_num):
                if mutation_props_list[i] < self.mutation_props:
                    self.individual[N][i] = random.choices(range(self.queen_num))[0]
        return None

    def step(self) -> None:
        self.evaluate()
        select_index = self.select_func()
        self.individual = [self.individual[index] for index in select_index]
        self.cross()
        self.mutation()
        return None

    def fit(self) -> None:
        gen = 0
        self.__init_individual()
        print('====== init individual ======')
        self.__print_init_individual()
        while gen < self.gen:
            print(f'====== {gen} step =======')
            self.step()
            self.__print_individual_evaluate()
            if 1. in self.evaluate_result:
                self.fitting_results = [self.individual[i] for i, evaluate in enumerate(self.evaluate_result) if evaluate == 1.]
                break
            gen += 1
        self.total_loop = gen
        return None

    def __print_individual_evaluate(self) -> None:
        for i, (individual, evaluate) in enumerate(zip(self.individual, self.evaluate_result)):
            print(f'{i}: {individual}, {evaluate}')
        return None

    def __print_init_individual(self) -> None:
        for i, individual in enumerate(self.individual):
            print(f'{i}: {individual}')
        return None
