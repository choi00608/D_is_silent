# AI TRPG 서비스: I Know

## 1. 프로젝트 개요

"I Know"는 플레이어 한 명이 AI 게임 마스터(GM)와 함께 롤플레잉 게임(TRPG)을 즐길 수 있도록 하는 웹 기반 서비스입니다. 사용자의 결정이 스토리를 만들어나가는 실시간 채팅 기반의 게임 플레이를 목표로 합니다.

## 2. 현재까지의 핵심 구현 내용

### 2.1. 백엔드 (Django)
- **플레이어 기반 세션 관리:** 익명 세션이 아닌, 플레이어 이름(`Player` 모델)을 기반으로 시나리오별 게임 세션(`GameSession` 모델)을 생성하고, 기존 게임을 이어서 할 수 있는 로직을 구현했습니다.
- **데이터베이스 모델링:** 게임의 핵심 요소인 `Player`, `GameScenario`, `GameSession`, `GameLog` 모델을 정의하고, `on_delete=models.CASCADE`를 통해 데이터 무결성을 확보했습니다.
- **AI 연동 (1차):** Groq API를 사용하여 LLM을 연동했습니다. `send_message` 뷰에서 아래와 같은 형식으로 AI에 요청을 보내고 응답을 받아 `GameLog`에 저장합니다.
  - `[시스템 프롬프트] + [게임 룰] + [대화 기록]`
- **Admin 커스터마이징:** 관리자 페이지에서 `GameLog`의 전체 메시지를 보거나, 펼치기/접기 기능을 통해 확인할 수 있도록 개선했습니다.
- **AI 응답 JSON 형식 강제 및 파싱:** AI의 응답을 정해진 JSON 형식으로 받도록 `prompt_template.json`을 강화하고, `trpg/views.py`에서 AI의 JSON 응답을 파싱하여 `description`, `is_major_decision`, `next_action_options`를 추출하도록 로직을 추가했습니다. AI가 Markdown 코드 블록으로 응답을 감싸는 경우를 대비하여 전처리 로직도 추가했습니다.
- **AI 응답 로깅:** AI의 전처리된 JSON 응답을 `conversation_log.json` 파일에 `ai_log` 키 아래에 JSON 객체 형태로 기록하도록 구현했습니다.

### 2.2. 프론트엔드
- **TypeScript 도입:** `game_session.html`의 채팅 로직을 `trpg/static/ts/game_session.ts`로 분리하여 코드의 안정성과 유지보수성을 향상시켰습니다.
- **빌드 환경:** `npm`을 통해 TypeScript 컴파일러를 설치하고, `tsconfig.json`을 구성하여 `.ts` 파일을 `.js`로 컴파일하는 환경을 구축했습니다. `npx tsc --watch`를 통해 자동 컴파일이 가능합니다.
- **AI 선택지 버튼 렌더링:** `trpg/static/ts/game_session.ts`와 `trpg/templates/trpg/game_session.html`을 수정하여 AI가 `next_action_options`를 제공할 경우, 이를 채팅창 하단에 선택 가능한 버튼 형태로 렌더링하도록 구현했습니다.

### 2.3. 프롬프트 엔지니어링 (1차)
- **프롬프트 외부화:** AI의 역할(`prompt_template.json`)과 게임 규칙(`game_rules.json`)을 별도의 JSON 파일로 분리하여, Python 코드를 수정하지 않고도 AI의 행동을 변경할 수 있는 기반을 마련했습니다.
- **기본 게임 룰 정의:** 사이버펑크 시나리오에 맞춰 '무력/솜씨/통찰/매력' 4가지 능력치와 '강한 성공/약한 성공/실패' 3단계 판정 결과를 기반으로 하는 게임 룰을 정의하고 AI에 주입했습니다.
- **JSON 출력 형식 명시:** `prompt_template.json`에 AI가 따라야 할 JSON 출력 형식, 각 필드의 상세 설명 및 제약 조건, 그리고 Markdown 코드 블록 사용 금지 지시를 명확히 추가했습니다.

## 3. 기술 스택

- **백엔드:** Django (Python)
- **프론트엔드:** HTML, CSS, TypeScript
- **데이터베이스:** SQLite
- **AI:** Groq API (LLM)
- **빌드:** Node.js, npm, TypeScript Compiler (tsc)

## 4. 다음 목표

- **플레이어 상태 업데이트 로직 구현:** AI 응답의 `player_status_update` 필드를 파싱하여 실제 플레이어 모델(인벤토리, 체력 등)에 반영하는 로직을 `trpg/views.py`에 추가해야 합니다.
- **AI 응답 재시도 로직:** AI가 유효하지 않은 JSON을 반환했을 때, 자동으로 재시도를 요청하는 로직을 `trpg/views.py`에 구현하여 안정성을 높여야 합니다.
- **게임 규칙 동적 로딩:** 현재 `GAME_RULES`가 서버 시작 시 로드되는데, 시나리오별로 다른 규칙을 동적으로 로드할 수 있도록 개선해야 합니다.



## 6. Gemini CLI 사용 가이드

이 프로젝트와 함께 Gemini CLI를 효과적으로 사용하기 위한 가이드입니다.

### 6.1. 프로젝트 개요 및 주요 파일

*   **프로젝트 루트:** `C:/Users/choi0/box/d_is_silent/i_know/`
*   **주요 백엔드 로직:** `trpg/views.py`
*   **AI 프롬프트 정의:** `prompt_template.json`, `game_rules.json`
*   **프론트엔드 TypeScript:** `trpg/static/ts/game_session.ts`
*   **프론트엔드 HTML:** `trpg/templates/trpg/game_session.html`
*   **AI 응답 로그:** `conversation_log.json` (프로젝트 루트에 위치)

### 6.2. 개발 환경 설정 및 실행

1.  **Python 가상 환경 활성화:**
    ```bash
    # 예시: venv를 사용했다면
    .\venv\Scripts\activate
    ```
2.  **Django 개발 서버 실행:**
    ```bash
    python manage.py runserver
    ```
    (서버는 기본적으로 `http://127.0.0.1:8000/`에서 실행됩니다.)
3.  **TypeScript 컴파일:**
    프론트엔드 TypeScript 파일을 변경한 후에는 반드시 JavaScript로 컴파일해야 합니다.
    ```bash
    npx tsc
    ```
    또는 변경 사항을 자동으로 감지하여 컴파일하려면:
    ```bash
    npx tsc --watch
    ```

### 6.3. 디버깅 및 로그 확인

*   **AI 응답 로그 확인:** AI가 생성한 원본 JSON 응답은 `conversation_log.json` 파일에 기록됩니다. 이 파일을 열어 AI의 응답 내용을 직접 확인할 수 있습니다.
*   **서버 로그 확인:** Django 개발 서버를 실행하는 터미널에서 백엔드 오류 메시지나 `print()` 문으로 출력된 디버그 메시지를 확인할 수 있습니다.

### 6.4. Gemini에게 작업 요청 시 유의사항

*   **명확한 목표 제시:** "AI 응답의 `player_status_update` 로직을 구현해줘"와 같이 구체적인 목표를 제시해주세요.
*   **관련 파일 언급:** 작업할 파일이나 관련 파일(예: `trpg/views.py`, `trpg/models.py`)을 함께 언급해주시면 좋습니다.
*   **기존 컨벤션 준수:** 프로젝트의 기존 코드 스타일, 명명 규칙, 아키텍처를 유지하도록 요청해주세요.
*   **테스트 요청:** 변경사항 적용 후 `npx tsc` 또는 `python manage.py test`와 같은 테스트/빌드 명령어를 실행하여 검증해달라고 요청할 수 있습니다.

---

## 관리자 계정

- **ID:** admin
- **PW:** abc0100608

---

## 최근 주요 변경사항 (2025-07-24)

**목표:** 대화가 길어질수록 AI 응답이 느려지고 토큰 제한에 도달하는 문제를 해결하고, 게임의 핵심 스토리가 개발자의 의도대로 안정적으로 진행되도록 시스템을 개선했습니다.

**핵심 변경점: "키워드 기반 하이브리드 시스템" 도입**

1.  **분기점 제어 (`major_plot_points.json`):**
    -   게임의 핵심 분기점, 각 분기점을 감지하기 위한 `keywords`, 분기점에서 주어지는 고정 `choices`, 그리고 획득할 아이템(`gives_items`) 등을 정의하는 `major_plot_points.json` 파일을 추가했습니다.
    -   이를 통해 AI의 창의성에만 의존하지 않고, 시스템이 직접 스토리의 흐름을 제어할 수 있게 되었습니다.

2.  **효율적인 프롬프트 구성 (`trpg/views.py`):
    -   더 이상 전체 대화 기록을 AI에게 보내지 않습니다.
    -   대신 **[현재 분기점 ID] + [플레이어 상태] + [최근 4개 대화]** 만을 조합하여 매번 간결하고 효율적인 프롬프트를 실시간으로 생성합니다. 이로 인해 토큰 사용량이 크게 줄고 응답 속도가 향상되었습니다.

3.  **상태 추적 모델링 (`trpg/models.py`):
    -   `GameSession` 모델에 플레이어의 현재 분기점 위치를 저장하는 `current_plot_point_id` 필드와 인벤토리 등을 관리하는 `player_state` (JSON) 필드를 추가했습니다.
    -   이를 통해 플레이어의 진행 상황을 영구적으로 추적할 수 있습니다.

4.  **아이템 획득 로직 구현 (`trpg/views.py`):
    -   AI의 응답에서 분기점 키워드가 감지되었을 때, 해당 분기점의 `gives_items`에 명시된 아이템이 `GameSession`의 `player_state` 필드에 있는 `inventory` 배열에 자동으로 추가되는 로직을 구현했습니다. 중복 아이템은 자동으로 제거됩니다.

5.  **프론트엔드 연동 (`trpg/static/ts/game_session.ts`):
    -   백엔드에서 받은 분기점의 고정 선택지(`choices`)를 올바르게 처리하도록 프론트엔드 로직을 수정했습니다.
    -   사용자가 선택지를 클릭하면, 해당 선택지의 `next_point_id`와 `is_major` 같은 메타데이터를 다시 백엔드로 전송하여 상태를 업데이트합니다.

6.  **전체적인 스타일 통일:
    -   `main.css` 파일을 생성하여 공통 스타일(다크모드 테마, 폰트, 버튼 모양 등)을 분리했습니다.
    -   `game_session.html`, `log_list.html`, `scenario_list.html`에 공통 스타일을 적용하여 일관된 사용자 경험을 제공합니다.

## 다음 작업 목표 및 초기 프롬프트 가이드

**현재 시스템의 최종 목표:** 안정적으로 주요 스토리를 따라가면서도, 분기점 사이에서는 AI가 자유롭게 상호작용하는 하이브리드 TRPG 시스템 완성.

**다음 작업 지시 예시 (Gemini에게):**

> "안녕하세요. `README.md`의 '최근 주요 변경사항'을 확인했습니다. 이제 다음 목표인 'AI 응답 재시도 로직'을 구현해 보겠습니다. `trpg/views.py`의 `send_message` 함수에서, AI의 응답이 유효하지 않은 JSON이거나 비어있는 등 예외 상황이 발생했을 때, 동일한 요청을 한 번 더 보내는 재시도 로직을 추가해주세요. 재시도 후에도 실패하면 현재와 같이 오류 메시지를 반환하도록 만들어야 합니다."