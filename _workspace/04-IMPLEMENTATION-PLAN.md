# 04. 구현 계획 — `main.py` 설계

> 요구사항 ID(R1~R12, B1~B2)는 [03-REQUIREMENTS-SPEC.md](03-REQUIREMENTS-SPEC.md) 를 참조합니다.

---

## 1. 파일 구성

```text
mission-3/
├─ main.py            ← 제출물 (전체 로직, 단일 파일)
├─ data.json          ← 제공된 데이터 (수정 금지)
├─ README.md          ← 제출물 (실행 방법 + 결과 리포트)
├─ .python-version    ← pyenv 로컬 버전 (커밋 권장)
├─ .venv/             ← 가상환경 (커밋 제외)
└─ _workspace/        ← 작업 문서 (본 폴더)
```

> 미션 제출물은 `main.py` **단일 파일**입니다. 모듈을 쪼개지 말고 섹션 주석으로 구분하세요.

---

## 2. 상수 정의

```python
EPSILON = 1e-9           # R6: 동점 판정 허용오차
REPEAT = 10              # R8: 성능 측정 반복 횟수
DATA_FILE = 'data.json'
PERF_SIZES = (3, 5, 13, 25)   # R8-5: 성능 측정 대상 크기

LABEL_CROSS = 'Cross'    # R4: 표준 라벨
LABEL_X = 'X'
LABEL_UNDECIDED = 'UNDECIDED'

LABEL_MAP = {            # R4-2, R4-3: 원본 → 표준 라벨
    '+': LABEL_CROSS,
    'cross': LABEL_CROSS,
    'x': LABEL_X,
}
```

---

## 3. 함수 설계 (구현 순서 = 아래 순서)

### STEP 1 — 핵심 연산 (R5)

```python
def mac_operation(pattern, filter_matrix):
    """패턴과 필터를 위치별로 곱해 모두 더한 MAC 점수를 반환한다.

    외부 라이브러리 없이 이중 for 문으로 직접 구현한다. (R5-2)
    반환: float
    """
    total = 0.0
    for i in range(len(pattern)):
        for j in range(len(pattern[i])):
            total += pattern[i][j] * filter_matrix[i][j]
    return total
```

### STEP 2 — 판정 (R6, R7)

```python
def decide(score_a, score_b, label_a, label_b):
    """두 점수를 epsilon 기반으로 비교해 승자 라벨 또는 UNDECIDED 를 반환한다."""
    if abs(score_a - score_b) < EPSILON:
        return LABEL_UNDECIDED
    return label_a if score_a > score_b else label_b


def normalize_label(raw):
    """'+'/'x'/'cross' 등 원본 표기를 표준 라벨(Cross/X)로 정규화한다. (R4)

    알 수 없는 값이면 None 을 반환해 호출부에서 FAIL 처리하게 한다.
    """
    if raw is None:
        return None
    return LABEL_MAP.get(str(raw).strip().lower())
```

### STEP 3 — 성능 측정 (R8)

```python
def measure_mac_ms(pattern, filter_matrix, repeat=REPEAT):
    """MAC 연산을 repeat 회 반복 실행하고 1회 평균 시간(ms)을 반환한다.

    I/O 를 측정 구간에 포함하지 않는다. (R8-3)
    """
    start = time.perf_counter()
    for _ in range(repeat):
        mac_operation(pattern, filter_matrix)
    return (time.perf_counter() - start) / repeat * 1000.0
```

### STEP 4 — 패턴 생성기 (B2, 3×3 성능측정에도 사용)

```python
def make_cross(n):
    """N×N 십자가 패턴을 생성한다."""
    return [[1.0 if (i == n // 2 or j == n // 2) else 0.0
             for j in range(n)] for i in range(n)]


def make_x(n):
    """N×N X 패턴을 생성한다."""
    return [[1.0 if (i == j or i + j == n - 1) else 0.0
             for j in range(n)] for i in range(n)]
```

### STEP 5 — 입력 처리 (R2)

```python
def read_matrix(title, n):
    """n 줄 × n 열의 행렬을 콘솔에서 입력받는다.

    형식 오류(행/열 개수, 숫자 파싱)가 있으면 안내 후 처음부터 재입력을 유도한다. (R2-3, R2-4)
    """
    while True:
        print(f'{title} ({n}줄 입력, 공백 구분)')
        rows = []
        ok = True
        for _ in range(n):
            line = input().strip()
            tokens = line.split()
            if len(tokens) != n:                      # 열 수 검증
                print(f'입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요.')
                ok = False
                break
            try:
                rows.append([float(t) for t in tokens])   # 숫자 파싱 검증
            except ValueError:
                print('입력 형식 오류: 숫자만 입력할 수 있습니다.')
                ok = False
                break
        if ok and len(rows) == n:                     # 행 수 검증
            return rows
        print('다시 입력해 주세요.\n')
```

### STEP 6 — JSON 로드 및 검증 (R3)

```python
def load_data(path=DATA_FILE):
    """data.json 을 읽어 dict 로 반환한다. 실패 시 None 과 사유를 반환한다."""

def parse_size_from_key(key):
    """'size_13_1' → 13 을 추출한다. 실패 시 None."""

def validate_square(matrix, expected_n):
    """행 수/열 수가 모두 expected_n 인지 검사한다. (R3-4)"""
```

> **핵심**: 모든 케이스 처리는 `try/except` 로 감싸고, 예외가 나면
> 해당 케이스만 `FAIL` + 사유 기록 후 **다음 케이스로 계속 진행**합니다. (R3-5, R11-3)

### STEP 7 — 모드 1 / 모드 2 실행 함수 (R10)

```python
def run_mode_user_input():   # R10-2
def run_mode_json():         # R10-3
def print_performance_table(sizes=PERF_SIZES):   # R8
def main():                  # R10-1 모드 선택
```

---

## 4. 실행 흐름 상세

### 모드 1 (사용자 입력, 3×3)

```text
1. "필터 A (3줄 입력, 공백 구분)"  → read_matrix()  → 검증/재입력
2. "필터 B (3줄 입력, 공백 구분)"  → read_matrix()  → 검증/재입력
3. 저장 확인 메시지 출력 (예: "✓ 필터 A/B 저장 완료")
4. "패턴 (3줄 입력, 공백 구분)"    → read_matrix()  → 검증/재입력
5. score_a = mac_operation(pattern, filter_a)
   score_b = mac_operation(pattern, filter_b)
6. verdict = decide(score_a, score_b, 'A', 'B')   # 동점 → 판정 불가
7. 평균 연산 시간(10회) 출력
8. 성능 분석(3×3) 표 출력
```

### 모드 2 (data.json 분석)

```text
1. load_data() → 실패 시 안내 후 종료(또는 모드 선택으로 복귀)
2. filters 로드 → size_5 / size_13 / size_25 각각 cross, x 확인
   → 로드 완료 메시지 출력 (라벨은 정규화된 Cross, X 로 표기)
3. patterns 순회 (정렬된 키 순서 권장)
   for key, item in patterns:
       a. N = parse_size_from_key(key)            → 실패 시 FAIL(키 규칙 위반)
       b. filt = filters['size_%d' % N]           → 없으면 FAIL(필터 누락)
       c. validate_square(item['input'], N)       → 불일치 시 FAIL(크기 불일치)
       d. validate_square(cross_filter, N) 등     → 불일치 시 FAIL
       e. score_cross = mac_operation(input, cross_filter)
          score_x     = mac_operation(input, x_filter)
       f. verdict  = decide(score_cross, score_x, 'Cross', 'X')
          expected = normalize_label(item['expected'])  → None 이면 FAIL(라벨 규칙 위반)
       g. PASS if verdict == expected else FAIL
       h. 케이스 결과 출력 + 실패 시 사유 저장
4. 성능 분석 표 출력 (3×3 포함, 5/13/25)
5. 결과 요약 출력: 총 / 통과 / 실패 + 실패 케이스 목록
```

---

## 5. 출력 포맷 예시

> 원문 예시는 참고용이며 문구·디자인은 달라도 됩니다. 아래는 정돈된 권장 형태입니다.

### 모드 선택

```text
=== Mini NPU Simulator ===

[모드 선택]
1. 사용자 입력 (3x3)
2. data.json 분석
선택: _
```

### 모드 1 결과

```text
----------------------------------------
[3] MAC 결과
----------------------------------------
A 점수: 1.0
B 점수: 5.0
연산 시간(평균/10회): 0.012 ms
판정: B
```

동점(판정 불가) 케이스:

```text
A 점수: 0.9000000000000000
B 점수: 0.8999999999999999
판정: 판정 불가 (|A-B| < 1e-9)
```

### 모드 2 결과

```text
----------------------------------------
[1] 필터 로드
----------------------------------------
✓ size_5  필터 로드 완료 (Cross, X)
✓ size_13 필터 로드 완료 (Cross, X)
✓ size_25 필터 로드 완료 (Cross, X)

----------------------------------------
[2] 패턴 분석 (라벨 정규화 적용)
----------------------------------------
--- size_5_1 ---
Cross 점수: 0.9
X 점수: 0.8999999999999999
판정: UNDECIDED | expected: X | FAIL (동점 규칙)
```

### 성능 분석 표

```text
----------------------------------------
[3] 성능 분석 (평균/10회)
----------------------------------------
크기        평균 시간(ms)      연산 횟수(N²)
--------------------------------------------
3x3            0.0010                9
5x5            0.0028               25
13x13          0.0187              169
25x25          0.0682              625
```

### 결과 요약

```text
----------------------------------------
[4] 결과 요약
----------------------------------------
총 테스트: 6개
통과: 3개
실패: 3개

실패 케이스:
- size_5_1  : 동점(UNDECIDED) 처리 규칙에 따라 FAIL (|Δ|=1.11e-16 < 1e-9)
- size_13_2 : 동점(UNDECIDED) 처리 규칙에 따라 FAIL (|Δ|=2.66e-15 < 1e-9)
- size_25_1 : 동점(UNDECIDED) 처리 규칙에 따라 FAIL (|Δ|=1.78e-15 < 1e-9)
```

> 실제 수치는 [05-VERIFICATION.md](05-VERIFICATION.md) 의 정답표와 대조하세요.

---

## 6. 구현 순서 (권장 8단계)

| 단계 | 작업 | 완료 조건 |
| --- | --- | --- |
| 1 | 상수 + `mac_operation()` | 3×3 십자가끼리 점수 5.0 나옴 |
| 2 | `normalize_label()` + `decide()` | `'+'→Cross`, 동점→UNDECIDED 확인 |
| 3 | `make_cross()` / `make_x()` | 3×3, 5×5 출력 눈으로 확인 |
| 4 | `measure_mac_ms()` + 성능 표 | 4개 크기 표 정상 출력 |
| 5 | `read_matrix()` + 모드 1 | 오류 입력 3종 재입력 동작 |
| 6 | `load_data()` + 스키마 검증 | 6개 패턴 로드 성공 |
| 7 | 모드 2 판정 루프 + PASS/FAIL | 정답표와 일치 |
| 8 | 결과 요약 + 실패 사유 출력 | 총/통과/실패 합계 일치 |

---

## 7. 흔한 실수 (미리 피하기)

| 실수 | 결과 | 예방 |
| --- | --- | --- |
| `expected` 를 정규화 없이 그대로 비교 | 전 케이스 FAIL | `normalize_label()` 을 로드 직후 1회 적용 |
| 점수 비교에 `==` 또는 `>` 만 사용 | 1e-16 차이로 잘못된 승자 결정 | `decide()` 에서 epsilon 먼저 검사 |
| `time.time()` 사용 | 해상도 부족으로 3×3 이 0.000ms | `time.perf_counter()` 사용 |
| 측정 구간에 `print`/파일읽기 포함 | 시간이 100배 부풀려짐 | 측정 구간엔 `mac_operation()` 만 |
| 성능 표에서 3×3 누락 | R8-5 미충족 | `make_cross(3)` 로 생성해 포함 |
| 크기 불일치 시 `raise` | 프로그램 중단 → R3-5 위반 | `try/except` 로 케이스 단위 FAIL |
| `input()` 이 EOF일 때 크래시 | 리다이렉션 실행 시 중단 | `try/except EOFError` 처리 |
| 모드 선택에 숫자 아닌 값 입력 | 크래시 | 유효값 검사 후 재입력 |
| NumPy import | **미션 실격** | 표준 라이브러리만 import |

---

## 8. 코드 품질 권장 사항

- PEP 8 준수 (들여쓰기 4칸, `snake_case`, 줄 길이 79~100자)
- 모든 함수에 **docstring** 작성 (역할 / 인자 / 반환)
- 문자열은 **작은따옴표** 통일 (Codyssey 관례)
- 전역 변수 최소화, 상수는 대문자
- `if __name__ == '__main__': main()` 사용

---

## 다음 단계

→ [05-VERIFICATION.md](05-VERIFICATION.md)
