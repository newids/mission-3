#!/usr/bin/env python3
"""Mini NPU Simulator — MISSION 3.

MAC(Multiply-Accumulate) 연산으로 Cross/X 패턴을 판별하는 콘솔 애플리케이션.
외부 라이브러리 없이 표준 라이브러리(json, time, sys, os)만 사용한다.

실행: python main.py [data.json 경로(생략 시 main.py와 같은 폴더)]
"""

import json
import os
import sys
import time

EPSILON = 1e-9            # 동점 판정 허용오차 (권장 기준)
BENCH_REPEATS = 10        # 성능 측정 반복 횟수 (최소 기준 10회)
BENCH_SIZES = [3, 5, 13, 25]

LABEL_CROSS = "Cross"     # 내부 표준 라벨
LABEL_X = "X"
UNDECIDED = "UNDECIDED"

LINE = "-" * 43


# ---------------------------------------------------------------------------
# 데이터 구조 — n×n 패턴/필터 저장, 위치별 읽기/쓰기
# ---------------------------------------------------------------------------

class Grid:
    """n×n 2차원 패턴/필터 저장소."""

    def __init__(self, n):
        self.n = n
        self.rows = [[0.0] * n for _ in range(n)]

    def get(self, i, j):
        return self.rows[i][j]

    def set(self, i, j, value):
        self.rows[i][j] = float(value)

    @classmethod
    def from_rows(cls, rows):
        """2차원 배열을 검증해 Grid로 변환. 정사각형/숫자 조건 위반 시 ValueError."""
        if not isinstance(rows, list) or not rows:
            raise ValueError("2차원 배열이 아닙니다")
        n = len(rows)
        grid = cls(n)
        for i, row in enumerate(rows):
            if not isinstance(row, list) or len(row) != n:
                width = len(row) if isinstance(row, list) else "?"
                raise ValueError(
                    "{0}x{0} 정사각형이 아닙니다 ({1}행 길이 {2})".format(n, i + 1, width))
            for j, value in enumerate(row):
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise ValueError(
                        "숫자가 아닌 값이 있습니다 ({0}행 {1}열: {2!r})".format(i + 1, j + 1, value))
                grid.set(i, j, value)
        return grid


# ---------------------------------------------------------------------------
# 핵심 연산 — MAC / 라벨 정규화 / epsilon 판정
# ---------------------------------------------------------------------------

def mac(pattern_rows, filter_rows):
    """MAC 연산: 같은 위치끼리 곱하고(Multiply) 전부 더한다(Accumulate).

    외부 라이브러리 없이 이중 for 루프로 직접 구현한다. 곱셈 횟수는 정확히 N².
    """
    total = 0.0
    n = len(pattern_rows)
    for i in range(n):
        row_p = pattern_rows[i]
        row_f = filter_rows[i]
        for j in range(n):
            total += row_p[j] * row_f[j]
    return total


def flatten(rows):
    """보너스 B1: 2차원 배열 → 길이 N²의 1차원 배열."""
    flat = []
    for row in rows:
        for value in row:
            flat.append(value)
    return flat


def mac_flat(flat_pattern, flat_filter):
    """보너스 B1: 1차원 배열 기반 MAC (접근 패턴 단순화 버전)."""
    total = 0.0
    for k in range(len(flat_pattern)):
        total += flat_pattern[k] * flat_filter[k]
    return total


def normalize_label(raw):
    """외부 표기('+', 'x', 'cross', 대소문자 무관)를 표준 라벨(Cross/X)로 정규화.

    해석 불가능한 표기는 None을 반환한다.
    """
    if not isinstance(raw, str):
        return None
    text = raw.strip().lower()
    if text in ("+", "cross"):
        return LABEL_CROSS
    if text == "x":
        return LABEL_X
    return None


def decide(score_cross, score_x):
    """epsilon 기반 판정: 차이가 EPSILON 미만이면 동점(UNDECIDED)."""
    if abs(score_cross - score_x) < EPSILON:
        return UNDECIDED
    return LABEL_CROSS if score_cross > score_x else LABEL_X


def decide_ab(score_a, score_b):
    """모드 1(임의 필터 A/B)용 판정."""
    if abs(score_a - score_b) < EPSILON:
        return UNDECIDED
    return "A" if score_a > score_b else "B"


# ---------------------------------------------------------------------------
# 보너스 B2 — 패턴 생성기 (성능 분석과 모드 3에서 재활용)
# ---------------------------------------------------------------------------

def make_cross(n):
    """N×N 십자가 패턴: 중앙 행/열 = 1.0."""
    grid = Grid(n)
    center = n // 2
    for k in range(n):
        grid.set(center, k, 1.0)
        grid.set(k, center, 1.0)
    return grid


def make_x(n):
    """N×N X 패턴: 주대각선(i==j)과 반대각선(i+j==n-1) = 1.0."""
    grid = Grid(n)
    for k in range(n):
        grid.set(k, k, 1.0)
        grid.set(k, n - 1 - k, 1.0)
    return grid


# ---------------------------------------------------------------------------
# 콘솔 입출력 도우미
# ---------------------------------------------------------------------------

def ask(prompt=""):
    try:
        return input(prompt)
    except EOFError:
        print("\n입력이 종료되어 프로그램을 마칩니다.")
        sys.exit(0)


def header(title):
    print()
    print(LINE)
    print(title)
    print(LINE)


def format_score(score):
    return repr(score)


def read_matrix(n, name):
    """n줄, 공백 구분 입력으로 n×n 행렬을 읽는다.

    행/열 개수 불일치·숫자 파싱 실패 시 안내 문구를 출력하고 해당 행을 재입력받는다.
    """
    print("{0} ({1}줄 입력, 공백 구분)".format(name, n))
    grid = Grid(n)
    i = 0
    while i < n:
        parts = ask().split()
        if len(parts) != n:
            print("입력 형식 오류: 각 줄에 {0}개의 숫자를 공백으로 구분해 입력하세요."
                  " ({1}행부터 다시 입력)".format(n, i + 1))
            continue
        try:
            values = [float(p) for p in parts]
        except ValueError:
            print("입력 형식 오류: 숫자로 변환할 수 없는 값이 있습니다."
                  " ({0}행부터 다시 입력)".format(i + 1))
            continue
        for j, value in enumerate(values):
            grid.set(i, j, value)
        i += 1
    return grid


def echo_grid(grid, title):
    """저장 확인: Grid.get()으로 저장된 값을 다시 읽어 출력한다."""
    print("✓ {0} 저장 완료:".format(title))
    for i in range(grid.n):
        print("  " + " ".join(str(grid.get(i, j)) for j in range(grid.n)))


# ---------------------------------------------------------------------------
# 성능 분석 — 크기별 MAC 시간 측정 (I/O 제외, 연산 함수 호출 구간만)
# ---------------------------------------------------------------------------

def measure_ms(fn, a, b, repeats=BENCH_REPEATS):
    """fn(a, b) 호출 구간만 repeats회 반복 측정해 평균 시간(ms)을 반환."""
    fn(a, b)  # 워밍업: 첫 호출의 초기화 비용을 측정에서 제외
    total = 0.0
    for _ in range(repeats):
        start = time.perf_counter()
        fn(a, b)
        total += time.perf_counter() - start
    return total / repeats * 1000.0


def run_benchmark(sizes=BENCH_SIZES):
    """크기별 (N, 2D 평균 ms, 연산 횟수 N², 1D 평균 ms) 목록을 반환."""
    results = []
    for n in sizes:
        pattern = make_x(n)       # 패턴 생성기(보너스 B2)를 성능 분석에 재활용
        filt = make_cross(n)
        avg_2d = measure_ms(mac, pattern.rows, filt.rows)
        avg_1d = measure_ms(mac_flat, flatten(pattern.rows), flatten(filt.rows))
        results.append((n, avg_2d, n * n, avg_1d))
    return results


def print_benchmark(results):
    print("{0:<10}{1:>14}{2:>14}".format("크기", "평균 시간(ms)", "연산 횟수(N²)"))
    print(LINE)
    for n, avg_2d, ops, _ in results:
        print("{0:<10}{1:>14.4f}{2:>14}".format("{0}×{0}".format(n), avg_2d, ops))
    print()
    print("[보너스] 2D 이중 루프 vs 1D 평탄화 (동일 입력, 동일 {0}회 반복)".format(BENCH_REPEATS))
    print("{0:<10}{1:>12}{2:>12}{3:>10}".format("크기", "2D(ms)", "1D(ms)", "빠른 쪽"))
    print(LINE)
    for n, avg_2d, _, avg_1d in results:
        winner = "1D" if avg_1d < avg_2d else "2D"
        print("{0:<10}{1:>12.4f}{2:>12.4f}{3:>10}".format(
            "{0}×{0}".format(n), avg_2d, avg_1d, winner))


# ---------------------------------------------------------------------------
# 모드 1 — 사용자 입력 (3×3)
# ---------------------------------------------------------------------------

def mode_manual():
    header("[1] 필터 입력")
    filter_a = read_matrix(3, "필터 A")
    echo_grid(filter_a, "필터 A")
    print()
    filter_b = read_matrix(3, "필터 B")
    echo_grid(filter_b, "필터 B")

    header("[2] 패턴 입력")
    pattern = read_matrix(3, "패턴")
    echo_grid(pattern, "패턴")

    header("[3] MAC 결과")
    score_a = mac(pattern.rows, filter_a.rows)
    score_b = mac(pattern.rows, filter_b.rows)
    avg_ms = (measure_ms(mac, pattern.rows, filter_a.rows)
              + measure_ms(mac, pattern.rows, filter_b.rows)) / 2
    print("A 점수: {0}".format(format_score(score_a)))
    print("B 점수: {0}".format(format_score(score_b)))
    print("연산 시간(평균/{0}회): {1:.4f} ms".format(BENCH_REPEATS, avg_ms))
    verdict = decide_ab(score_a, score_b)
    if verdict == UNDECIDED:
        print("판정: 판정 불가 (|A-B| < 1e-9)")
    else:
        print("판정: {0}".format(verdict))

    header("[4] 성능 분석 (3×3, 평균/{0}회)".format(BENCH_REPEATS))
    print_benchmark(run_benchmark([3]))


# ---------------------------------------------------------------------------
# 모드 2 — data.json 분석
# ---------------------------------------------------------------------------

def load_filters(raw_filters):
    """filters 구역을 검증·정규화해 {'size_5': {'Cross': Grid, 'X': Grid}, ...}로 반환."""
    filters = {}
    for size_key in sorted(raw_filters, key=lambda k: (len(k), k)):
        entry = raw_filters[size_key]
        if not isinstance(entry, dict):
            print("✗ {0} 필터 스키마 오류: 객체가 아닙니다".format(size_key))
            continue
        normalized = {}
        for raw_label, rows in entry.items():
            label = normalize_label(raw_label)   # 'cross' → Cross, 'x' → X
            if label is None:
                print("✗ {0} 필터 라벨 해석 불가: {1!r}".format(size_key, raw_label))
                continue
            try:
                normalized[label] = Grid.from_rows(rows)
            except ValueError as exc:
                print("✗ {0}/{1} 필터 배열 오류: {2}".format(size_key, raw_label, exc))
        if LABEL_CROSS in normalized and LABEL_X in normalized:
            filters[size_key] = normalized
            print("✓ {0:<8} 필터 로드 완료 (Cross, X)".format(size_key))
        else:
            print("✗ {0} 필터 불완전: Cross/X 중 일부 누락".format(size_key))
    return filters


def parse_pattern_size(key):
    """패턴 키 'size_{N}_{idx}'에서 N을 추출한다. 실패 시 None."""
    parts = key.split("_")
    if len(parts) >= 2 and parts[0] == "size":
        try:
            return int(parts[1])
        except ValueError:
            return None
    return None


def analyze_case(key, entry, filters):
    """패턴 1건을 판정한다. 반환: (passed, reason, detail_lines)."""
    lines = []
    if not isinstance(entry, dict) or "input" not in entry or "expected" not in entry:
        return False, "스키마 오류: input/expected 누락", lines

    n = parse_pattern_size(key)
    if n is None:
        return False, "키 형식 오류: size_{N}_{idx} 형태가 아님", lines

    size_key = "size_{0}".format(n)
    if size_key not in filters:
        return False, "해당 크기 필터 없음 ({0})".format(size_key), lines

    try:
        pattern = Grid.from_rows(entry["input"])
    except ValueError as exc:
        return False, "패턴 배열 오류: {0}".format(exc), lines

    if pattern.n != n:
        return False, "크기 불일치: 필터 {0}×{0} vs 패턴 {1}×{1}".format(n, pattern.n), lines

    expected = normalize_label(entry["expected"])  # '+' → Cross, 'x' → X
    if expected is None:
        return False, "expected 라벨 해석 불가: {0!r}".format(entry["expected"]), lines

    score_cross = mac(pattern.rows, filters[size_key][LABEL_CROSS].rows)
    score_x = mac(pattern.rows, filters[size_key][LABEL_X].rows)
    verdict = decide(score_cross, score_x)

    lines.append("Cross 점수: {0}".format(format_score(score_cross)))
    lines.append("X 점수: {0}".format(format_score(score_x)))

    if verdict == expected:
        lines.append("판정: {0} | expected: {1} | PASS".format(verdict, expected))
        return True, "", lines
    if verdict == UNDECIDED:
        reason = "동점(UNDECIDED) 처리 규칙에 따라 FAIL (|차이| = {0:.3g} < {1})".format(
            abs(score_cross - score_x), EPSILON)
        lines.append("판정: {0} | expected: {1} | FAIL (동점 규칙)".format(verdict, expected))
    else:
        reason = "판정({0})이 expected({1})와 불일치".format(verdict, expected)
        lines.append("판정: {0} | expected: {1} | FAIL".format(verdict, expected))
    return False, reason, lines


def mode_json(data_path):
    header("[1] 필터 로드")
    try:
        with open(data_path, encoding="utf-8") as fp:
            data = json.load(fp)
    except (OSError, json.JSONDecodeError) as exc:
        print("✗ data.json 로드 실패: {0}".format(exc))
        print("  경로를 확인하세요: {0}".format(data_path))
        return

    raw_filters = data.get("filters")
    raw_patterns = data.get("patterns")
    if not isinstance(raw_filters, dict) or not isinstance(raw_patterns, dict):
        print("✗ 스키마 오류: 최상위에 filters/patterns 객체가 필요합니다")
        return

    filters = load_filters(raw_filters)

    header("[2] 패턴 분석 (라벨 정규화 적용)")
    results = []  # (key, passed, reason)
    for key, entry in raw_patterns.items():
        print("--- {0} ---".format(key))
        passed, reason, lines = analyze_case(key, entry, filters)
        for line in lines:
            print(line)
        if not passed and not lines:
            print("FAIL ({0})".format(reason))
        results.append((key, passed, reason))

    header("[3] 성능 분석 (평균/{0}회)".format(BENCH_REPEATS))
    print_benchmark(run_benchmark(BENCH_SIZES))

    header("[4] 결과 요약")
    total = len(results)
    passed_count = sum(1 for _, ok, _ in results if ok)
    failed = [(key, reason) for key, ok, reason in results if not ok]
    print("총 테스트: {0}개".format(total))
    print("통과: {0}개".format(passed_count))
    print("실패: {0}개".format(len(failed)))
    if failed:
        print()
        print("실패 케이스:")
        for key, reason in failed:
            print("- {0}: {1}".format(key, reason))


# ---------------------------------------------------------------------------
# 모드 3 — 패턴 생성기 데모 (보너스 B2)
# ---------------------------------------------------------------------------

def mode_generator():
    header("[보너스] 패턴 생성기")
    while True:
        raw = ask("생성할 크기 N (홀수 권장, 3~25): ").strip()
        try:
            n = int(raw)
        except ValueError:
            print("입력 형식 오류: 정수를 입력하세요.")
            continue
        if n < 3:
            print("입력 형식 오류: 3 이상의 크기를 입력하세요.")
            continue
        break

    cross = make_cross(n)
    x_pattern = make_x(n)
    echo_grid(cross, "{0}×{0} Cross 패턴".format(n))
    print()
    echo_grid(x_pattern, "{0}×{0} X 패턴".format(n))

    score_cross = mac(x_pattern.rows, cross.rows)
    score_x = mac(x_pattern.rows, x_pattern.rows)
    print()
    print("검증: X 패턴 입력 시 → Cross 필터 점수 {0}, X 필터 점수 {1} → 판정 {2}".format(
        format_score(score_cross), format_score(score_x),
        decide(score_cross, score_x)))


# ---------------------------------------------------------------------------
# 실행 흐름 — 모드 선택
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) > 1:
        data_path = sys.argv[1]
    else:
        data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

    print("=== Mini NPU Simulator ===")
    print()
    print("[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    print("3. 패턴 생성기 (보너스)")
    while True:
        choice = ask("선택: ").strip()
        if choice == "1":
            mode_manual()
            return
        if choice == "2":
            mode_json(data_path)
            return
        if choice == "3":
            mode_generator()
            return
        print("입력 형식 오류: 1, 2, 3 중 하나를 입력하세요.")


if __name__ == "__main__":
    main()
