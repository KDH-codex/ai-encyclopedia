# 🌐 AI 백과사전 (AI 모델 · MCP 지식 그래프)

> **개인용 AI 모델 및 MCP(Model Context Protocol) 생태계 지식 그래프 백과사전**  
> 복잡한 AI 모델들을 **추론 에포트(Reasoning Effort)** 및 **용도** 단위로 분류하고, 노드 네트워크 그래프와 상세 카드로 한눈에 탐색하며, Google Gemini API로 최신 모델 후보를 주기적으로 수집·관리하는 시스템입니다.

---

## 📌 주요 특징

1. **인터랙티브 지식 그래프 (D3.js Force Simulation)**:
   - 개발사, AI 모델, 추론 에포트, MCP 서버, 핵심 개념이 서로 어떻게 연결되어 있는지 한눈에 시각화
   - 노드 드래그, 줌/팬(Zoom & Pan), 마우스 호버 시 이웃 노드 강조 하이라이트 지원
2. **상세 카드 슬라이드 패널**:
   - 노드를 클릭하면 우측에서 슬라이드로 열리며 한 줄 요약, 스펙, 장단점, 가격, 출처 링크 확인 가능
   - 연결된 다른 노드로 즉시 이동할 수 있는 바로가기 탐색 버튼 제공
3. **실시간 필터 및 검색 & 모델 비교**:
   - 회사 / 모델 / 에포트 / MCP / 개념 카테고리별 원클릭 필터링
   - 실시간 키워드(이름, 태그, 요약) 검색
   - 대표 모델들의 스펙(추론 강도, 컨텍스트 창, 가격 등)을 나란히 비교하는 비교 모달 탑재
4. **Gemini API 연동 자동 후보 수집 & 사용자 승인 시스템**:
   - `search_candidates.py`: 최신 AI 모델 및 MCP 출시 정보를 Gemini API(또는 테스트용 모의 데이터)로 자동 탐색하여 후보군에 저장
   - `merge_candidates.py`: 수집된 후보군을 사람이 직접 눈으로 확인하고 `y(승인)`를 누를 때만 정식 데이터로 병합
5. **Gemini 노트북 (NotebookLM) 연동 지원**:
   - `export_for_notebook.py`: 전체 지식 베이스를 NotebookLM에 올리기 좋은 단일 마크다운 문서로 즉시 추출

---

## 📂 프로젝트 폴더 구조

```text
ai-encyclopedia/
├── data/
│   ├── nodes.json          # 정식 등록된 모든 노드 (회사, 모델, 에포트, MCP, 개념)
│   ├── edges.json          # 노드 간 연결 관계 (소속, 후속, 에포트제공, 도구호환 등)
│   └── candidates.json     # 새로 발견되어 사람의 승인을 기다리는 후보 목록
├── web/
│   └── index.html          # 인터랙티브 지식 그래프 웹 뷰어 (단일 완성형 HTML)
├── scripts/
│   ├── search_candidates.py # 최신 모델/MCP 신작 자동 검색 스크립트
│   ├── merge_candidates.py  # 대화형 후보 검토 및 본 데이터 안전 병합 도구
│   └── export_for_notebook.py# Gemini 노트북/NotebookLM 질의용 마크다운 요약 추출기
├── ai_encyclopedia_knowledge_base.md # NotebookLM에 바로 업로드 가능한 지식 파일
├── .env.example            # Gemini API 키 설정 템플릿
├── .gitignore              # API 키 및 보안 파일 보호 설정
└── README.md               # 본 사용자 가이드북
```

---

## 🚀 빠른 시작 가이드

### 1단계: 웹 뷰어 실행하기 (아주 간단합니다!)
- **방법 1 (가장 간단한 방법)**:  
  `web/index.html` 파일을 마우스로 **더블 클릭**하면 기본 웹 브라우저(크롬, 엣지 등)에서 즉시 열립니다!  
  *(CORS 보안 제약 없는 내장 Fallback 데이터가 포함되어 있어 즉시 작동합니다.)*
- **방법 2 (로컬 웹 서버로 열기 - 추천)**:  
  터미널(PowerShell 또는 명령 프롬프트)에서 아래 명령어를 실행하면 외부 JSON 파일을 실시간 동기화하여 열 수 있습니다:
  ```powershell
  cd c:\Users\dongh\ai-encyclopedia
  py -m http.server 8000
  ```
  브라우저 주소창에 `http://localhost:8000/web/` 을 입력하고 접속하세요.

---

### 2단계: 신규 모델 및 MCP 후보 자동 탐색하기
새로운 모델이 출시되었는지 확인하고 후보 목록에 담고 싶을 때 실행합니다:

```powershell
cd c:\Users\dongh\ai-encyclopedia
py scripts/search_candidates.py
```
- **Gemini API 키가 없을 때**: 자동으로 안전한 **시뮬레이션 모의 데이터(Mock Data)** 모드로 동작하여 시스템을 테스트해 볼 수 있습니다.
- **실제 Gemini API를 쓰고 싶을 때**: `.env.example` 파일을 복사하여 `.env`로 이름을 바꾼 후, [Google AI Studio](https://aistudio.google.com/app/apikey)에서 무료로 발급받은 API 키를 적어주시면 됩니다.

---

### 3단계: 후보 검토 및 본 데이터로 승인 병합하기
수집된 후보 중 마음에 드는 항목을 정식 백과사전으로 등록합니다:

```powershell
py scripts/merge_candidates.py
```
- 터미널에 후보 모델의 이름, 스펙, 요약, 출처가 하나씩 표시됩니다.
- `y`: 승인하여 정식 데이터(`nodes.json`, `edges.json`)에 즉시 추가
- `n`: 기각하고 후보 목록에서 삭제
- `s`: 보류하고 나중에 다시 검토

승인이 끝나면 브라우저(`web/index.html`)를 새로고침(F5)하는 즉시 새로운 노드와 연결선이 나타납니다!

---

### 4단계: Gemini 노트북 (NotebookLM)에서 질의응답하기
백과사전 데이터를 바탕으로 AI에게 질의응답을 받고 싶을 때:

```powershell
py scripts/export_for_notebook.py
```
- 프로젝트 루트에 `ai_encyclopedia_knowledge_base.md` 파일이 생성됩니다.
- [Google NotebookLM](https://notebooklm.google.com)에 접속하여 새 노트를 만들고, 이 마크다운 파일을 소스로 업로드하세요.
- *"이 중에서 코딩에 가장 가성비가 좋은 모델은 뭐야?"*, *"MCP가 지원되는 모델은 어떤 것들이 있어?"* 와 같이 자유롭게 질문할 수 있습니다!

---

## 🎨 노드 색상 구분 안내

| 분류 | 색상 | 설명 |
| :--- | :--- | :--- |
| **🏢 회사 (Company)** | 슬레이트 그레이 (`#64748b`) | OpenAI, Anthropic, Google, Meta 등 AI 연구·개발사 |
| **🧠 모델 (Model)** | 인디고 / 보라 (`#818cf8`) | Claude 3.7, GPT-4.5, Gemini 2.5, o3-mini 등 |
| **⚡ 에포트 (Effort)** | 앰버 / 주황 (`#f59e0b`) | Low / Medium / High / Max Thinking 등 추론 강도 단계 |
| **🔌 MCP 서버 (MCP)** | 에메랄드 그린 (`#10b981`) | Filesystem, GitHub, Brave Search 등 도구 프로토콜 |
| **💡 핵심 개념 (Concept)**| 청록 / 사이언 (`#06b6d4`) | MCP 표준 규약, 추론 예산(CoT), 문맥 창 등 |

---

## 🔒 보안 및 개인정보 보호 안내
- `.env` 파일에 저장되는 API 키는 절대로 GitHub 저장소나 외부에 노출되지 않도록 `.gitignore`에 기본 등록되어 있습니다.
- 모든 데이터는 개인 PC 로컬에 안전하게 보관됩니다.
