# coding: utf-8


import os
import shutil
import random
from typing import List, Tuple
from functools import partial
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image


from ga import GA


# トップレベル関数として定義（pickle化を効率化）
def _evaluate_point_cost(individual: List[int], point_cost: Tuple[Tuple[int]]) -> float:
    """
    TSP問題の評価関数（並列処理用）
    """
    total_cost = _calc_point_cost(individual, point_cost)
    return -total_cost


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
                 use_parallel: bool = False, n_workers: int = None,
                 coordinates: List[Tuple[float, float]] = None,
                 show_route_interval: int = None,
                 output_image_dir: str = 'output_route_images'):
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
        self.coordinates = coordinates  # 座標データ
        self.show_route_interval = show_route_interval  # 経路表示の間隔
        self.output_image_dir = output_image_dir  # 画像出力ディレクトリ
        self.saved_image_paths = []  # 保存した画像のパスリスト
        self.fig = None  # matplotlibのfigureオブジェクト
        self.ax = None  # matplotlibのaxesオブジェクト

    def init_individual(self) -> None:
        """
        初期個体群の生成

        改善: 完全ランダムだけでなく、nearest neighborヒューリスティックで
        いくつかの良い初期解を含める
        """
        self.individual = []

        # 70%はランダム生成
        num_random = int(self.N * 0.7)
        for _ in range(num_random):
            self.individual.append(random.sample(range(self.point_num), self.point_num))

        # 30%はnearest neighbor法で生成（多様性を持たせる）
        num_nn = self.N - num_random
        for _ in range(num_nn):
            start_city = random.randint(0, self.point_num - 1)
            nn_route = self.__nearest_neighbor_route(start_city)
            self.individual.append(nn_route)

        return None

    def __nearest_neighbor_route(self, start_city: int) -> List[int]:
        """
        Nearest Neighbor法で経路を生成
        """
        route = [start_city]
        unvisited = set(range(self.point_num)) - {start_city}

        current_city = start_city
        while unvisited:
            # 最も近い未訪問都市を選択
            nearest_city = min(unvisited, key=lambda city: self.point_cost[current_city][city])
            route.append(nearest_city)
            unvisited.remove(nearest_city)
            current_city = nearest_city

        return route

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
            optimal_chunksize = max(1, len(self.individual) // (self.n_workers * 3))

                # 並列処理で評価
            # partial を使って point_cost を固定
            eval_func = partial(self._get_evaluate_wrapper(), point_cost=self.point_cost)

            self.evaluate_result = list(self.executor.map(
                eval_func,
                self.individual,
                chunksize=optimal_chunksize
            ))
        else:
            # 逐次処理で評価
            self.evaluate_result = [self.evaluate_func(individual) for individual in self.individual]
        return None

    def fit(self) -> None:
        gen = 0
        self.__init_output_individual()
        self.init_individual()
        self.evaluate()

        # 画像出力ディレクトリの初期化（座標データと表示間隔が指定されている場合）
        if self.coordinates is not None and self.show_route_interval is not None:
            self.__init_output_image_dir()

        # 初期世代の最良個体を表示
        max_point_cost = max(self.evaluate_result)
        max_index = self.evaluate_result.index(max_point_cost)
        max_individual = self.individual[max_index]
        point_cost = _calc_point_cost(max_individual, self.point_cost)

        if self.verbose:
            print('====== init individual ======')
            self.__print_individual_evaluate()

        # 経路表示が有効な場合、初期世代の最良経路を表示・保存
        if self.show_route_interval is not None:

            # 画像として保存
            if self.coordinates is not None:
                filename = os.path.join(self.output_image_dir, f'route_gen_0000.png')
                self.__plot_route(max_individual, point_cost, max_point_cost, 0, filename)
                self.saved_image_paths.append(filename)
                if self.verbose:
                    print(f'  画像を保存: {filename}')

        while gen < self.gen:
            self.step()
            max_point_cost = max(self.evaluate_result)
            max_index = self.evaluate_result.index(max_point_cost)
            max_individual = self.individual[max_index]
            point_cost = _calc_point_cost(max_individual, self.point_cost)

            # 経路表示の判定
            should_show_route = (self.show_route_interval is not None and
                                 (gen + 1) % self.show_route_interval == 0)

            print(f'====== {gen + 1} step, max_point_cost_eval: {max_point_cost} =======\r', end='')

            # 指定された間隔で経路を表示・保存
            if should_show_route:

                # 画像として保存
                if self.coordinates is not None:
                    filename = os.path.join(self.output_image_dir, f'route_gen_{gen + 1}.png')
                    self.__plot_route(max_individual, point_cost, max_point_cost, gen + 1, filename)
                    self.saved_image_paths.append(filename)

            gen += 1
        self.total_loop = gen

        # 最終世代の画像を保存（まだ保存されていない場合）
        if self.coordinates is not None and self.show_route_interval is not None:
            if len(self.saved_image_paths) == 0 or self.saved_image_paths[-1] != os.path.join(self.output_image_dir, f'route_gen_{gen}.png'):
                max_point_cost = max(self.evaluate_result)
                max_index = self.evaluate_result.index(max_point_cost)
                max_individual = self.individual[max_index]
                point_cost = _calc_point_cost(max_individual, self.point_cost)
                filename = os.path.join(self.output_image_dir, f'route_gen_{gen}.png')
                self.__plot_route(max_individual, point_cost, max_point_cost, gen, filename)
                self.saved_image_paths.append(filename)
                print(f'\n最終世代の画像を保存: {filename}')

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

    def __print_route_with_coordinates(self, individual: List[int], cost: float, eval_score: float) -> None:
        """
        経路と座標を表示する

        Args:
            individual: 経路を表す個体
            cost: 総コスト
            eval_score: 評価値
        """
        print(f'  経路: {individual}')
        print(f'  総コスト: {cost}')
        print(f'  評価値: {eval_score}')

        if self.coordinates is not None:
            print(f'  座標順序:')
            for i, point_id in enumerate(individual):
                x, y = self.coordinates[point_id]
                next_point_id = individual[(i + 1) % len(individual)]
                edge_cost = self.point_cost[point_id][next_point_id]
                print(f'    {i+1}. 地点{point_id} ({x:.2f}, {y:.2f}) -> 地点{next_point_id} (コスト: {edge_cost})')
        return None

    def __plot_route(self, individual: List[int], cost: float, eval_score: float, generation: int, filename: str) -> None:
        """
        経路を図にプロットして画像として保存する

        Args:
            individual: 経路を表す個体
            cost: 総コスト
            eval_score: 評価値
            generation: 世代数
            filename: 保存するファイル名
        """
        if self.coordinates is None:
            return None

        # 図の作成
        fig, ax = plt.subplots(figsize=(12, 10))

        # 全地点をプロット
        xs = [coord[0] for coord in self.coordinates]
        ys = [coord[1] for coord in self.coordinates]
        ax.scatter(xs, ys, c='lightblue', s=100, zorder=2, edgecolors='black', linewidth=1)

        # 地点番号を表示
        for i, (x, y) in enumerate(self.coordinates):
            ax.annotate(str(i), (x, y), fontsize=8, ha='center', va='center', weight='bold')

        # 経路をプロット
        for i, point_id in enumerate(individual):
            next_point_id = individual[(i + 1) % len(individual)]
            x1, y1 = self.coordinates[point_id]
            x2, y2 = self.coordinates[next_point_id]

            # エッジを描画
            ax.plot([x1, x2], [y1, y2], 'r-', linewidth=1.5, alpha=0.6, zorder=1)

            # 矢印を描画（方向を示す）
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            dx, dy = x2 - x1, y2 - y1
            ax.arrow(mid_x - dx * 0.1, mid_y - dy * 0.1, dx * 0.2, dy * 0.2,
                     head_width=2, head_length=1.5, fc='red', ec='red', alpha=0.6, zorder=1)

        # 開始地点を強調
        start_x, start_y = self.coordinates[individual[0]]
        ax.scatter([start_x], [start_y], c='green', s=200, zorder=3, edgecolors='black', linewidth=2, marker='*')

        # タイトルと情報を表示
        ax.set_title(f'TSP Route - Generation {generation}\nTotal Cost: {cost: .0f}, Eval Score: {eval_score: .6f}',
                     fontsize=14, weight='bold')
        ax.set_xlabel('X coordinate', fontsize=12)
        ax.set_ylabel('Y coordinate', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal', adjustable='box')

        # 画像を保存
        plt.tight_layout()
        plt.savefig(filename, dpi=100, bbox_inches='tight')
        plt.close(fig)

        return None

    def __init_output_image_dir(self) -> None:
        """画像出力ディレクトリを初期化"""
        if os.path.exists(self.output_image_dir):
            shutil.rmtree(self.output_image_dir)
        os.makedirs(self.output_image_dir)
        self.saved_image_paths = []
        return None

    def create_gif(self, output_filename: str = 'tsp_route_evolution.gif', duration: int = 500) -> None:
        """
        保存した画像からGIFアニメーションを作成する

        Args:
            output_filename: 出力するGIFファイル名
            duration: 各フレームの表示時間（ミリ秒）
        """
        if len(self.saved_image_paths) == 0:
            print('警告: 保存された画像がありません。GIFを作成できません。')
            return None

        print(f'\nGIFアニメーションを作成中... ({len(self.saved_image_paths)}枚の画像)')

        # 画像を読み込む
        images = []
        for img_path in self.saved_image_paths:
            img = Image.open(img_path)
            images.append(img)

        # GIFとして保存
        output_path = os.path.join(self.output_image_dir, output_filename)
        images[0].save(
            output_path,
            save_all=True,
            append_images=images[1:],
            duration=duration,
            loop=0  # 無限ループ
        )

        print(f'GIFアニメーションを保存しました: {output_path}')
        print(f'  フレーム数: {len(images)}')
        print(f'  フレームあたりの時間: {duration}ms')

        return None
