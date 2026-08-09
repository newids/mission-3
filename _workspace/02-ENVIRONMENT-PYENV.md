# 02. 개발 환경 구축 — pyenv + 가상환경

> **현재 이 PC의 상태 (점검 결과)**
> - `pyenv` : **미설치**
> - `python` : Microsoft Store 스텁만 존재 (`--version` 이 정상 동작하지 않음) → **실사용 불가**
> - `winget`, `choco`, `git` : 사용 가능
>
> 따라서 아래 **STEP 1부터** 순서대로 진행해야 합니다.

플랫폼: **Windows 11 / PowerShell 7+**
(macOS·Linux 사용자는 맨 아래 [부록 B](#부록-b-macos--linux-용-pyenv) 참고)

---

## 전체 흐름

```text
STEP 1  pyenv-win 설치
STEP 2  터미널 재시작 → pyenv 동작 확인
STEP 3  Python 3.12.x 설치 (pyenv install)
STEP 4  프로젝트 로컬 버전 고정 (pyenv local)
STEP 5  가상환경 생성 (python -m venv)
STEP 6  가상환경 활성화 + 검증
STEP 7  .gitignore 정리
```

---

## STEP 1. pyenv-win 설치

**방법 A — 공식 설치 스크립트 (권장)**

```powershell
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "$env:TEMP\install-pyenv-win.ps1"
& "$env:TEMP\install-pyenv-win.ps1"
```

> `실행 정책(ExecutionPolicy)` 오류가 나면 먼저 아래를 1회 실행합니다.
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

**방법 B — Chocolatey (관리자 권한 PowerShell 필요)**

```powershell
choco install pyenv-win -y
```

**방법 C — winget**

```powershell
winget install --id pyenv-win.pyenv-win -e
```

### Microsoft Store 스텁 비활성화 (중요)

Windows의 `python.exe` 스텁이 pyenv보다 먼저 잡히면 계속 Store 앱이 열립니다.
`설정 → 앱 → 고급 앱 설정 → 앱 실행 별칭` 에서 **python.exe / python3.exe 를 끕니다.**

---

## STEP 2. 터미널 재시작 후 확인

PowerShell 창을 **완전히 닫고 새로 연 뒤**:

```powershell
pyenv --version
```

버전이 출력되지 않으면 PATH 환경변수를 확인합니다.

```powershell
$env:PYENV
$env:Path -split ';' | Select-String pyenv
```

`~\.pyenv\pyenv-win\bin` 과 `~\.pyenv\pyenv-win\shims` 가 PATH에 있어야 합니다.

---

## STEP 3. Python 설치

```powershell
# 설치 가능한 3.12 목록 확인
pyenv install --list | Select-String "^\s*3\.12"

# 설치 (미션 요구: 3.8 이상 / 권장: 3.12.x)
pyenv install 3.12.7

# 설치된 버전 확인
pyenv versions
```

> 미션 최소 요구는 **Python 3.8 이상**입니다. 3.12.x 를 권장합니다.

---

## STEP 4. 프로젝트 로컬 버전 고정

```powershell
cd C:\Users\user\Codyssey\mission-3
pyenv local 3.12.7
```

→ 프로젝트 루트에 `.python-version` 파일이 생성되고, 이 폴더에서는 항상 3.12.7이 사용됩니다.

```powershell
pyenv version      # 3.12.7 (set by ...\.python-version)
python --version   # Python 3.12.7
```

---

## STEP 5. 가상환경 생성

```powershell
cd C:\Users\user\Codyssey\mission-3
python -m venv .venv
```

> `.venv` 는 pyenv가 고정한 3.12.7 인터프리터를 그대로 복제합니다.
> (pyenv-virtualenv 는 Windows에서 지원되지 않으므로 표준 `venv` 를 사용합니다.)

---

## STEP 6. 활성화 및 검증

```powershell
# PowerShell
.\.venv\Scripts\Activate.ps1

# (Git Bash 사용 시)
source .venv/Scripts/activate
```

프롬프트 앞에 `(.venv)` 가 붙으면 성공입니다. 아래로 최종 검증합니다.

```powershell
python --version                       # Python 3.12.7
python -c "import sys; print(sys.executable)"   # ...\mission-3\.venv\Scripts\python.exe
pip list                               # pip / setuptools 정도만 있어야 정상
```

> **외부 라이브러리 설치 금지** — `pip install numpy` 같은 건 절대 하지 않습니다.
> `pip list` 가 거의 비어 있는 것이 정상이며, 그래서 이 미션은 `requirements.txt` 가 필요 없습니다.

비활성화는 `deactivate` 입니다.

---

## STEP 7. .gitignore 확인

프로젝트 루트 `.gitignore` 에 아래 항목이 포함되어 있는지 확인합니다 (없으면 추가).

```gitignore
.venv/
__pycache__/
*.pyc
```

`.python-version` 은 **커밋하는 것을 권장**합니다 (재현성 확보).

---

## 실행 방법 (구현 후)

```powershell
# 가상환경 활성화 상태에서
cd C:\Users\user\Codyssey\mission-3
python main.py
```

`data.json` 은 **프로젝트 루트(`main.py` 와 같은 위치)** 에 있습니다.

---

## 부록 A. 자주 나는 오류

| 증상 | 원인 | 해결 |
| --- | --- | --- |
| `pyenv : 용어를 인식할 수 없습니다` | PATH 미반영 | 터미널 완전 재시작 / PATH 확인 |
| `python` 실행 시 Microsoft Store가 열림 | Store 앱 실행 별칭 | 설정 → 앱 실행 별칭 → python.exe 끄기 |
| `Activate.ps1 ... 실행할 수 없습니다` | 실행 정책 | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `pyenv install` 이 매우 느림/실패 | 미러 다운로드 문제 | `pyenv update` 후 재시도 |
| 가상환경인데 `sys.executable` 이 다른 경로 | 활성화 안 됨 | `Activate.ps1` 재실행 |

## 부록 B. macOS / Linux 용 pyenv

```bash
# 설치 (macOS)
brew install pyenv

# 셸 설정 (~/.zshrc 또는 ~/.bashrc)
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# 이후 동일
pyenv install 3.12.7
cd mission-3 && pyenv local 3.12.7
python -m venv .venv && source .venv/bin/activate
```

---

## 다음 단계

→ [03-REQUIREMENTS-SPEC.md](03-REQUIREMENTS-SPEC.md)
