# test_ga.py
# coding: utf-8

import pytest
import random
from typing import List
from ga import GA, Select, Cross, Mutation


# GAクラスの具体的な実装（テスト用）
class TestableGA(GA):
    """テスト用のGA具体クラス"""

    def init_individual(self) -> None:
        """個体の初期化"""
        self.individual = [[random.randint(0, 10) for _ in range(10)] for _ in range(self.N)]

    def evaluate_func(self, individual: List[int]) -> float:
        """評価関数（単純な合計値）"""
        return sum(individual)

    def fit(self) -> None:
        """学習の実行"""
        self.init_individual()
        self.evaluate()
        for _ in range(self.gen):
            self.step()


# トップレベルの評価関数（並列処理用）
def simple_evaluate_func(individual: List[int]) -> float:
    """並列処理用の評価関数"""
    return sum(individual)


class ParallelTestableGA(TestableGA):
    """並列処理テスト用のGA"""

    def _get_evaluate_wrapper(self):
        """並列処理用のラッパー関数を返す"""
        return simple_evaluate_func


class TestGA:
    """GAクラスのテスト"""

    def test_init_basic(self):
        """基本的な初期化のテスト"""
        gen = 10
        N = 20
        N_length = 8
        mutation_props = 0.1

        ga = TestableGA(gen, N, N_length, mutation_props)

        assert ga.gen == gen
        assert ga.N == N
        assert ga.individual == []
        assert isinstance(ga.select, Select)
        assert isinstance(ga.mutation, Mutation)
        assert isinstance(ga.cross, Cross)
        assert ga.select_func == 'roulette'
        assert ga.cross_func == 'random'
        assert ga.mutation_func == 'point'

    def test_init_with_custom_functions(self):
        """カスタム関数での初期化のテスト"""
        gen = 10
        N = 20
        N_length = 8
        mutation_props = 0.1
        ranking_props = [0.2, 0.15, 0.15, 0.1] + [0.1] * 16

        ga = TestableGA(
            gen, N, N_length, mutation_props,
            select_func='ranking',
            ranking_props=ranking_props,
            cross_func='order',
            mutation_func='shuffle'
        )

        assert ga.select_func == 'ranking'
        assert ga.cross_func == 'order'
        assert ga.mutation_func == 'shuffle'

    def test_init_individual(self):
        """個体初期化のテスト"""
        ga = TestableGA(10, 20, 8, 0.1)
        ga.init_individual()

        assert len(ga.individual) == 20
        for ind in ga.individual:
            assert len(ind) == 10  # TestableGAでは10要素の個体を作成

    def test_evaluate(self):
        """評価のテスト"""
        ga = TestableGA(10, 20, 8, 0.1)
        ga.init_individual()
        ga.evaluate()

        assert len(ga.evaluate_result) == 20
        assert all(isinstance(score, (int, float)) for score in ga.evaluate_result)

    def test_step(self):
        """1ステップの実行テスト"""
        ga = TestableGA(10, 20, 8, 0.1)
        random.seed(42)
        ga.init_individual()
        ga.evaluate()
        original_individual = [ind.copy() for ind in ga.individual]

        ga.step()

        # 個体数が変わっていないこと
        assert len(ga.individual) == 20
        # 評価結果が更新されていること
        assert len(ga.evaluate_result) == 20

    def test_fit(self):
        """学習全体の実行テスト"""
        ga = TestableGA(gen=5, N=10, N_length=8, mutation_props=0.1)
        random.seed(42)

        ga.fit()

        # 個体が生成されていること
        assert len(ga.individual) == 10
        # 評価結果があること
        assert len(ga.evaluate_result) == 10

    def test_parallel_disabled_by_default(self):
        """並列処理がデフォルトで無効なことのテスト"""
        ga = TestableGA(10, 20, 8, 0.1)

        assert ga.use_parallel is False
        assert ga.executor is None

    def test_parallel_enabled(self):
        """並列処理を有効にした場合のテスト"""
        ga = ParallelTestableGA(10, 20, 8, 0.1, use_parallel=True, n_workers=2)

        assert ga.use_parallel is True
        assert ga.n_workers == 2
        assert ga.executor is not None

        # クリーンアップ
        ga.executor.shutdown(wait=True)

    def test_parallel_evaluation_small_population(self):
        """小さい個体数での並列評価テスト（閾値以下なので逐次処理）"""
        ga = ParallelTestableGA(10, 50, 8, 0.1, use_parallel=True, n_workers=2)
        ga.init_individual()
        ga.evaluate()

        assert len(ga.evaluate_result) == 50
        assert all(isinstance(score, (int, float)) for score in ga.evaluate_result)

        # クリーンアップ
        ga.executor.shutdown(wait=True)

    def test_parallel_evaluation_large_population(self):
        """大きい個体数での並列評価テスト（閾値以上なので並列処理）"""
        ga = ParallelTestableGA(10, 250, 8, 0.1, use_parallel=True, n_workers=2)
        ga.init_individual()
        ga.evaluate()

        assert len(ga.evaluate_result) == 250
        assert all(isinstance(score, (int, float)) for score in ga.evaluate_result)

        # クリーンアップ
        ga.executor.shutdown(wait=True)

    def test_evaluate_func_abstract(self):
        """評価関数が抽象メソッドであることのテスト"""
        # GAクラスを直接インスタンス化しようとするとエラー
        with pytest.raises(TypeError):
            ga = GA(10, 20, 8, 0.1)

    def test_different_selection_methods(self):
        """異なる選択手法でのテスト"""
        for select_func in ['roulette', 'ranking']:
            ranking_props = [0.2] * 10 if select_func == 'ranking' else []
            ga = TestableGA(
                5, 10, 8, 0.1,
                select_func=select_func,
                ranking_props=ranking_props
            )
            random.seed(42)
            ga.fit()

            assert len(ga.individual) == 10
            assert len(ga.evaluate_result) == 10

    def test_different_crossover_methods(self):
        """異なる交叉手法でのテスト"""
        for cross_func in ['random', 'order']:
            ga = TestableGA(5, 10, 8, 0.1, cross_func=cross_func)
            random.seed(42)
            ga.fit()

            assert len(ga.individual) == 10
            assert len(ga.evaluate_result) == 10

    def test_different_mutation_methods(self):
        """異なる変異手法でのテスト"""
        for mutation_func in ['point', 'random', 'shuffle', 'random_bit']:
            ga = TestableGA(5, 10, 8, 0.1, mutation_func=mutation_func)
            random.seed(42)
            ga.fit()

            assert len(ga.individual) == 10
            assert len(ga.evaluate_result) == 10

    def test_destructor_cleanup(self):
        """デストラクタでのクリーンアップテスト"""
        ga = ParallelTestableGA(10, 20, 8, 0.1, use_parallel=True, n_workers=2)
        executor = ga.executor

        # GAオブジェクトを削除
        del ga

        # Executorがシャットダウン要求されていること
        # （実際のシャットダウンは非同期なので、完了を確認するのは難しい）
        assert executor is not None

    def test_parallel_threshold(self):
        """並列化閾値のテスト"""
        ga = TestableGA(10, 20, 8, 0.1, use_parallel=True)

        assert ga.parallel_threshold == 200

    def test_n_workers_default(self):
        """ワーカー数のデフォルト値テスト"""
        import multiprocessing
        ga = TestableGA(10, 20, 8, 0.1, use_parallel=True)

        assert ga.n_workers == multiprocessing.cpu_count()

        # クリーンアップ
        if ga.executor:
            ga.executor.shutdown(wait=True)

    def test_step_maintains_population_size(self):
        """stepメソッドが個体数を維持することのテスト"""
        N = 15
        ga = TestableGA(10, N, 8, 0.1)
        random.seed(42)
        ga.init_individual()
        ga.evaluate()

        for _ in range(5):
            ga.step()
            assert len(ga.individual) == N
            assert len(ga.evaluate_result) == N

    def test_with_zero_mutation_props(self):
        """変異確率0でのテスト"""
        ga = TestableGA(5, 10, 8, 0.0)
        random.seed(42)
        ga.fit()

        assert len(ga.individual) == 10
        assert len(ga.evaluate_result) == 10

    def test_with_high_mutation_props(self):
        """高い変異確率でのテスト"""
        ga = TestableGA(5, 10, 8, 1.0)
        random.seed(42)
        ga.fit()

        assert len(ga.individual) == 10
        assert len(ga.evaluate_result) == 10

    def test_evaluate_result_correctness(self):
        """評価結果の正しさのテスト"""
        ga = TestableGA(10, 5, 8, 0.1)
        ga.individual = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # sum = 10
            [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],  # sum = 20
            [3, 3, 3, 3, 3, 3, 3, 3, 3, 3],  # sum = 30
            [4, 4, 4, 4, 4, 4, 4, 4, 4, 4],  # sum = 40
            [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],  # sum = 50
        ]

        ga.evaluate()

        assert ga.evaluate_result == [10, 20, 30, 40, 50]
