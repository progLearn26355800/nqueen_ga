# coding: utf-8


import os
import shutil
import random
from typing import List, Tuple
from functools import partial


from ga import GA


# トップレベル関数として定義（pickle化を効率化）
def _evaluate_point_cost(individual: List[int], point_cost: Tuple[Tuple[int]]) -> float:
    """
    TSP問題の評価関数（並列処理用）
    """
    total_cost = _calc_point_cost(individual, point_cost)
    return 1.0 / (1.0 + total_cost)


def _calc_point_cost(individual: List[int], point_cost: Tuple[Tuple[int]]) -> float:
    """
    TSP問題の評価関数(表示用)
    """
    total_cost = 0
    individual_num = len(individual)
    for i, row in enumerate(individual):
        # ポイント間のコスト総和
        total_cost += point_cost[individual[i]][individual[(i + 1) % individual_num]]
    return total_cost


class TSP(GA):

    def __init__(self, gen: int, N: int, point_num: int,
                 point_cost: Tuple[Tuple[int]],
                 mutation_props: float, select_func: str = 'roulette',
                 ranking_props: List[float] = [], cross_func: str = 'random',
                 mutation_func: str = 'point', verbose: bool = False,
                 use_parallel: bool = False, n_workers: int = None):
        super().__init__(gen, N, point_num, mutation_props, select_func,
                         ranking_props, cross_func, mutation_func,
                         use_parallel, n_workers)
        self.point_num = point_num
        self.point_cost = point_cost
        self.evaluate_result = []
        self.fitting_results = set()
        self.total_loop = 0
        self.output_individual_dir = 'output_individual_tsp'
        self.output_all_results = 'output_result_tsp.csv'
        self.verbose = verbose

    def init_individual(self) -> None:
        self.individual = [random.sample(
            range(self.point_num), self.point_num) for _ in range(self.N)]
        return None

    def evaluate_func(self, individual: List[int]) -> float:
        """評価関数（逐次処理用）"""
        return _evaluate_point_cost(individual, self.point_cost)

    def _get_evaluate_wrapper(self):
        """並列処理用のトップレベル関数を返す"""
        return _evaluate_point_cost

    def evaluate(self) -> None:
        """個体の評価を行う（並列処理対応）"""
        # 並列化の条件: 個体数が閾値以上 AND 並列処理が有効
        if self.use_parallel and len(self.individual) >= self.parallel_threshold and self.executor is not None:
            # 最適なchunksizeを計算
            # オーバーヘッドを減らすため、より大きなchunksizeを使用
            # 目安: 各ワーカーが1〜2回処理する程度に分割（大きめ）
            optimal_chunksize = max(200, len(self.individual) // self.n_workers)

            if self.verbose:
                print(f'[並列処理] 個体数: {len(self.individual)}, ワーカー数: {self.n_workers}, chunksize: {optimal_chunksize}')

            # 並列処理で評価
            # partial を使って point_cost を固定
            eval_func = partial(self._get_evaluate_wrapper(), point_cost=self.point_cost)

            self.evaluate_result = list(self.executor.map(
                eval_func,
                self.individual,
                chunksize=optimal_chunksize
            ))
        else:
            if self.verbose:
                print(f'[逐次処理] 個体数: {len(self.individual)}, 閾値: {self.parallel_threshold}')
            # 逐次処理で評価
            self.evaluate_result = [self.evaluate_func(individual) for individual in self.individual]
        return None

    def fit(self) -> None:
        gen = 0
        self.__init_output_individual()
        self.init_individual()
        self.evaluate()
        if self.verbose:
            print('====== init individual ======')
            self.__print_individual_evaluate()
        while gen < self.gen:
            self.step()
            max_point_cost = max(self.evaluate_result)
            max_index = self.evaluate_result.index(max_point_cost)
            max_individual = self.individual[max_index]
            point_cost = _calc_point_cost(max_individual, self.point_cost)
            if self.verbose:
                print(f'====== {gen + 1} step, max_point_cost_eval: {max_point_cost} =======', end='\n')
                self.__print_individual_evaluate()
            else:
                print(f'====== {gen + 1} step, max_point_cost_eval: {max_point_cost} =======\r', end='')
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

    def output_result_individual_to_csv(self) -> None:
        with open(os.path.join(self.output_individual_dir, f'{self.output_all_results}'), 'w') as f:
            for i, individual in enumerate(self.individual):
                f.write(f"{','.join(list(map(str, individual)))},{self.evaluate_result[i]}\n")
        return None
