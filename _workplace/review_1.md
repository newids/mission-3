# MISSION 3 메인 프로그램 평가 (review_1)

- 평가 대상: `codyssey-e1-3/main.py` (219줄)
- 기준 문서: `mission-3/docs/MISSION-3.md`
- 평가일: 2026-08-13
- 검증 환경: Python 3.9.6 (macOS), `data.json` = 필터 3종(size_5/13/25), 패턴 6건

---

## 0. 한 줄 요약

**현재 상태로는 제출 불가.** 명시된 개발 환경(Python 3.8+)에서 **문법 오류로 아예 실행되지 않고**,
실행 가능한 형태로 고쳐도 **성능 측정 단위가 10^9배 틀렸으며**, 필수 요구사항인
**결과 요약(총/통과/실패)**, **필터 키 라벨 정규화**, **크기 불일치 검증**이 구현되어 있지 않다.
MAC 연산 자체와 입력 재검증 로직은 방향이 맞다.

**요구사항 충족도: 약 45%** (아래 4장 체크리스트 기준 필수 항목 8/18 완전 충족)

---

## 1. 치명적 결함 (Blocker) — 실행 자체가 불가

### B-1. Python 3.8~3.11에서 SyntaxError (main.py:112, 114, 116)

```python
print(f"{filters.get("size_5")}")   # 112
print(f"{filters.get("size_13")}")  # 114
print(f"{filters.get("size_25")}")  # 116
```

f-string 안에서 바깥과 **같은 큰따옴표**를 다시 사용했다. 이 문법은 PEP 701이 적용된
**Python 3.12 이상에서만** 허용된다. 과제 개발 환경은 "Python 3.8 이상"이므로,
채점자가 3.8~3.11로 실행하면 프로그램이 시작조차 못 한다.

실측 (Python 3.9.6):

```text
$ python3 -m py_compile main.py
  File "main.py", line 112
    print(f"{filters.get("size_5")}")
                          ^
SyntaxError: f-string: unmatched '('
```

**수정**: 안쪽 따옴표를 작은따옴표로 바꾸거나 f-string을 쓰지 않는다.

```python
print(filters.get('size_5'))
```

> 참고: 이 3줄은 5×5/13×13/25×25 필터 **원본 배열을 통째로 콘솔에 덤프**한다.
> 25×25 배열이 한 줄로 쏟아지면 가독성이 무너진다. 요구 출력은
> `✓ size_25 필터 로드 완료 (Cross, X)` 한 줄이면 충분하므로 덤프 자체를 제거하는 편이 낫다.
> 같은 이유로 `print("meta:", meta)`(107~110줄)도 정리 대상이다.

---

## 2. 정확성 버그 (Major)

### M-1. 성능 측정 단위가 10^9배 틀림 (main.py:36)

```python
elapsed_time = (time.perf_counter_ns() - start_time) * 1000
```

`perf_counter_ns()`는 **나노초**를 반환한다. 밀리초로 바꾸려면 `/ 1_000_000`이어야 하는데
`* 1000`을 곱했다. 결과적으로 출력값은 ms가 아니라 **피코초**이며, 실제 값의 10^9배다.

실측 출력:

```text
크기       평균 시간(ms)    연산 횟수
-------------------------------------
--->>> 3×3            0.010           9
5×5		9012250.000		25
13×13		26430850.000		169
25×25		87917900.000		625
```

`25×25 = 87,917,900 ms`는 **약 24.4시간**이라는 뜻이다. 과제 예시(0.682 ms)와 8자리 차이.
이 표를 근거로 README에 O(N²)를 논증하면 논증 자체가 무너진다.

**수정**:

```python
elapsed_ms = (time.perf_counter_ns() - start_time) / 1_000_000
```

> 부수적으로, 이 값을 고치고 나면 5×5 → 13×13 → 25×25 시간비가
> 9.0 : 26.4 : 87.9 ≈ 1 : 2.9 : 9.8 로 연산 횟수비 25 : 169 : 625 = 1 : 6.8 : 25 와
> 어긋나 보이는 점도 함께 설명해야 한다(작은 N에서는 루프/함수 호출 상수 비용이 지배적).

### M-2. `mac_operation`이 점수 계산과 시간 측정을 한 덩어리로 묶음 (main.py:22-39)

```python
for _ in range(repeats):
    for p, fa in zip(pattern, filter_a):
        for n, f in zip(p, fa):
            point_a += n * f      # 누산기를 repeat마다 초기화하지 않음
...
return point_a / repeats, point_b / repeats, repeats, elapsed_time
```

세 가지 문제가 겹쳐 있다.

1. **점수의 부동소수점 오차가 증폭된다.** 10회분을 한 누산기에 계속 더한 뒤 나누므로,
   1회 계산과 결과가 달라진다. 실측 비교(size_13_2, Cross 점수):

   | 방식 | 점수 |
   | --- | --- |
   | 1회 계산 | `7.499999999999997` |
   | 10회 누적 후 ÷10 (현재 코드) | `7.4999999999999645` |

   오차가 약 10배 커졌다. 이 과제는 `1e-9` 경계에서 UNDECIDED를 판정하는 과제이므로,
   **측정 반복이 판정 결과를 흔들 수 있는 구조는 그 자체로 위험하다.**
   (현재 `data.json`에서는 다행히 판정이 뒤집히지 않음을 확인했다.)
2. **측정 구간에 필터 A/B 두 번의 MAC이 함께 들어간다.** 그런데 성능표의 "연산 횟수"는 `N²`로
   적혀 있다. 실제 측정된 것은 `2 × N² × repeats`회다. 표와 측정 대상이 불일치한다.
3. **책임 분리 위반.** "점수 계산"과 "성능 측정"은 분리해야 재사용·검증이 가능하다.

**권장 구조**:

```python
def mac(pattern, filter_matrix):
    """MAC 1회. 점수만 반환."""
    total = 0.0
    for row_p, row_f in zip(pattern, filter_matrix):
        for p_val, f_val in zip(row_p, row_f):
            total += p_val * f_val
    return total


def measure_mac_ms(pattern, filter_matrix, repeats=10):
    """MAC 연산 구간만 repeats회 측정해 1회 평균 ms 반환."""
    start = time.perf_counter_ns()
    for _ in range(repeats):
        mac(pattern, filter_matrix)
    return (time.perf_counter_ns() - start) / repeats / 1_000_000
```

### M-3. 모드 1 헤더가 판정과 모순 (main.py:59)

```python
print(f"# [3] MAC 결과 {'' if abs(point_a - point_b) > 1e-9 and point_b > point_a else '판정 불가'}")
```

조건이 **"B가 이겼을 때"만** 정상으로 취급한다. 즉 **A가 이기면 헤더에 `판정 불가`가 찍히는데
바로 아래 줄에는 `판정: A`가 출력된다.** 실측:

```text
# [3] MAC 결과 판정 불가
# ------------------------------
	A 점수: 5.0
	B 점수: 1.0
	연산 시간(평균/10회): 32562000.000 ms
	판정: A
```

재현성 요구사항 7장("모드 1: 십자가 필터와 X 필터를 예시대로 입력했을 때 점수/판정/시간이
정상 출력되어야 한다")에 정면으로 걸리는 버그다.

**수정**: 판정 로직을 함수 하나로 뽑고 헤더/본문이 같은 값을 쓰게 한다.

```python
EPSILON = 1e-9


def decide(score_a, score_b, label_a, label_b, undecided):
    if abs(score_a - score_b) < EPSILON:
        return undecided
    return label_a if score_a > score_b else label_b
```

### M-4. `zip`이 크기 불일치를 조용히 삼킨다 (main.py:28-34)

`zip(pattern, filter_a)`는 **짧은 쪽 길이에 맞춰 잘린다.** 5×5 패턴에 13×13 필터를 넣어도
예외가 발생하지 않고 5×5 영역만 계산한 "그럴듯한 틀린 점수"가 나온다.

요구사항 4.3은 *"필터와 패턴의 크기가 일치하는지 검증해야 한다 / 불일치 시 해당 케이스를 FAIL로
처리하고 원인을 메시지로 남겨야 한다"* 인데, **크기 검증 코드가 어디에도 없다.**
지금 구조는 오류를 감지하는 게 아니라 **은폐한다**. 제약사항 7장의 "의도적 오류 입력(크기 불일치)"
재현 항목도 통과할 수 없다.

**수정**: MAC 진입 전에 검증한다.

```python
def validate_size(pattern, filter_matrix):
    n = len(filter_matrix)
    if len(pattern) != n or any(len(row) != n for row in pattern):
        raise ValueError(f'크기 불일치: 필터 {n}x{n}, 패턴 {len(pattern)}행')
```

---

## 3. 요구사항 미충족 (Missing)

### R-1. [4] 결과 요약이 통째로 없음 — 필수

요구사항 6.3 및 결과 예시 `[4] 결과 요약`:

```text
총 테스트: 8개
통과: 7개
실패: 1개

실패 케이스:
- size_13_1: 동점(UNDECIDED) 처리 규칙에 따라 FAIL
```

현재 `analyze_json()`은 케이스별 PASS/FAIL을 **출력만 하고 집계하지 않는다.**
`classification_x_cross()`가 `is_pass`를 계산한 뒤 `print`하고 버린다(main.py:175-176).

이건 단순 누락이 아니라 과제의 최종 산출물 4번 "결과 리포트" 자체다.
현재 `data.json` 기준 정답은 **총 6건 / 통과 3건 / 실패 3건**이며, 실패 3건은 전부
`UNDECIDED`(size_5_1, size_13_2, size_25_1)다 — 즉 **epsilon 정책을 설명하기 위해
일부러 심어둔 케이스**이므로, 이 요약은 README 결과 리포트의 핵심 재료가 된다.

**수정**: 판정 함수가 `(label, is_pass, reason)`을 **반환**하게 하고, 호출부에서 리스트에 모아
마지막에 집계·출력한다.

### R-2. 필터 키 라벨 정규화 미구현 (main.py:90-96, 130-131)

요구사항 4.4는 정규화 대상을 **두 가지**로 명시한다.

| 대상 | 규칙 | 구현 여부 |
| --- | --- | --- |
| `expected` 값 | `'+'` → `Cross`, `'x'` → `X` | ✅ 구현됨 |
| `filter` 키 | `'cross'` → `Cross`, `'x'` → `X` | ❌ **없음** |

```python
cross_filter = filters.get(label[0]).get("cross")   # 원본 키 직접 사용
x_filter = filters.get(label[0]).get("x")
```

게다가 `label_normalization('cross')`를 실제로 호출하면 **ValueError로 죽는다.**
`value.upper() == 'X'`도 아니고 `value == '+'`도 아니기 때문이다. 함수 이름은 범용인데
`expected` 전용으로만 동작한다.

**수정**: 정규화 함수를 두 입력 모두 받도록 확장한다.

```python
LABEL_MAP = {'+': CROSS, 'cross': CROSS, 'x': X}


def normalize_label(value):
    key = str(value).strip().lower()
    if key not in LABEL_MAP:
        raise ValueError(f'알 수 없는 라벨: {value!r}')
    return LABEL_MAP[key]
```

### R-3. 패턴 키를 순회하지 않고 하드코딩 (main.py:119-123)

```python
labels = [
    ["size_5", "size_5_1", "size_5_2"],
    ["size_13", "size_13_1", "size_13_2"],
    ["size_25", "size_25_1", "size_25_2"],
]
```

요구사항 4.3은 *"patterns의 각 항목에 대해, **키에서 N을 추출하여** 해당 size_N 필터를 선택"*
하라고 요구한다. 지금은 6개 키 이름과 개수를 코드에 박아 두었으므로,

- 채점용 `data.json`에 `size_5_3`이 추가되면 → **조용히 무시**
- `size_7_1`이 추가되면 → **조용히 무시**
- `size_13_2`가 빠지면 → `patterns.get(...)`이 `None` → `AttributeError`로 **프로그램 강제 종료**

"데이터를 읽는 프로그램"이 아니라 "특정 파일 한 개에 맞춘 스크립트"가 되어 있다.

**수정**:

```python
for key in sorted(patterns):
    size = key.split('_')[1]          # 'size_13_2' -> '13'
    filter_set = filters.get(f'size_{size}')
```

### R-4. 케이스 단위 예외 격리 없음 — 프로그램이 비정상 종료됨

제약사항 7장: *"모드 2에서 스키마/크기 불일치가 발생해도 프로그램이 중단되지 않도록 처리한다."*

현재 `analyze_json()`에는 `try`가 파일 열기에만 걸려 있다(main.py:101-105). 그 뒤로는
`label_normalization`의 `ValueError`, `filters.get(...)`의 `AttributeError`,
누락 키의 `KeyError`가 전부 `main()`을 뚫고 나가 프로그램을 죽인다.
최상위 `try`는 `NotImplementedError`만 잡는다(main.py:216-219).

또한 `json.JSONDecodeError`(파일이 깨진 경우)와 `PermissionError`도 처리되지 않는다.

**수정**: 케이스 루프 내부를 `try/except Exception`으로 감싸 해당 케이스만 FAIL 처리하고
사유를 요약 목록에 담는다.

### R-5. 실행 흐름 누락 (요구사항 6.4)

| 명세된 단계 | 구현 |
| --- | --- |
| 모드 1: 필터 A, B 입력 → **저장 확인** → 패턴 입력 | ❌ 저장 확인(입력값 되읽어 출력) 없음 |
| 모드 1: … → **성능 분석(3×3) 출력** | ❌ 시간 한 줄만 있고 `크기/평균시간/연산횟수` 표 없음 |
| 모드 2: … → 성능 분석 **(3×3 포함**, 5/13/25) | ❌ 3×3이 **하드코딩 상수** |

특히 main.py:158이 문제다.

```python
print(f"--->>> 3×3            0.010           9")
```

**측정하지 않은 값 `0.010`을 측정한 것처럼 출력한다.** 성능 분석 과제에서 측정값을 위조한
형태가 되므로 감점 위험이 가장 큰 줄이다. 디버그 흔적인 `--->>>` 접두사도 그대로 남아 있고,
5/13/25 행은 탭 정렬이라 3×3 행과 열이 맞지 않는다.

**수정**: 3×3 십자가/X 필터를 코드에서 생성해 동일한 측정 함수로 측정한 뒤 같은 포맷으로 출력한다.

### R-6. 보너스 미구현 (선택 항목)

- `generate_patterns()`는 `raise NotImplementedError`(main.py:82-83). 선택 과제이므로 미구현
  자체는 감점 대상이 아니다. 다만 **메뉴 3번을 고르면 최상위 `except`가 잡아 프로그램이 종료된다.**
  메뉴로 노출한 이상 "미구현입니다" 안내 후 메뉴로 복귀해야 한다.
- 1차원 배열 최적화 비교도 미구현.

---

## 4. 요구사항 체크리스트

| # | 요구사항 | 상태 | 근거 |
| --- | --- | --- | --- |
| 1 | n×n 데이터 구조(3/5/13/25) 저장·조회 | ✅ | 중첩 리스트로 처리 |
| 2 | 모드 1 필터 A/B·패턴 한 줄씩 입력 | ✅ | `input_3x3_matrix` |
| 2 | 행/열 개수·숫자 파싱 검증 후 재입력 유도 | ✅ | 실측 재입력 동작 확인 |
| 2 | 입력 저장 확인 출력 | ❌ | R-5 |
| 3 | data.json filters/patterns 로드 | ⚠️ | 하드코딩 (R-3) |
| 3 | 키에서 N 추출해 필터 선택 | ❌ | R-3 |
| 3 | 필터/패턴 크기 일치 검증 | ❌ | M-4 |
| 3 | 불일치 시 케이스 FAIL + 비정상 종료 방지 | ❌ | R-4 |
| 4 | expected 라벨 정규화(`+`/`x`) | ✅ | `label_normalization` |
| 4 | filter 키 라벨 정규화(`cross`/`x`) | ❌ | R-2 |
| 5 | MAC 반복문 직접 구현, 외부 라이브러리 금지 | ✅ | `json`, `time`만 사용 |
| 6 | epsilon(1e-9) 기반 동점 처리 | ⚠️ | 동작하나 3곳에 중복·상수 미분리 |
| 6.1 | Cross/X 점수 + 판정 출력 | ⚠️ | 모드 2 정상, 모드 1 헤더 모순 (M-3) |
| 6.1 | expected 대비 PASS/FAIL 출력 | ✅ | `classification_x_cross` |
| 6.2 | 크기별 ms 측정, 10회 평균 | ❌ | 단위 10^9배 오류 (M-1) |
| 6.2 | 표에 크기/평균시간/연산횟수(N²) 포함 | ⚠️ | 3×3 하드코딩, 정렬 깨짐 (R-5) |
| 6.3 | 총/통과/실패 + 실패 케이스 목록 | ❌ | R-1 |
| 6.4 | 실행 흐름 순서 준수 | ⚠️ | R-5 |

필수 18항목 중 **완전 충족 8 / 부분 5 / 미충족 5**.

---

## 5. 코드 품질 (PEP 8 · 가독성)

Codyssey 제출 기준에서 별도 감점되는 영역이다.

1. **79자 초과 라인 12곳** — 14, 18, 46, 47, 52, 59, 70, 78, 138, 146, 184, 212줄.
   특히 **184줄은 184자**로, 판정 삼항 연산이 한 줄에 3중으로 중첩돼 사실상 읽을 수 없다.
2. **docstring 전무** — 모듈 docstring도, 함수 docstring도 하나도 없다. 함수 10개 전부.
3. **따옴표 혼용** — `"data.json"`, `'X'`, `f"..."`가 파일 전체에 섞여 있다. 하나로 통일.
4. **상수 위치** — `CROSS`/`X`가 파일 중간 86~87줄에 선언됐다. 상수는 import 직후 상단에 모은다.
   `1e-9`, `10`(repeats), `"data.json"`도 매직 넘버/문자열로 흩어져 있다.
5. **불필요한 f-string** — 152~156, 158줄은 치환할 변수가 없는데 `f"..."`를 썼다.
6. **주석 스타일** — 151줄 `## point_a / repeats, ...`는 이중 해시이며 내용도 삭제된 코드 잔해다.
   38줄 `# Assuming 1 repeat for simplicity`는 실제 동작과 맞지 않는 **거짓 주석**이다.
   162~165줄의 주석 처리된 예시 표도 제거 대상.
7. **죽은 반환값** — `mac_operation`이 인자로 받은 `repeats`를 그대로 되돌려준다(39줄).
   호출부는 출력 문구에만 쓴다. 반환할 이유가 없다.
8. **숨겨진 메뉴 `T`** — 206줄 `elif choice.upper() == "T"`로 `test_mac_operation`을 호출하는데
   메뉴에 표기되지 않는다. 개발용이면 제거하거나, 남긴다면 메뉴에 노출한다.
   덧붙여 212줄 안내문 "1-3 사이의 숫자 또는 'Q'"도 실제 지원 키와 어긋난다.
9. **얕은 복사** — 67, 75줄 `f_a.copy()`는 중첩 리스트의 내부 행을 공유한다.
   지금은 읽기만 해서 문제가 없지만 관용적으로 틀린 코드다.
10. **파일 경로/인코딩** — 102줄 `open("data.json", "r")`은 **CWD 기준 상대 경로**이며 인코딩 미지정이다.
    다른 디렉터리에서 실행하면 실패하고, 기본 인코딩이 UTF-8이 아닌 환경에서 깨질 수 있다.

```python
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data.json')

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)
```

11. **출력 포맷 미세 오류** — `판정: X | expected : X`(176줄)의 콜론 앞 공백,
    `- -- size_5_1 ---`의 잘못된 구분선(예시의 `--- size_5_1 ---` 오타를 그대로 옮긴 듯),
    성능표의 탭 정렬 붕괴.

---

## 6. 잘한 점

공정하게 짚어둘 부분.

- **외부 라이브러리를 쓰지 않고** 3중 루프로 MAC을 직접 구현했다(핵심 요구 5번 충족).
- **입력 재검증 루프가 실제로 동작한다.** 개수 부족·문자 입력 모두 해당 행만 다시 받는다.
  (실측: `1 2` → 재입력, `x y z` → 재입력)
- `while True` 메뉴 루프 + `Q` 종료로 반복 실행이 가능하다.
- 판정/출력을 `classification`, `classification_x_cross`로 분리하려는 시도가 있다.
- `test_mac_operation`으로 자체 검증을 시도한 흔적이 있다(정식 테스트로 승격할 가치가 있다).

---

## 7. 수정 우선순위

| 순위 | 항목 | 위치 | 예상 난이도 |
| --- | --- | --- | --- |
| 1 | B-1 f-string 문법 오류 (실행 불가) | 112, 114, 116 | 1분 |
| 2 | M-1 ns→ms 단위 (`/1_000_000`) | 36 | 1분 |
| 3 | R-1 결과 요약(총/통과/실패 + 실패 목록) | `analyze_json` | 30분 |
| 4 | M-3 모드 1 헤더/판정 모순 | 59, 184 | 10분 |
| 5 | M-4 + R-4 크기 검증 & 케이스 단위 예외 격리 | `mac_operation`, `analyze_json` | 30분 |
| 6 | R-3 패턴 키 순회 + N 추출 | 119-149 | 20분 |
| 7 | R-2 필터 키 라벨 정규화 | 90-96, 130 | 10분 |
| 8 | R-5 3×3 실측 + 모드 1 성능표 | 158, `user_input` | 20분 |
| 9 | M-2 점수 계산/시간 측정 함수 분리 | 22-39 | 20분 |
| 10 | 5장 PEP 8 · docstring 정리 | 전체 | 30분 |

1~2번만 고쳐도 "실행되는 프로그램"이 되고, 1~8번까지 마치면 요구사항 필수 항목은 모두 충족한다.

---

## 8. 다음 단계 참고 (README 연계)

`README.md`가 현재 3줄(98바이트)이라 제출물 요구(실행 방법 + 결과 리포트 10줄 이상)를
충족하지 못한다. 위 R-1의 집계 기능을 구현하면 README 결과 리포트를 이렇게 채울 수 있다.

- 현재 `data.json` 기준 실측: **총 6건 / PASS 3 / FAIL 3**
- FAIL 3건(size_5_1, size_13_2, size_25_1)은 전부 `UNDECIDED`이며,
  Cross/X 점수 차가 각각 약 `1.1e-16`, `2.7e-15`, `1.8e-15` 수준이다.
- 즉 **"로직 오류가 아니라 부동소수점 표현 한계"** — 0.1·0.9 같은 값이 이진 부동소수점으로
  정확히 표현되지 않아 수학적으로 동일한 두 합이 미세하게 갈린 것이다.
  이것이 바로 과제가 요구하는 "데이터/스키마 문제 vs 로직 문제 vs 수치 비교 문제" 분류의
  **세 번째 유형**이며, epsilon(1e-9) 정책이 필요한 이유의 실증 사례다.
- 시간 복잡도는 M-1 수정 후 재측정한 값으로 N² 대비 비례 관계를 서술한다.
