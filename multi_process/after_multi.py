import time
import concurrent.futures

def is_prime(n):
    """素数判定を行う関数"""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def process_number(num):
    """各数値を処理する関数"""
    result = is_prime(num)
    return f"{num} は素数です" if result else f"{num} は素数ではありません"

def process_row(row):
    """行全体を処理する関数"""
    return [process_number(num) for num in row]

def main():
    # データ量を大幅に増やす（100行 × 100列 = 10,000個）
    # より大きな数値で計算時間を増やす
    import random
    random.seed(42)

    data = []
    for _ in range(100):
        row = [random.randint(1000000, 10000000) for _ in range(10000)]
        data.append(row)

    print(f"データ数: {len(data)} 行 × {len(data[0])} 列 = {len(data) * len(data[0])} 個")

    # 逐次処理
    start_time = time.time()
    results_seq = []
    for row in data:
        results_seq.append(process_row(row))
    sequential_time = time.time() - start_time
    print(f"逐次処理時間: {sequential_time:.4f} 秒")

    # 並列処理
    start_time = time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        results_parallel = list(executor.map(process_row, data))
    parallel_time = time.time() - start_time
    print(f"並列処理時間: {parallel_time:.4f} 秒")

    print(f"速度向上率: {sequential_time / parallel_time:.2f}倍")

if __name__ == "__main__":
    main()
