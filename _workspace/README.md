# Mission 3 작업 문서 (_workspace)

> `docs/MISSION-3.md` 원문을 **수행 순서대로 / 빠짐없이** 재정리한 작업용 문서 모음입니다.
> 이 디렉터리는 **작업용**이며, 최종 제출물은 프로젝트 루트의 `main.py` 와 `README.md` 입니다.

## 문서 지도

| 순서 | 파일 | 내용 | 언제 읽나 |
| --- | --- | --- | --- |
| 1 | [01-MISSION-OVERVIEW.md](01-MISSION-OVERVIEW.md) | 미션 배경, MAC 연산 원리, 최종 결과물 정의, 학습 목표 | 시작 전 1회 |
| 2 | [02-ENVIRONMENT-PYENV.md](02-ENVIRONMENT-PYENV.md) | pyenv-win 설치 → Python 설치 → 가상환경(venv) 생성 → 실행 | 코딩 전 (환경 구축) |
| 3 | [03-REQUIREMENTS-SPEC.md](03-REQUIREMENTS-SPEC.md) | 기능 요구사항 전체 + `data.json` 스키마 + 라벨 정규화 규칙 (체크리스트) | 설계/구현 내내 |
| 4 | [04-IMPLEMENTATION-PLAN.md](04-IMPLEMENTATION-PLAN.md) | 함수 단위 구현 설계, 실행 흐름, 출력 포맷, 구현 순서 | 구현 중 |
| 5 | [05-VERIFICATION.md](05-VERIFICATION.md) | 자가 검증 시나리오 + `data.json` 기대 결과 정답표 | 구현 후 검증 |
| 6 | [06-SUBMISSION-README-TEMPLATE.md](06-SUBMISSION-README-TEMPLATE.md) | 제출용 `README.md` 작성 템플릿 (빈칸 채우기) | 마무리 |
| 7 | [07-FINAL-CHECKLIST.md](07-FINAL-CHECKLIST.md) | 제출 직전 최종 점검표 (이것만 통과하면 완료) | 제출 직전 |

## 한 줄 요약

3×3 ~ 25×25 크기의 **패턴(입력)** 과 **필터(기준)** 를 곱해서 더하는 **MAC 연산**을
외부 라이브러리 없이 순수 Python 반복문으로 구현하고,
`Cross` / `X` 를 판정하며 크기별 연산 시간을 측정해 **O(N²)** 를 증명하는
**Mini NPU 시뮬레이터** 콘솔 애플리케이션을 만든다.

## 진행 순서 (권장)

```text
[환경]  02 문서 → pyenv 설치 → venv 생성 → 활성화
   ↓
[이해]  01 문서 → MAC 원리 / 결과물 정의 파악
   ↓
[설계]  03 문서 → 요구사항 체크리스트 확보
   ↓
[구현]  04 문서 → main.py 를 8단계 순서대로 작성
   ↓
[검증]  05 문서 → 모드1 / 모드2 / 오류입력 시나리오 실행, 정답표 대조
   ↓
[문서]  06 문서 → 제출용 README.md 작성 (결과 리포트 10줄 이상)
   ↓
[제출]  07 문서 → 최종 체크리스트 전 항목 통과 확인
```

## 절대 놓치면 안 되는 5가지

1. **NumPy 등 외부 라이브러리 금지** — MAC은 반드시 `for` 반복문으로 직접 구현
2. **라벨 정규화 필수** — `'+' → Cross`, `'x' → X`, 필터 키 `cross → Cross` 로 표준화
3. **epsilon 동점 처리** — `abs(a - b) < 1e-9` 이면 `UNDECIDED`
4. **프로그램이 죽으면 안 됨** — 스키마/크기 불일치는 케이스 단위 `FAIL` 로 처리
5. **README 결과 리포트 10줄 이상** — 실패 원인 분석 + O(N²) 근거 서술
