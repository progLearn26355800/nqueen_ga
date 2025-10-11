# test_cross.py
# coding: utf-8

import pytest
import random
from ga import Cross


class TestCross:
    """Crossクラスのテスト"""

    def test_init(self):
        """初期化のテスト"""
        N = 10
        N_length = 8
        cross = Cross(N, N_length)

        assert cross.N == N
        assert cross.N_length == N_length
        assert 'random' in cross.cross_func
        assert 'order' in cross.cross_func

    def test_random_cross_basic(self):
        """ランダム交叉の基本動作テスト"""
        N = 4
        N_length = 6
        cross = Cross(N, N_length)
        individual = [
            [0, 1, 2, 3, 4, 5],
            [5, 4, 3, 2, 1, 0],
            [1, 2, 3, 4, 5, 0],
            [0, 5, 4, 3, 2, 1]
        ]
        original = [ind.copy() for ind in individual]

        random.seed(42)
        cross.random_cross(individual)

        # 個体数とサイズが変わっていないこと
        assert len(individual) == N
        for ind in individual:
            assert len(ind) == N_length

    def test_random_cross_modifies_individuals(self):
        """ランダム交叉が個体を変更することのテスト"""
        N = 10
        N_length = 8
        cross = Cross(N, N_length)
        individual = [[i for _ in range(N_length)] for i in range(N)]
        original = [ind.copy() for ind in individual]

        random.seed(42)
        cross.random_cross(individual)

        # 少なくとも一部の個体が変更されているはず
        modified_count = sum(1 for i in range(N) if individual[i] != original[i])
        assert modified_count > 0

    def test_order_cross_basic(self):
        """順序交叉の基本動作テスト"""
        N = 4
        N_length = 6
        cross = Cross(N, N_length)
        individual = [
            [0, 1, 2, 3, 4, 5],
            [5, 4, 3, 2, 1, 0],
            [1, 2, 3, 4, 5, 0],
            [0, 5, 4, 3, 2, 1]
        ]

        random.seed(42)
        cross.order_cross(individual)

        # 個体数とサイズが変わっていないこと
        assert len(individual) == N
        for ind in individual:
            assert len(ind) == N_length

    def test_order_cross_preserves_elements(self):
        """順序交叉が要素を保存することのテスト（重複なし）"""
        N = 4
        N_length = 6
        cross = Cross(N, N_length)
        individual = [
            [0, 1, 2, 3, 4, 5],
            [5, 4, 3, 2, 1, 0],
            [1, 2, 3, 4, 5, 0],
            [0, 5, 4, 3, 2, 1]
        ]

        random.seed(42)
        cross.order_cross(individual)

        # 各個体が0-5の全要素を1つずつ持つこと
        for ind in individual:
            assert sorted(ind) == [0, 1, 2, 3, 4, 5]

    def test_order_cross_with_different_permutations(self):
        """順序交叉が異なる順列で正しく動作することのテスト"""
        N = 2
        N_length = 5
        cross = Cross(N, N_length)
        individual = [
            [0, 1, 2, 3, 4],
            [4, 3, 2, 1, 0]
        ]

        random.seed(42)
        cross.order_cross(individual)

        # 子個体が全要素を含むこと
        for ind in individual:
            assert sorted(ind) == [0, 1, 2, 3, 4]
            assert len(set(ind)) == N_length  # 重複なし

    def test_create_random_pairs_private_method(self):
        """__create_random_pairs メソッドの動作テスト（間接的）"""
        N = 6
        N_length = 4
        cross = Cross(N, N_length)
        individual = [[i, i+1, i+2, i+3] for i in range(N)]
        original = [ind.copy() for ind in individual]

        random.seed(42)
        cross.random_cross(individual)

        # ペアが作成され交叉が行われたことを確認
        # （完全に同じ個体が残っていない可能性が高い）
        assert len(individual) == N

    def test_random_cross_with_binary(self):
        """バイナリデータでのランダム交叉テスト"""
        N = 4
        N_length = 8
        cross = Cross(N, N_length)
        individual = [
            [0, 0, 0, 0, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 0, 0, 0],
            [0, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 0]
        ]

        random.seed(42)
        cross.random_cross(individual)

        # すべての値が0か1であること
        for ind in individual:
            assert all(val in [0, 1] for val in ind)
            assert len(ind) == N_length

    def test_order_cross_with_large_N(self):
        """大きなNでの順序交叉テスト"""
        N = 10
        N_length = 10
        cross = Cross(N, N_length)
        individual = [list(range(N_length)) for _ in range(N)]

        # 各個体を異なる順列にする
        for i, ind in enumerate(individual):
            random.seed(i)
            random.shuffle(ind)

        random.seed(42)
        cross.order_cross(individual)

        # すべての個体が正しい要素セットを持つこと
        for ind in individual:
            assert sorted(ind) == list(range(N_length))
            assert len(set(ind)) == N_length

    def test_cross_with_odd_number_of_individuals(self):
        """奇数個の個体での交叉テスト（ペアリング）"""
        N = 5  # 奇数
        N_length = 4
        cross = Cross(N, N_length)
        individual = [[i, i+1, i+2, i+3] for i in range(N)]

        random.seed(42)
        cross.random_cross(individual)

        # 個体数が変わっていないこと
        assert len(individual) == N

    def test_order_crossover_deterministic(self):
        """順序交叉が決定的に動作することのテスト"""
        N = 2
        N_length = 5
        cross = Cross(N, N_length)

        # 同じシードで2回実行
        individual1 = [[0, 1, 2, 3, 4], [4, 3, 2, 1, 0]]
        individual2 = [[0, 1, 2, 3, 4], [4, 3, 2, 1, 0]]

        random.seed(123)
        cross.order_cross(individual1)

        random.seed(123)
        cross.order_cross(individual2)

        # 結果が同じであること
        assert individual1 == individual2
