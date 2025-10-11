# 遺伝的アルゴリズムモジュール


## 共通モジュール

- ga.py

### GAクラス
遺伝的アルゴリズムの基本モジュール．抽象基底クラスとなっている

- init_individual(self) -> None
    - 世代の初期化．抽象化されているため，継承先のクラスで初期化内容を記載
- evaluate(self) -> None
    - 世代の評価．個体単位でevaluate_func()で定義した評価を行う
- evaluate_func(individual: List[int]) -> float
    - 評価関数．抽象化されているため継承先のクラスで関数を定義する必要あり
- step(self) -> None
    - 1世代の処理.
- fit(self) -> None
    - 最適化処理．抽象化sれているため継承先のクラスで定義する必要あり

### Selectクラス
選択処理を行うクラス．

- roulette(evaluate_result: List[int]) -> List[int]
    - ルーレット選択．evaluateで算出した評価結果を渡すことで選択を行う
- ranking(evaluate_result: List[int]) -> List[int]
    - ランキング選択．evaluateで算出した評価結果を渡すことで選択を行う


### Crossクラス
交差処理を行うクラス．

- random_cross(individual: List[int]) -> None
    - 一様交差．世代の集団を渡すことで交差を行う．

- order_cross(individual: List[int]) -> None
    - 順序交差．世代の集団を渡すことで交差を行う．遺伝子の重複が起きない交差が可能


### Mutationクラス
突然変異処理を行うクラス

- random_bit_mutation(individual: List[int]) -> None
    - ビット単位遺伝子の突然変異．世代の集団を渡すことで変異を行う．
- random_mutation(individual: List[int]) -> None
    - 遺伝子単位のランダムな突然変異．世代の集団を渡すことで変異を行う．
- point_mutation(individual: List[int]) -> None
    - 遺伝子内の2点間を入れ替える．世代の集団を渡すことで変異を行う
- shuffle_mutation(individual: List[int]) -> None
    - 遺伝子の並びをランダムに入れ替える．世代の集団を渡すことで変異を行う
