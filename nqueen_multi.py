# coding: utf-8

import os
import csv
import time
import random
import shutil
import pickle
from typing import List, Tuple, Set, Dict, Any
from multiprocessing import Pool, Manager, Queue, Process, Lock, Value
from concurrent.futures import ProcessPoolExecutor, as_completed
from threading import Thread
from queue import Empty
import numpy as np

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


class ParallelNQueen(GA):
    """並列処理対応のNクイーン問題GA実装"""

    def __init__(self, gen: int, N: int, queen_num: int, mutation_props: float,
                 select_func: str = 'roulette', ranking_props: List[float] = [],
                 cross_func: str = 'random', mutation_func: str = 'point',
                 verbose: bool = False, n_processes: int = None):
        super().__init__(gen, N, queen_num, mutation_props, select_func,
                        ranking_props, cross_func, mutation_func)
        self.queen_num = queen_num
        self.evaluate_result = []
        self.fitting_results = set()  # セットで重複を自動排除
        self.total_loop = 0
        self.output_individual_dir = 'output_individual'
        self.output_all_results = 'output_all_result.csv'
        self.verbose = verbose

        # 並列処理用パラメータ
        self.n_processes = n_processes or os.cpu_count()
        self.shared_solutions = None
        self.solution_lock = None
        self.solution_counter = None

    def init_individual(self) -> None:
        """初期個体群の生成"""
        self.individual = [random.sample(
            range(self.queen_num), self.queen_num) for _ in range(self.N)]
        return None

    def __init_chrome(self) -> List[int]:
        """単一染色体の初期化"""
        return random.sample(range(self.queen_num), self.queen_num)

    def evaluate(self) -> None:
        """個体群の評価"""
        self.evaluate_result = [self.evaluate_func(
            individual) for individual in self.individual]
        return None

    def evaluate_func(self, individual: List[int]) -> float:
        """評価関数"""
        return 1 / (1 + self.__count_duplicate(individual))

    def __count_duplicate(self, individual: List[int]) -> int:
        """衝突数のカウント"""
        total_count = 0
        for i in range(len(individual)):
            for j in range(i + 1, len(individual)):
                # 対角線上の衝突をチェック
                if abs(i - j) == abs(individual[i] - individual[j]):
                    total_count += 1
        return total_count

    def parallel_fit(self) -> None:
        """並列処理でGAを実行"""
        manager = Manager()
        self.shared_solutions = manager.dict()  # 共有辞書で解を管理
        self.solution_lock = manager.Lock()
        self.solution_counter = manager.Value('i', 0)

        # プロセスプールの作成
        with ProcessPoolExecutor(max_workers=self.n_processes) as executor:
            # 各プロセスに異なるシードを与えて多様性を確保
            futures = []
            for i in range(self.n_processes):
                future = executor.submit(
                    self._worker_process,
                    i,  # worker_id
                    self.gen // self.n_processes,  # 各プロセスの世代数
                    self.shared_solutions,
                    self.solution_lock,
                    self.solution_counter,
                    random.randint(0, 1000000)  # ランダムシード
                )
                futures.append(future)

            # 進捗監視スレッド
            monitor_thread = Thread(
                target=self._monitor_progress,
                args=(self.solution_counter,)
            )
            monitor_thread.daemon = True
            monitor_thread.start()

            # 全プロセスの完了を待つ
            for future in as_completed(futures):
                try:
                    worker_solutions = future.result()
                    print(f"Worker completed with {len(worker_solutions)} solutions")
                except Exception as e:
                    print(f"Worker failed with error: {e}")

        # 結果の集約
        self.fitting_results = set(self.shared_solutions.keys())
        self.total_loop = self.gen

    def _worker_process(self, worker_id: int, generations: int,
                       shared_solutions: Dict, solution_lock: Lock,
                       solution_counter: Value, seed: int) -> Set[Tuple[int]]:
        """各ワーカープロセスの処理"""
        random.seed(seed)
        np.random.seed(seed)

        local_solutions = set()
        local_individual = [random.sample(
            range(self.queen_num), self.queen_num) for _ in range(self.N)]

        for gen in range(generations):
            # 目標解数に達したら終了
            if solution_counter.value >= MAX_PATTERN[self.queen_num - 1]:
                break

            # 評価
            evaluate_result = [self.evaluate_func(ind) for ind in local_individual]

            # 解の収集
            for i, evaluate in enumerate(evaluate_result):
                if evaluate == 1.0:
                    solution_tuple = tuple(local_individual[i])

                    # ローカルで新しい解の場合のみ共有
                    if solution_tuple not in local_solutions:
                        local_solutions.add(solution_tuple)

                        # 共有解に追加
                        with solution_lock:
                            if solution_tuple not in shared_solutions:
                                shared_solutions[solution_tuple] = worker_id
                                solution_counter.value += 1

                        # 新しい個体で置換
                        local_individual[i] = random.sample(
                            range(self.queen_num), self.queen_num)

            # 選択・交叉・突然変異
            self._evolution_step(local_individual, evaluate_result)

            # 定期的に共有解をチェックして多様性を維持
            if gen % 10 == 0:
                self._inject_diversity(local_individual, shared_solutions)

        return local_solutions

    def _evolution_step(self, individual: List[List[int]],
                       evaluate_result: List[float]) -> None:
        """進化操作（選択・交叉・突然変異）"""
        # 選択
        if self.select_func == 'roulette':
            select_index = self._roulette_selection(evaluate_result)
        else:  # ranking
            select_index = self._ranking_selection(evaluate_result)

        individual[:] = [individual[idx].copy() for idx in select_index]

        # 交叉
        if self.cross_func == 'order':
            self._order_crossover_population(individual)
        else:
            self._random_crossover_population(individual)

        # 突然変異
        if self.mutation_func == 'shuffle':
            self._shuffle_mutation_population(individual)
        else:
            self._point_mutation_population(individual)

    def _roulette_selection(self, evaluate_result: List[float]) -> List[int]:
        """ルーレット選択"""
        evaluate_sum = sum(evaluate_result)
        if evaluate_sum == 0:
            return list(range(len(evaluate_result)))

        select_props = [e / evaluate_sum for e in evaluate_result]
        return random.choices(range(len(evaluate_result)),
                            k=len(evaluate_result),
                            weights=select_props)

    def _ranking_selection(self, evaluate_result: List[float]) -> List[int]:
        """ランキング選択"""
        sorted_indices = sorted(range(len(evaluate_result)),
                              key=lambda i: evaluate_result[i],
                              reverse=True)

        # ランキング確率の生成
        n = len(evaluate_result)
        ranking_props = [2 * (n - i) / (n * (n + 1)) for i in range(n)]

        return random.choices(sorted_indices, k=n, weights=ranking_props)

    def _order_crossover_population(self, individual: List[List[int]]) -> None:
        """順序交叉を集団に適用"""
        pairs = self._create_random_pairs(len(individual))
        for p1, p2 in pairs:
            child1 = self._order_crossover(individual[p1], individual[p2])
            child2 = self._order_crossover(individual[p2], individual[p1])
            individual[p1] = child1
            individual[p2] = child2

    def _order_crossover(self, parent1: List[int], parent2: List[int]) -> List[int]:
        """順序交叉"""
        n = len(parent1)
        point1, point2 = sorted(random.sample(range(n), 2))

        child = [-1] * n
        child[point1:point2] = parent1[point1:point2]

        pointer = point2
        for value in parent2[point2:] + parent2[:point2]:
            if value not in child:
                child[pointer % n] = value
                pointer += 1

        return child

    def _random_crossover_population(self, individual: List[List[int]]) -> None:
        """ランダム交叉を集団に適用"""
        pairs = self._create_random_pairs(len(individual))
        for p1, p2 in pairs:
            cross_points = [random.random() < 0.5 for _ in range(self.queen_num)]
            for i in range(self.queen_num):
                if cross_points[i]:
                    individual[p1][i], individual[p2][i] = \
                        individual[p2][i], individual[p1][i]

    def _point_mutation_population(self, individual: List[List[int]]) -> None:
        """点突然変異を集団に適用"""
        for ind in individual:
            if random.random() < self.mutation_props:
                p1, p2 = random.sample(range(self.queen_num), 2)
                ind[p1], ind[p2] = ind[p2], ind[p1]

    def _shuffle_mutation_population(self, individual: List[List[int]]) -> None:
        """シャッフル突然変異を集団に適用"""
        for ind in individual:
            if random.random() < self.mutation_props:
                random.shuffle(ind)

    def _create_random_pairs(self, n: int) -> List[Tuple[int, int]]:
        """ランダムペアの生成"""
        indices = list(range(n))
        random.shuffle(indices)
        pairs = []
        for i in range(0, n - 1, 2):
            if i + 1 < n:
                pairs.append((indices[i], indices[i + 1]))
        return pairs

    def _inject_diversity(self, individual: List[List[int]],
                         shared_solutions: Dict) -> None:
        """共有解を参考に多様性を注入"""
        # 一部の個体を新しいランダム個体で置換
        n_replace = max(1, len(individual) // 10)
        replace_indices = random.sample(range(len(individual)), n_replace)

        for idx in replace_indices:
            individual[idx] = random.sample(range(self.queen_num), self.queen_num)

    def _monitor_progress(self, solution_counter: Value) -> None:
        """進捗監視"""
        max_solutions = MAX_PATTERN[self.queen_num - 1]

        while True:
            time.sleep(1)
            current = solution_counter.value
            if max_solutions:
                progress = (current / max_solutions) * 100
                print(f"Progress: {current}/{max_solutions} ({progress:.2f}%)",
                      end='\r')
                if current >= max_solutions:
                    break
            else:
                print(f"Solutions found: {current}", end='\r')

    def output_all_result_to_csv(self) -> None:
        """全解をCSVに出力"""
        with open(self.output_all_results, 'w') as f:
            for result in sorted(self.fitting_results):
                f.write(f"{','.join(map(str, result))}\n")
        print(f"\nSaved {len(self.fitting_results)} solutions to {self.output_all_results}")

    def get_statistics(self) -> Dict[str, Any]:
        """統計情報の取得"""
        return {
            'queen_num': self.queen_num,
            'solutions_found': len(self.fitting_results),
            'expected_solutions': MAX_PATTERN[self.queen_num - 1],
            'completion_rate': len(self.fitting_results) / MAX_PATTERN[self.queen_num - 1] * 100
                              if MAX_PATTERN[self.queen_num - 1] else 0,
            'processes_used': self.n_processes
        }


class ParallelNQueenIsland:
    """島モデル並列GA（より高度な並列化）"""

    def __init__(self, queen_num: int, n_islands: int = None,
                 migration_interval: int = 50, migration_rate: float = 0.1):
        self.queen_num = queen_num
        self.n_islands = n_islands or os.cpu_count()
        self.migration_interval = migration_interval
        self.migration_rate = migration_rate

    def run(self, total_generations: int = 10000) -> Set[Tuple[int]]:
        """島モデルGAの実行"""
        manager = Manager()
        shared_solutions = manager.dict()
        migration_queue = manager.Queue()
        solution_lock = manager.Lock()
        solution_counter = manager.Value('i', 0)

        # 各島のプロセスを起動
        processes = []
        for island_id in range(self.n_islands):
            p = Process(
                target=self._island_evolution,
                args=(island_id, total_generations, shared_solutions,
                      migration_queue, solution_lock, solution_counter)
            )
            p.start()
            processes.append(p)

        # 全プロセスの完了を待つ
        for p in processes:
            p.join()

        return set(shared_solutions.keys())

    def _island_evolution(self, island_id: int, generations: int,
                         shared_solutions: Dict, migration_queue: Queue,
                         solution_lock: Lock, solution_counter: Value) -> None:
        """各島での進化"""
        # 島固有のGAインスタンス
        ga = ParallelNQueen(
            gen=generations,
            N=50,  # 各島の個体数
            queen_num=self.queen_num,
            mutation_props=0.1 + island_id * 0.05,  # 島ごとに異なる突然変異率
            select_func='ranking' if island_id % 2 == 0 else 'roulette',
            cross_func='order' if island_id % 2 == 0 else 'random',
            mutation_func='shuffle' if island_id % 2 == 0 else 'point'
        )

        ga.init_individual()

        for gen in range(generations):
            # 通常の進化
            ga.evaluate()

            # 解の収集
            for i, evaluate in enumerate(ga.evaluate_result):
                if evaluate == 1.0:
                    solution = tuple(ga.individual[i])
                    with solution_lock:
                        if solution not in shared_solutions:
                            shared_solutions[solution] = island_id
                            solution_counter.value += 1

            # 定期的な移住
            if gen % self.migration_interval == 0:
                self._migrate(ga, island_id, migration_queue)

            # 進化ステップ
            ga.step()

    def _migrate(self, ga: ParallelNQueen, island_id: int,
                migration_queue: Queue) -> None:
        """個体の移住処理"""
        # 最良個体を送出
        best_idx = ga.evaluate_result.index(max(ga.evaluate_result))
        migration_queue.put((island_id, ga.individual[best_idx].copy()))

        # 他島からの個体を受け入れ
        try:
            while not migration_queue.empty():
                from_island, immigrant = migration_queue.get_nowait()
                if from_island != island_id:
                    # ランダムな個体を置換
                    replace_idx = random.randint(0, len(ga.individual) - 1)
                    ga.individual[replace_idx] = immigrant
        except Empty:
            pass


def benchmark_parallel_performance(queen_num: int = 8):
    """並列化の性能測定"""
    print(f"\n=== Benchmarking N-Queens (N={queen_num}) ===\n")

    # シングルプロセス版
    print("Testing single process...")
    start_time = time.time()

    single_ga = ParallelNQueen(
        gen=1000, N=100, queen_num=queen_num,
        mutation_props=0.25, select_func='ranking',
        cross_func='order', mutation_func='shuffle',
        n_processes=1
    )
    single_ga.parallel_fit()

    single_time = time.time() - start_time
    single_solutions = len(single_ga.fitting_results)

    print(f"Single process: {single_solutions} solutions in {single_time:.2f}s")

    # マルチプロセス版
    print(f"\nTesting {os.cpu_count()} processes...")
    start_time = time.time()

    multi_ga = ParallelNQueen(
        gen=1000, N=100, queen_num=queen_num,
        mutation_props=0.25, select_func='ranking',
        cross_func='order', mutation_func='shuffle',
        n_processes=os.cpu_count()
    )
    multi_ga.parallel_fit()

    multi_time = time.time() - start_time
    multi_solutions = len(multi_ga.fitting_results)

    print(f"Multi process: {multi_solutions} solutions in {multi_time:.2f}s")
    print(f"Speedup: {single_time / multi_time:.2f}x")
    print(f"Efficiency: {(single_time / multi_time) / os.cpu_count() * 100:.1f}%")

    return multi_ga


if __name__ == '__main__':
    # 並列版の実行例
    print("Starting Parallel N-Queens GA...")

    # 基本的な並列実行
    parallel_ga = ParallelNQueen(
        gen=10000,
        N=200,
        queen_num=10,
        mutation_props=0.25,
        select_func='roulette',
        ranking_props=[],  # 必要に応じて設定
        cross_func='order',
        mutation_func='shuffle',
        n_processes=4  # 使用するプロセス数
    )

    # 並列GAの実行
    start_time = time.time()
    parallel_ga.parallel_fit()
    execution_time = time.time() - start_time

    # 結果の保存
    parallel_ga.output_all_result_to_csv()

    # 統計情報の表示
    stats = parallel_ga.get_statistics()
    print("\n=== Results ===")
    print(f"N-Queens: {stats['queen_num']}")
    print(f"Solutions found: {stats['solutions_found']}")
    print(f"Expected solutions: {stats['expected_solutions']}")
    print(f"Completion rate: {stats['completion_rate']:.2f}%")
    print(f"Execution time: {execution_time:.2f} seconds")
    print(f"Processes used: {stats['processes_used']}")

    # ベンチマークの実行（オプション）
    # benchmark_parallel_performance(queen_num=8)
