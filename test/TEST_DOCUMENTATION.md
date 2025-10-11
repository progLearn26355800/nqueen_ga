# ga.py 単体テスト仕様書

## 概要

本ドキュメントは、遺伝的アルゴリズム（GA）ライブラリ `ga.py` の単体テストの内容を整理したものです。

## テスト環境

- **テストフレームワーク**: pytest 8.4.2
- **Python バージョン**: 3.12.11
- **総テスト数**: 56
- **テスト実行時間**: 約0.45秒

---

## 1. Selectクラスのテスト (test_select.py)

### テスト対象
個体選択を行うSelectクラスの各メソッド

### テストケース一覧

| No. | テスト名 | 目的 | 検証内容 |
|-----|---------|------|---------|
| 1 | `test_init` | 初期化 | N、ranking_props、select_func辞書の正しい初期化 |
| 2 | `test_roulette_selection_length` | ルーレット選択の結果数 | 選択結果がN個であること |
| 3 | `test_roulette_selection_range` | ルーレット選択のインデックス範囲 | すべてのインデックスが0〜N-1の範囲内 |
| 4 | `test_roulette_selection_probability` | ルーレット選択の確率的傾向 | 高評価個体が選ばれやすいこと |
| 5 | `test_ranking_selection_length` | ランキング選択の結果数 | 選択結果がN個であること |
| 6 | `test_ranking_selection_range` | ランキング選択のインデックス範囲 | すべてのインデックスが0〜N-1の範囲内 |
| 7 | `test_ranking_selection_sorted` | ランキング選択のソート | 評価値でソートされた順に選択されること |
| 8 | `test_roulette_with_zero_sum` | ゼロ除算対策 | 評価値合計が0の場合にZeroDivisionErrorが発生 |
| 9 | `test_ranking_with_different_N` | 異なる個体数 | N=5,10,20で正しく動作すること |

### 主要な検証ポイント

- **ルーレット選択**: 評価値に比例した確率で個体が選択される
- **ランキング選択**: 評価値の順位に基づいて選択される
- **エッジケース**: ゼロ除算などの異常系の処理

---

## 2. Crossクラスのテスト (test_cross.py)

### テスト対象
交叉操作を行うCrossクラスの各メソッド

### テストケース一覧

| No. | テスト名 | 目的 | 検証内容 |
|-----|---------|------|---------|
| 1 | `test_init` | 初期化 | N、N_length、cross_func辞書の正しい初期化 |
| 2 | `test_random_cross_basic` | ランダム交叉の基本動作 | 個体数とサイズが維持されること |
| 3 | `test_random_cross_modifies_individuals` | ランダム交叉の変更確認 | 少なくとも一部の個体が変更されること |
| 4 | `test_order_cross_basic` | 順序交叉の基本動作 | 個体数とサイズが維持されること |
| 5 | `test_order_cross_preserves_elements` | 順序交叉の要素保存 | すべての要素が保存されること（順列） |
| 6 | `test_order_cross_with_different_permutations` | 異なる順列での順序交叉 | 異なる順列で正しく動作すること |
| 7 | `test_create_random_pairs_private_method` | ペア生成の動作確認 | 交叉ペアが正しく生成されること（間接的） |
| 8 | `test_random_cross_with_binary` | バイナリデータでの交叉 | 0/1のバイナリ値が維持されること |
| 9 | `test_order_cross_with_large_N` | 大規模個体数での順序交叉 | N=10で正しく動作すること |
| 10 | `test_cross_with_odd_number_of_individuals` | 奇数個体での交叉 | 奇数個体でペアリングが正しく行われること |
| 11 | `test_order_crossover_deterministic` | 順序交叉の決定性 | 同じシードで同じ結果が得られること |

### 主要な検証ポイント

- **ランダム交叉**: ランダムな交叉点で遺伝子を交換
- **順序交叉**: 順列を保持する交叉（N-Queen問題などに有効）
- **要素保存**: 交叉後も必要な要素が保持される
- **決定性**: 乱数シード固定時の再現性

---

## 3. Mutationクラスのテスト (test_mutation.py)

### テスト対象
変異操作を行うMutationクラスの各メソッド

### テストケース一覧

| No. | テスト名 | 目的 | 検証内容 |
|-----|---------|------|---------|
| 1 | `test_init` | 初期化 | N、N_length、mutation_props、mutation_func辞書の正しい初期化 |
| 2 | `test_random_bit_mutation_basic` | ランダムビット変異の基本 | 個体数とサイズが維持されること |
| 3 | `test_random_bit_mutation_flips_bits` | ビット反転の確認 | ビットが0↔1で反転すること |
| 4 | `test_random_mutation_basic` | ランダム変異の基本 | 個体数とサイズが維持されること |
| 5 | `test_random_mutation_changes_values` | 値の変更確認 | 値が変更されること |
| 6 | `test_random_mutation_range` | ランダム変異の値範囲 | 変異後の値が0〜N_length-1の範囲内 |
| 7 | `test_point_mutation_basic` | ポイント変異の基本 | 個体数とサイズが維持されること |
| 8 | `test_point_mutation_swaps` | ポイント変異の交換確認 | 要素が交換されること（同じ要素セット） |
| 9 | `test_shuffle_mutation_basic` | シャッフル変異の基本 | 個体数とサイズが維持されること |
| 10 | `test_shuffle_mutation_preserves_elements` | シャッフル変異の要素保存 | 要素セットが保存されること |
| 11 | `test_mutation_props_zero` | 変異確率0 | 変異確率0で変化しないこと |
| 12 | `test_mutation_with_different_N_length` | 異なる遺伝子長 | N_length=4,8,16,32で正しく動作すること |
| 13 | `test_point_mutation_modifies_inplace` | in-place変更 | 同じオブジェクトが変更されること |
| 14 | `test_random_bit_mutation_with_high_props` | 高い変異確率 | 変異確率0.9でほとんどのビットが反転 |
| 15 | `test_shuffle_mutation_changes_order` | シャッフル変異の順序変更 | 順序が変わること |

### 変異手法の詳細

#### 1. random_bit_mutation（ランダムビット変異）
- **用途**: バイナリ表現の個体
- **動作**: 各ビットを一定確率でXOR反転（0↔1）
- **特徴**: 小さな変化を与える

#### 2. random_mutation（ランダム変異）
- **用途**: 整数表現の個体
- **動作**: 各遺伝子を一定確率でランダムな値に置き換え
- **特徴**: 大きな変化を与える可能性

#### 3. point_mutation（ポイント変異）
- **用途**: 順列表現の個体（N-Queen問題など）
- **動作**: 各遺伝子位置で一定確率で2点を選んで交換
- **特徴**: 順列を保持しながら変異

#### 4. shuffle_mutation（シャッフル変異）
- **用途**: 順列表現の個体
- **動作**: 個体全体を一定確率でシャッフル
- **特徴**: 大きな順序変更

### 主要な検証ポイント

- **変異確率**: mutation_propsに従って変異が発生
- **要素保存**: 順列を保持する変異では要素が保存される
- **値範囲**: 変異後の値が適切な範囲内
- **in-place変更**: 元のオブジェクトが変更される

---

## 4. GAクラスのテスト (test_ga.py)

### テスト対象
遺伝的アルゴリズムの基底クラスGA

### テストヘルパークラス

```python
class TestableGA(GA):
    """テスト用のGA具体クラス"""
    - init_individual(): ランダムな整数リストで個体を初期化
    - evaluate_func(): 単純な合計値で評価
    - fit(): gen世代分の進化を実行

class ParallelTestableGA(TestableGA):
    """並列処理テスト用のGA"""
    - _get_evaluate_wrapper(): トップレベル関数を返す
```

### テストケース一覧

| No. | テスト名 | 目的 | 検証内容 |
|-----|---------|------|---------|
| 1 | `test_init_basic` | 基本初期化 | すべてのパラメータの正しい初期化 |
| 2 | `test_init_with_custom_functions` | カスタム関数での初期化 | select_func、cross_func、mutation_funcの設定 |
| 3 | `test_init_individual` | 個体初期化 | 正しい個体数と遺伝子長で初期化 |
| 4 | `test_evaluate` | 評価 | evaluate_resultが正しく計算される |
| 5 | `test_step` | 1ステップ実行 | 選択、交叉、変異、評価が実行される |
| 6 | `test_fit` | 学習全体 | gen世代分の進化が実行される |
| 7 | `test_parallel_disabled_by_default` | 並列処理デフォルト無効 | use_parallel=False、executor=None |
| 8 | `test_parallel_enabled` | 並列処理有効化 | use_parallel=True、executorが生成される |
| 9 | `test_parallel_evaluation_small_population` | 小規模個体数での並列評価 | 閾値以下で逐次処理 |
| 10 | `test_parallel_evaluation_large_population` | 大規模個体数での並列評価 | 閾値以上で並列処理 |
| 11 | `test_evaluate_func_abstract` | 抽象メソッドの確認 | GAクラスの直接インスタンス化でTypeError |
| 12 | `test_different_selection_methods` | 選択手法の違い | roulette/rankingで正しく動作 |
| 13 | `test_different_crossover_methods` | 交叉手法の違い | random/orderで正しく動作 |
| 14 | `test_different_mutation_methods` | 変異手法の違い | point/random/shuffle/random_bitで正しく動作 |
| 15 | `test_destructor_cleanup` | デストラクタでのクリーンアップ | Executorが正しく終了 |
| 16 | `test_parallel_threshold` | 並列化閾値 | parallel_threshold=200 |
| 17 | `test_n_workers_default` | ワーカー数デフォルト | CPU数と同じ |
| 18 | `test_step_maintains_population_size` | 個体数維持 | stepで個体数が変わらない |
| 19 | `test_with_zero_mutation_props` | 変異確率0 | mutation_props=0で動作 |
| 20 | `test_with_high_mutation_props` | 高い変異確率 | mutation_props=1で動作 |
| 21 | `test_evaluate_result_correctness` | 評価結果の正しさ | 評価関数の計算が正しい |

### 並列処理の詳細

#### 並列化の条件
1. `use_parallel=True` が設定されている
2. 個体数が `parallel_threshold`（デフォルト200）以上
3. `executor` が利用可能

#### 並列処理の最適化
- **chunksize**: `len(individual) // (n_workers * 3)` で計算
- **再利用**: ProcessPoolExecutorを事前作成して再利用
- **クリーンアップ**: デストラクタで自動的にシャットダウン

#### 並列処理の注意点
- 評価関数はトップレベル関数またはpickle化可能な関数
- グローバル変数への依存を避ける
- すべての必要なデータを引数として受け取る

### 主要な検証ポイント

- **抽象クラス**: GAクラスは直接インスタンス化できない
- **柔軟性**: 複数の選択/交叉/変異手法に対応
- **並列処理**: 大規模個体数で自動的に並列化
- **個体数維持**: 世代を通じて個体数が一定
- **評価の正確性**: evaluate_funcが正しく呼ばれる

---

## 5. テスト実行方法

### 全テストの実行

```bash
pytest test/ -v
```

### 特定のテストファイルの実行

```bash
pytest test/test_select.py -v
pytest test/test_cross.py -v
pytest test/test_mutation.py -v
pytest test/test_ga.py -v
```

### 特定のテストケースの実行

```bash
pytest test/test_select.py::TestSelect::test_init -v
```

### カバレッジレポートの生成（オプション）

```bash
pytest test/ --cov=ga --cov-report=html
```

---

## 6. テスト結果サマリー

### 実行結果
```
============================= test session starts ==============================
platform linux -- Python 3.12.11, pytest-8.4.2, pluggy-1.5.0
collected 56 items

test/test_cross.py::TestCross (11 tests) ........................... PASSED
test/test_ga.py::TestGA (21 tests) ................................. PASSED
test/test_mutation.py::TestMutation (17 tests) ..................... PASSED
test/test_select.py::TestSelect (9 tests) .......................... PASSED

======================== 56 passed, 1 warning in 0.45s =========================
```

### テスト統計

| クラス | テスト数 | 成功 | 失敗 |
|--------|---------|------|------|
| Select | 9 | 9 | 0 |
| Cross | 11 | 11 | 0 |
| Mutation | 17 | 17 | 0 |
| GA | 21 | 21 | 0 |
| **合計** | **56** | **56** | **0** |

### 警告
- `PytestCollectionWarning`: TestableGAクラスが`__init__`を持つためのコレクション警告（動作には影響なし）

---

## 7. テストカバレッジ

### カバーされている機能

#### Selectクラス
- ✅ roulette選択
- ✅ ranking選択
- ✅ エッジケース（ゼロ除算）

#### Crossクラス
- ✅ random交叉
- ✅ order交叉
- ✅ ペアリング生成
- ✅ 要素保存の確認

#### Mutationクラス
- ✅ random_bit変異
- ✅ random変異
- ✅ point変異
- ✅ shuffle変異
- ✅ 変異確率の制御

#### GAクラス
- ✅ 初期化
- ✅ 個体生成
- ✅ 評価
- ✅ 選択・交叉・変異の統合
- ✅ 並列処理（有効/無効）
- ✅ 複数の手法の組み合わせ

### カバーされていない領域

- 並列処理時の例外処理
- ファイルI/O関連（該当コードなし）
- 一部のエッジケース（極端に大きな個体数など）

---

## 8. 今後の改善提案

### テストの追加
1. **パフォーマンステスト**: 大規模個体数での実行時間計測
2. **並列処理の効果測定**: 逐次処理との比較
3. **統計的テスト**: 選択手法の分布の統計的検証
4. **メモリ使用量テスト**: 大規模個体での メモリリーク確認

### テストの改善
1. **パラメトリックテスト**: pytest.mark.parametrizeの活用
2. **フィクスチャの活用**: 共通セットアップの効率化
3. **モックの導入**: 並列処理部分の単体テスト強化

### ドキュメントの追加
1. **使用例**: 実際の問題への適用例
2. **パラメータチューニング**: 各パラメータの推奨値
3. **トラブルシューティング**: よくある問題と解決法

---

## 付録: テストで使用する主要なパラメータ

| パラメータ | 説明 | 典型的な値 |
|-----------|------|----------|
| `gen` | 世代数 | 5〜100 |
| `N` | 個体数 | 10〜500 |
| `N_length` | 遺伝子長 | 4〜100 |
| `mutation_props` | 変異確率 | 0.01〜0.3 |
| `select_func` | 選択手法 | 'roulette', 'ranking' |
| `cross_func` | 交叉手法 | 'random', 'order' |
| `mutation_func` | 変異手法 | 'point', 'random', 'shuffle', 'random_bit' |
| `use_parallel` | 並列処理 | True/False |
| `n_workers` | ワーカー数 | CPU数または指定値 |
| `parallel_threshold` | 並列化閾値 | 200（デフォルト） |

---

**作成日**: 2025-10-11
**バージョン**: 1.0
**作成者**: Claude Code
