# test_mutation.py
# coding: utf-8

import pytest
import random
from ga import Mutation


class TestMutation:
    """Mutationクラスのテスト"""

    def test_init(self):
        """初期化のテスト"""
        N = 10
        N_length = 8
        mutation_props = 0.1
        mutation = Mutation(N, N_length, mutation_props)

        assert mutation.N == N
        assert mutation.N_length == N_length
        assert mutation.mutation_props == mutation_props
        assert 'random_bit' in mutation.mutation_func
        assert 'random' in mutation.mutation_func
        assert 'point' in mutation.mutation_func
        assert 'shuffle' in mutation.mutation_func
        assert mutation.xor_value == 1

    def test_random_bit_mutation_basic(self):
        """ランダムビット変異の基本動作テスト"""
        N = 4
        N_length = 8
        mutation_props = 0.3
        mutation = Mutation(N, N_length, mutation_props)
        individual = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 0]
        ]

        random.seed(42)
        mutation.random_bit_mutation(individual)

        # 個体数とサイズが変わっていないこと
        assert len(individual) == N
        for ind in individual:
            assert len(ind) == N_length

    def test_random_bit_mutation_flips_bits(self):
        """ランダムビット変異がビットを反転することのテスト"""
        N = 1
        N_length = 100
        mutation_props = 0.5  # 高い変異確率
        mutation = Mutation(N, N_length, mutation_props)
        individual = [[0] * N_length]

        random.seed(42)
        mutation.random_bit_mutation(individual)

        # いくつかのビットが1に反転しているはず
        flipped_count = sum(individual[0])
        assert flipped_count > 0
        # 全ての値が0か1であること
        assert all(val in [0, 1] for val in individual[0])

    def test_random_mutation_basic(self):
        """ランダム変異の基本動作テスト"""
        N = 4
        N_length = 8
        mutation_props = 0.3
        mutation = Mutation(N, N_length, mutation_props)
        individual = [
            [0, 1, 2, 3, 4, 5, 6, 7],
            [7, 6, 5, 4, 3, 2, 1, 0],
            [1, 2, 3, 4, 5, 6, 7, 0],
            [0, 7, 6, 5, 4, 3, 2, 1]
        ]

        random.seed(42)
        mutation.random_mutation(individual)

        # 個体数とサイズが変わっていないこと
        assert len(individual) == N
        for ind in individual:
            assert len(ind) == N_length

    def test_random_mutation_changes_values(self):
        """ランダム変異が値を変更することのテスト"""
        N = 1
        N_length = 100
        mutation_props = 0.5  # 高い変異確率
        mutation = Mutation(N, N_length, mutation_props)
        individual = [[0] * N_length]
        original = individual[0].copy()

        random.seed(42)
        mutation.random_mutation(individual)

        # いくつかの値が変更されているはず
        changed_count = sum(1 for i in range(N_length) if individual[0][i] != original[i])
        assert changed_count > 0

    def test_random_mutation_range(self):
        """ランダム変異の値範囲のテスト"""
        N = 4
        N_length = 8
        mutation_props = 1.0  # 全て変異
        mutation = Mutation(N, N_length, mutation_props)
        individual = [[0] * N_length for _ in range(N)]

        random.seed(42)
        mutation.random_mutation(individual)

        # 変異後の値が0からN_length-1の範囲であること
        for ind in individual:
            assert all(0 <= val < N_length for val in ind)

    def test_point_mutation_basic(self):
        """ポイント変異の基本動作テスト"""
        N = 4
        N_length = 8
        mutation_props = 0.3
        mutation = Mutation(N, N_length, mutation_props)
        individual = [
            [0, 1, 2, 3, 4, 5, 6, 7],
            [7, 6, 5, 4, 3, 2, 1, 0],
            [1, 2, 3, 4, 5, 6, 7, 0],
            [0, 7, 6, 5, 4, 3, 2, 1]
        ]

        random.seed(42)
        mutation.point_mutation(individual)

        # 個体数とサイズが変わっていないこと
        assert len(individual) == N
        for ind in individual:
            assert len(ind) == N_length

    def test_point_mutation_swaps(self):
        """ポイント変異が要素を交換することのテスト"""
        N = 1
        N_length = 10
        mutation_props = 1.0  # 全ての位置で変異
        mutation = Mutation(N, N_length, mutation_props)
        individual = [list(range(N_length))]
        original_set = set(individual[0])

        random.seed(42)
        mutation.point_mutation(individual)

        # 同じ要素セットを持つこと（順列）
        assert set(individual[0]) == original_set

    def test_shuffle_mutation_basic(self):
        """シャッフル変異の基本動作テスト"""
        N = 4
        N_length = 8
        mutation_props = 0.5
        mutation = Mutation(N, N_length, mutation_props)
        individual = [
            [0, 1, 2, 3, 4, 5, 6, 7],
            [7, 6, 5, 4, 3, 2, 1, 0],
            [1, 2, 3, 4, 5, 6, 7, 0],
            [0, 7, 6, 5, 4, 3, 2, 1]
        ]

        random.seed(42)
        mutation.shuffle_mutation(individual)

        # 個体数とサイズが変わっていないこと
        assert len(individual) == N
        for ind in individual:
            assert len(ind) == N_length

    def test_shuffle_mutation_preserves_elements(self):
        """シャッフル変異が要素を保存することのテスト"""
        N = 4
        N_length = 8
        mutation_props = 1.0  # 全て変異
        mutation = Mutation(N, N_length, mutation_props)
        individual = [
            [0, 1, 2, 3, 4, 5, 6, 7],
            [7, 6, 5, 4, 3, 2, 1, 0],
            [1, 2, 3, 4, 5, 6, 7, 0],
            [0, 7, 6, 5, 4, 3, 2, 1]
        ]
        original_sets = [set(ind) for ind in individual]

        random.seed(42)
        mutation.shuffle_mutation(individual)

        # 各個体が元と同じ要素セットを持つこと
        for i in range(N):
            assert set(individual[i]) == original_sets[i]

    def test_mutation_props_zero(self):
        """変異確率0のテスト"""
        N = 4
        N_length = 8
        mutation_props = 0.0  # 変異なし
        mutation = Mutation(N, N_length, mutation_props)
        individual = [
            [0, 1, 2, 3, 4, 5, 6, 7],
            [7, 6, 5, 4, 3, 2, 1, 0],
            [1, 2, 3, 4, 5, 6, 7, 0],
            [0, 7, 6, 5, 4, 3, 2, 1]
        ]
        original = [ind.copy() for ind in individual]

        random.seed(42)
        mutation.point_mutation(individual)

        # 変異確率0なので変化しないはず
        assert individual == original

    def test_mutation_with_different_N_length(self):
        """異なるN_lengthでの変異テスト"""
        for N_length in [4, 8, 16, 32]:
            N = 4
            mutation_props = 0.3
            mutation = Mutation(N, N_length, mutation_props)
            individual = [[i % N_length for i in range(N_length)] for _ in range(N)]

            random.seed(42)
            mutation.point_mutation(individual)

            # サイズが維持されていること
            for ind in individual:
                assert len(ind) == N_length

    def test_point_mutation_modifies_inplace(self):
        """ポイント変異がin-placeで変更することのテスト"""
        N = 2
        N_length = 6
        mutation_props = 1.0
        mutation = Mutation(N, N_length, mutation_props)
        individual = [
            [0, 1, 2, 3, 4, 5],
            [5, 4, 3, 2, 1, 0]
        ]
        original_ids = [id(ind) for ind in individual]

        random.seed(42)
        mutation.point_mutation(individual)

        # 同じオブジェクトIDであること（in-place変更）
        assert [id(ind) for ind in individual] == original_ids

    def test_random_bit_mutation_with_high_props(self):
        """高い変異確率でのビット変異テスト"""
        N = 1
        N_length = 10
        mutation_props = 0.9  # 非常に高い確率
        mutation = Mutation(N, N_length, mutation_props)
        individual = [[0] * N_length]

        random.seed(42)
        mutation.random_bit_mutation(individual)

        # ほとんどのビットが反転しているはず
        flipped_count = sum(individual[0])
        assert flipped_count >= N_length * 0.7  # 少なくとも70%

    def test_shuffle_mutation_changes_order(self):
        """シャッフル変異が順序を変更することのテスト"""
        N = 1
        N_length = 10
        mutation_props = 1.0
        mutation = Mutation(N, N_length, mutation_props)
        individual = [list(range(N_length))]
        original = individual[0].copy()

        random.seed(42)
        mutation.shuffle_mutation(individual)

        # 順序が変わっているはず（確率的には変わるはず）
        assert individual[0] != original
        # でも要素は同じ
        assert sorted(individual[0]) == sorted(original)
