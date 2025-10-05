import time
import concurrent.futures

def is_prime(n):
    """素数判定を行う関数（CPU負荷の高い計算の例）"""
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
    """行全体を処理する関数（行単位で並列化する場合）"""
    return [process_number(num) for num in row]

def main():
    # 2重リストのサンプルデータ
    data = [
        [104729, 104743, 104759, 104761, 104773],
        [104779, 104789, 104801, 104803, 104827],
        [104831, 104849, 104851, 104869, 104873],
        [104891, 104907, 104917, 104933, 104947]
    ]
    
    start_time = time.time()
    
    # CPUバウンドな処理なので ProcessPoolExecutor を使用
    # max_workers を指定しない場合、CPUコア数が自動的に使用されます
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        # 各行を並列処理
        results = list(executor.map(process_row, data))
    
    end_time = time.time()
    
    # 結果の表示
    print("=== 処理結果 ===")
    for i, row_results in enumerate(results):
        print(f"\n行 {i+1}:")
        for result in row_results:
            print(f"  {result}")
    
    print(f"\n処理時間: {end_time - start_time:.4f} 秒")

if __name__ == "__main__":
    main()
