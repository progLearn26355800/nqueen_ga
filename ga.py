# coding: utf-8


import random
from abc import ABC, abstractmethod
from typing import List, Tuple
from concurrent.futures import ProcessPoolExecutor
import multiprocessing


class GA(ABC):
    def __init__(self, gen: int, N: int, N_length: int, mutation_props: float, select_func: str = 'roulette',
                 ranking_props: List[float] = [], cross_func: str = 'random', mutation_func: str = 'point',
                 use_parallel: bool = False, n_workers: int = None):
        self.gen = gen
        self.N = N
        self.individual = []
        self.select = Select(N, ranking_props)
        self.mutation = Mutation(N, N_length, mutation_props)
        self.cross = Cross(N, N_length)
        self.select_func = select_func
        self.cross_func = cross_func
        self.mutation_func = mutation_func
        
        # 並列処理の設定
        self.use_parallel = use_parallel
        self.n_workers = n_workers if n_workers is not None else multiprocessing.cpu_count()

    @abstractmethod
    def init_individual(self) -> None:
        pass

    def evaluate(self) -> None:
        """個体の評価を行う（並列処理対応）"""
        if self.use_parallel and len(self.individual) > 10:  # 個体数が少ない場合は逐次処理
            # 並列処理で評価
            with ProcessPoolExecutor(max_workers=self.n_workers) as executor:
                self.evaluate_result = list(executor.map(
                    self.evaluate_func, 
                    self.individual,
                    chunksize=max(1, len(self.individual) // self.n_workers)
                ))
        else:
            # 逐次処理で評価
            self.evaluate_result = [self.evaluate_func(individual) for individual in self.individual]
        return None

    @abstractmethod
    def evaluate_func(self, individual: List[int]) -> float:
        """
        評価関数（サブクラスで実装）
        
        注意: この関数は並列処理で呼び出される可能性があるため、
        以下の点に注意してください：
        - グローバル変数への依存を避ける
        - すべての必要なデータを引数として受け取る
        - pickle化可能な型のみを使用する
        """
        pass

    def step(self) -> None:
        select_index = self.select.select_func[self.select_func](self.evaluate_result)
        self.individual = [self.individual[index] for index in select_index]
        self.cross.cross_func[self.cross_func](self.individual)
        self.mutation.mutation_func[self.mutation_func](self.individual)
        self.evaluate()
        return None

    @abstractmethod
    def fit(self) -> None:
        pass


class Select:
    def __init__(self, N: int, ranking_props: List[int] = []):
        self.N = N
        self.ranking_props = ranking_props
        self.select_func = {
            'roulette': self.roulette,
            'ranking': self.ranking
        }

    def roulette(self, evaluate_result: List[int]) -> List[int]:
        evaluate_sum = sum(evaluate_result)
        select_props = [(evaluate / evaluate_sum) for evaluate in evaluate_result]
        select_index = random.choices(
            range(self.N), k=self.N, weights=select_props)
        return select_index

    def ranking(self, evaluate_result: List[int]) -> List[int]:
        sort_evaluate = sorted(range(len(evaluate_result)), key=evaluate_result.__getitem__, reverse=True)
        select_index = random.choices(
            sort_evaluate, k=self.N, weights=self.ranking_props
        )
        return select_index


class Cross:
    def __init__(self, N: int, N_length: int):
        self.N = N
        self.N_length = N_length
        self.cross_func = {
            'random': self.random_cross,
            'order': self.order_cross
        }

    def random_cross(self, individual: List[int]) -> None:
        pairs = self.__create_random_pairs()
        for pair in pairs:
            cross_point = random.choices(range(2), k=self.N_length)
            for i in range(self.N_length):
                if cross_point[i] == 1:
                    individual[pair[0]][i], individual[pair[1]][i] = individual[pair[1]][i], individual[pair[0]][i]
        return None

    def order_cross(self, individual: List[int]) -> None:
        pairs = self.__create_random_pairs()
        for pair in pairs:
            pair_copy1 = individual[pair[0]].copy()
            pair_copy2 = individual[pair[1]].copy()
            individual[pair[0]] = self.__order_crossover(pair_copy1, pair_copy2)
            individual[pair[1]] = self.__order_crossover(pair_copy2, pair_copy1)
        return None

    def __order_crossover(self, parent1, parent2):
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

    def __create_random_pairs(self) -> List[Tuple[int]]:
        individual_index = list(range(self.N))
        random.shuffle(individual_index)
        pairs = []
        for i in range(0, len(individual_index) - 1, 2):
            if i + 1 < len(individual_index):
                pairs.append((individual_index[i], individual_index[i + 1]))
        return pairs


class Mutation:

    def __init__(self, N: int, N_length: int, mutation_props: float):
        self.N = N
        self.N_length = N_length
        self.mutation_props = mutation_props
        self.mutation_func = {
            'random_bit': self.random_bit_mutation,
            'random': self.random_mutation,
            'point': self.point_mutation,
            'shuffle': self.shuffle_mutation
        }
        self.xor_value = 1

    def random_bit_mutation(self, individual: List[int]) -> None:
        for N in range(self.N):
            individual_copy = individual[N].copy()
            mutation_props_list = [random.random()
                                   for _ in range(self.N_length)]
            for i in range(self.N_length):
                if mutation_props_list[i] < self.mutation_props:
                    individual_copy[i] ^= self.xor_value
            individual[N] = individual_copy
        return None

    def random_mutation(self, individual: List[int]) -> None:
        for N in range(self.N):
            individual_copy = individual[N].copy()
            mutation_props_list = [random.random()
                                   for _ in range(self.N_length)]
            for i in range(self.N_length):
                if mutation_props_list[i] < self.mutation_props:
                    mutation_value = random.choice(range(self.N_length))
                    individual_copy[i] = mutation_value
            individual[N] = individual_copy
        return None

    def point_mutation(self, individual: List[int]) -> None:
        for N in range(self.N):
            mutation_props_list = [random.random()
                                   for _ in range(self.N_length)]
            for i in range(self.N_length):
                if mutation_props_list[i] < self.mutation_props:
                    mutation_point = random.sample(range(self.N_length), 2)
                    individual[N][mutation_point[0]], individual[N][mutation_point[1]] = individual[N][mutation_point[1]], individual[N][mutation_point[0]]
        return None

    def shuffle_mutation(self, individual: List[int]) -> None:
        mutation_props_list = [random.random() for _ in range(self.N)]
        for N in range(self.N):
            if mutation_props_list[N] < self.mutation_props:
                random.shuffle(individual[N])
        return None
