# test_select.py
# coding: utf-8

import pytest
import random
from ga import Select


class TestSelect:
    """Selectクラスのテスト"""

    def test_init(self):
        """初期化のテスト"""
        N = 10
        ranking_props = [0.1, 0.2, 0.3]
        select = Select(N, ranking_props)

        assert select.N == N
        assert select.ranking_props == ranking_props
        assert 'roulette' in select.select_func
        assert 'ranking' in select.select_func

    def test_roulette_selection_length(self):
        """ルーレット選択の結果数のテスト"""
        N = 10
        select = Select(N)
        evaluate_result = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

        result = select.roulette(evaluate_result)

        assert len(result) == N

    def test_roulette_selection_range(self):
        """ルーレット選択のインデックス範囲のテスト"""
        N = 10
        select = Select(N)
        evaluate_result = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

        result = select.roulette(evaluate_result)

        for index in result:
            assert 0 <= index < N

    def test_roulette_selection_probability(self):
        """ルーレット選択の確率的な傾向のテスト（高評価が選ばれやすい）"""
        N = 5
        select = Select(N)
        # 最後の要素だけ非常に高い評価
        evaluate_result = [1, 1, 1, 1, 1000]

        random.seed(42)
        results = []
        for _ in range(100):
            result = select.roulette(evaluate_result)
            results.extend(result)

        # インデックス4（高評価）が多く選ばれているはず
        count_high = results.count(4)
        assert count_high > 80  # 100回の選択で80回以上

    def test_ranking_selection_length(self):
        """ランキング選択の結果数のテスト"""
        N = 10
        ranking_props = [0.2, 0.18, 0.16, 0.14, 0.12, 0.08, 0.06, 0.04, 0.01, 0.01]
        select = Select(N, ranking_props)
        evaluate_result = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

        result = select.ranking(evaluate_result)

        assert len(result) == N

    def test_ranking_selection_range(self):
        """ランキング選択のインデックス範囲のテスト"""
        N = 10
        ranking_props = [0.2, 0.18, 0.16, 0.14, 0.12, 0.08, 0.06, 0.04, 0.01, 0.01]
        select = Select(N, ranking_props)
        evaluate_result = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

        result = select.ranking(evaluate_result)

        for index in result:
            assert 0 <= index < N

    def test_ranking_selection_sorted(self):
        """ランキング選択が評価値でソートして選択するテスト"""
        N = 5
        ranking_props = [0.5, 0.3, 0.15, 0.04, 0.01]
        select = Select(N, ranking_props)
        evaluate_result = [30, 10, 50, 20, 40]  # 最高はインデックス2(50)

        random.seed(42)
        results = []
        for _ in range(100):
            result = select.ranking(evaluate_result)
            results.extend(result)

        # インデックス2（最高評価の50）が最も多く選ばれているはず
        count_best = results.count(2)
        assert count_best > 40  # 100回の選択で40回以上

    def test_roulette_with_zero_sum(self):
        """評価値の合計が0の場合のテスト（ゼロ除算対策）"""
        N = 5
        select = Select(N)
        evaluate_result = [0, 0, 0, 0, 0]

        with pytest.raises(ZeroDivisionError):
            select.roulette(evaluate_result)

    def test_ranking_with_different_N(self):
        """異なるNでのランキング選択のテスト"""
        for N in [5, 10, 20]:
            ranking_props = [1.0 / N] * N
            select = Select(N, ranking_props)
            evaluate_result = list(range(N))

            result = select.ranking(evaluate_result)

            assert len(result) == N
            for index in result:
                assert 0 <= index < N
