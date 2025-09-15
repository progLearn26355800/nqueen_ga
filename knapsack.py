# coding: utf-8


import os
import csv
import shutil
import random
from typing import List
from ga import GA


class Knapsack(GA):
    def __init__(self, gen: int, N: int, N_length: int, knapsack_weight: int,
                 obj_weight: List[int], obj_price: List[int],
                 mutation_props: float, select_func: str = 'roulette',
                 ranking_props: List[float] = [], cross_func: str = 'random', mutation_func: str = 'point',
                 mode: str = '01'):
        super().__init__(gen, N, N_length, mutation_props, select_func, ranking_props, cross_func, mutation_func)
        self.obj_num = N_length
        self.knapsack_weight = knapsack_weight
        self.obj_weight = obj_weight
        self.obj_price = obj_price
        self.fitting_results = []
        self.output_csv_dir = 'output_result_csv'
        self.output_max_csv_file = 'output_max_result_knapsack.csv'
        self.mode = mode
        self.obj_destiny_list = self.__calc_obj_destiny_list()
        self.mutation = KnapsackMutation(N, N_length, mutation_props, self.obj_destiny_list)

    def init_individual(self) -> None:
        if self.mode == '01':
            self.individual = [random.choices(range(2), k=self.obj_num) for _ in range(self.N)]
        else:
            self.individual = [self.__init_chrome() for _ in range(self.N)]
        return None

    def __calc_obj_destiny_list(self):
        # return tuple([int(self.obj_price[i] / self.obj_weight[i]) for i in range(self.obj_num)])
        return tuple([int(self.knapsack_weight / self.obj_weight[i]) for i in range(self.obj_num)])

    def __init_chrome(self) -> List[int]:
        return [random.choice(range(self.obj_destiny_list[i])) for i in range(self.obj_num)]

    def evaluate_func(self, individual: List[int]) -> int:
        evaluate = self.__evaluate_price(individual)
        if self.__evaluate_weight(individual) > self.knapsack_weight:
            evaluate = 0
        return evaluate

    def __evaluate_weight(self, individual: List[int]) -> float:
        weight = sum(self.obj_weight[i] * individual[i] for i in range(self.obj_num))
        return weight

    def __evaluate_price(self, individual: List[int]) -> float:
        price = sum(self.obj_price[i] * individual[i] for i in range(self.obj_num))
        return price

    def fit(self) -> None:
        gen = 0
        self.__init_output_result_csv()
        self.init_individual()
        self.evaluate()
        print('====== init individual ======')
        self.__print_individual_evaluate()
        while gen < self.gen:
            self.step()
            print(f'====== {gen + 1} step =======\r', end='')
            # self.__print_individual_evaluate()
            self.__output_result_step_csv(gen)
            gen += 1
            self.__add_output_max_evaluate(gen)
        self.total_loop = gen
        self.__output_max_evaluate()
        return None

    def __print_individual_evaluate(self) -> None:
        for i, (individual, evaluate) in enumerate(zip(self.individual, self.evaluate_result)):
            weight = self.__evaluate_weight(individual)
            print(f'{i}: {individual}, {evaluate}, {weight}')
        return None

    def __init_output_result_csv(self) -> None:
        if os.path.exists(self.output_csv_dir):
            shutil.rmtree(self.output_csv_dir)
        os.makedirs(self.output_csv_dir)
        return None

    def __output_result_step_csv(self, step: int) -> None:
        with open(os.path.join(self.output_csv_dir, f'{step}.csv'), 'w') as f:
            f.write(','.join(list(map(str, self.obj_weight)) + ['price', f'{self.knapsack_weight}']) + '\n')
            for i, (individual, evaluate) in enumerate(zip(self.individual, self.evaluate_result)):
                weight = self.__evaluate_weight(individual)
                f.write(f'{','.join(list(map(str, individual)))},{evaluate},{weight}\n')
        return None

    def __add_output_max_evaluate(self, gen) -> None:
        max_evaluate = max(self.evaluate_result)
        max_evaluate_index = self.evaluate_result.index(max_evaluate)
        max_evaluate_count = 0
        for evaluate in self.evaluate_result:
            if evaluate == max_evaluate:
                max_evaluate_count += 1
        weight = self.__evaluate_weight(self.individual[max_evaluate_index])
        output_dict = {'gen': gen, 'max_evaluate': max_evaluate, 'weight': weight, 'max_count': max_evaluate_count}
        individual_key = [f'obj_{i + 1}' for i in range(self.obj_num)]
        output_individual = self.individual[max_evaluate_index]
        output_dict.update(dict([(key, value) for key, value in zip(individual_key, output_individual)]))
        self.fitting_results.append(output_dict)
        return None

    def __output_max_evaluate(self) -> None:
        field_name = list(self.fitting_results[0].keys())
        with open(self.output_max_csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=field_name)
            writer.writeheader()
            writer.writerows(self.fitting_results)
        return None


class KnapsackMutation:
    def __init__(self, N: int, N_length: int, mutation_props: float, random_range: List[int] = []):
        self.N = N
        self.N_length = N_length
        self.mutation_props = mutation_props
        self.mutation_func = {
            'random': self.random_mutation,
        }
        self.random_range = random_range

    def random_mutation(self, individual: List[int]) -> None:
        for N in range(self.N):
            individual_copy = individual[N].copy()
            mutation_props_list = [random.random()
                                   for _ in range(self.N_length)]
            for i in range(self.N_length):
                if mutation_props_list[i] < self.mutation_props:
                    mutation_value = random.choice(range(self.random_range[i]))
                    individual_copy[i] = mutation_value
            individual[N] = individual_copy
        return None
