"""size_5_1 × X 필터 MAC이 0.8999999999999999가 되는 과정 추적.

main.py의 mac()과 같은 순서(행 우선)로 곱-누적하면서,
매 단계 float에 '실제로 저장된 값'(십진 전개)과 이론값의 차이를 로그로 출력.
"""
import json
import math
import os
from decimal import Decimal
from fractions import Fraction

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, '..', '..', 'codyssey-e1-3', 'data.json')


def exact(value, digits=22):
    """float에 실제로 저장된 값을 십진수로 그대로 전개한다."""
    return str(Decimal(value))[:digits + 2]


def main():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    pattern = data['patterns']['size_5_1']['input']
    x_filter = data['filters']['size_5']['x']

    print('=' * 100)
    print('size_5_1 패턴 × X 필터 MAC 추적 (main.py mac()과 같은 행 우선 순서)')
    print('=' * 100)
    print()
    print('[0] 재료 확인: 0.1은 float에 어떻게 저장되나')
    print(f'    입력한 값        : 0.1')
    print(f'    실제 저장된 값   : {exact(0.1, 30)}...')
    print(f'    분수로 정확히    : {Fraction(0.1)}')
    print(f'                      = 3602879701896397 / 2^55  (0.1보다 5.55e-18 큼)')
    print(f'    2진수 전개       : 0.0001100110011001100... (1100 무한 반복 → 53비트에서 반올림)')
    print()
    print('[1] 곱-누적 로그 (곱이 0인 16칸은 합을 바꾸지 않으므로 생략)')
    print()
    header = (f"{'단계':>4} {'(i,j)':>6} {'p×f':>8} "
              f"{'repr(누적합) — 파이썬이 출력하는 값':<24} "
              f"{'float에 실제 저장된 값':<26} {'이론값':>6} {'오차':>12}")
    print(header)
    print('-' * 100)

    total = 0.0
    step = 0
    for i, (row_p, row_f) in enumerate(zip(pattern, x_filter)):
        for j, (p, fv) in enumerate(zip(row_p, row_f)):
            if p * fv == 0.0:
                continue
            step += 1
            total += p * fv
            ideal = Fraction(1, 10) * step
            err = float(Fraction(total) - ideal)
            print(f'{step:>4} ({i},{j})  {p:g}×{fv:g}  '
                  f'{total!r:<26} {exact(total):<28} '
                  f'{float(ideal):>6.1f} {err:>+12.2e}')

    print('-' * 100)
    print()
    print('[2] 마지막 덧셈 확대: 8번째 합 + 0.1 이 왜 0.9에 못 미치나')
    s8 = 0.1 * 1  # 재계산: 0.1을 8번 더한 합
    s8 = 0.0
    for _ in range(8):
        s8 += 0.1
    stored_01 = Fraction(0.1)
    exact_sum = Fraction(s8) + stored_01          # 반올림 전의 참값
    print(f'    8단계 합(저장값)      : {exact(s8)}')
    print(f'    + 저장된 0.1          : {exact(0.1)}')
    print(f'    = 반올림 전 참값      : {str(Decimal(exact_sum.numerator) / Decimal(exact_sum.denominator))[:24]}')
    lo, hi = 0.8999999999999999, 0.9
    print(f'    이 참값 근처의 float 눈금 (간격 = 1 ULP = {math.ulp(0.9):.2e}):')
    print(f'      아래 눈금: {exact(lo)}  ← 참값과의 거리 {float(Fraction(exact_sum) - Fraction(lo)):.3e}')
    print(f'      위   눈금: {exact(hi)}  ← 참값과의 거리 {float(Fraction(hi) - Fraction(exact_sum)):.3e}')
    print(f'    → 참값이 아래 눈금에 더 가까워서 {lo!r} 로 반올림됨')
    print()
    print('[3] 판정에 미치는 영향')
    cross, x = 0.9, s8 + 0.1
    print(f'    Cross 점수: {cross!r}   (실제 저장값 {exact(cross)})')
    print(f'    X     점수: {x!r}   (실제 저장값 {exact(x)})')
    print(f'    x == 0.9        → {x == 0.9}')
    print(f'    |Cross − X|     → {abs(cross - x):.3e}')
    print(f'    epsilon(1e-9)   → {abs(cross - x):.3e} < 1e-9 → UNDECIDED (판정하지 않음)')


if __name__ == '__main__':
    main()
