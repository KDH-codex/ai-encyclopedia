# -*- coding: utf-8 -*-
"""
=============================================================================
[AI 백과사전] 신규 모델 및 MCP 서버 후보 자동 탐색 스크립트 (search_candidates.py)
=============================================================================
이 스크립트는 Google Gemini API를 활용하여 최근 출시되거나 업데이트된
새로운 AI 모델 및 대중적인 MCP 서버를 검색하고, 그 결과를 'candidates.json'에
'승인 대기(pending_approval)' 상태로 안전하게 수집합니다.

[기획서 핵심 원칙]
- 자동 추가가 아니라 "후보 목록 수집 -> 사람이 승인" 흐름을 준수합니다.
- 각 후보 항목에는 반드시 출처(source_url)와 발견 일자를 기록합니다.
=============================================================================
"""

import os
import sys
import io
import json
import urllib.request
import urllib.error
from datetime import datetime

# Windows 콘솔 환경(cp949)에서 한글 및 이모지 출력 시 인코딩 오류가 발생하지 않도록 UTF-8 설정
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding="utf-8", errors="replace")
    except Exception:
        pass

# 파일 경로 정의 (프로젝트 기준)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
CANDIDATES_FILE = os.path.join(DATA_DIR, "candidates.json")
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")


def load_env():
    """
    .env 파일에서 환경변수(GEMINI_API_KEY)를 읽어와 os.environ에 등록합니다.
    외부 라이브러리(python-dotenv 등) 설치 없이도 순수 파이썬으로 동작하도록 구현되었습니다.
    """
    if os.path.exists(ENV_FILE):
        try:
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # 주석이나 빈 줄은 무시
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, val = line.split("=", 1)
                        os.environ[key.strip()] = val.strip().strip('"').strip("'")
        except Exception as e:
            print(f"[경고] .env 파일 읽기 중 오류 발생: {e}")


def load_candidates():
    """기존에 수집되어 대기 중인 후보 목록을 불러옵니다."""
    if not os.path.exists(CANDIDATES_FILE):
        return []
    try:
        with open(CANDIDATES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[오류] candidates.json 읽기 실패: {e}")
        return []


def save_candidates(candidates):
    """업데이트된 후보 목록을 candidates.json에 저장합니다."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CANDIDATES_FILE, "w", encoding="utf-8") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)
    print(f"✅ 총 {len(candidates)}개의 후보 목록이 안전하게 저장되었습니다: {CANDIDATES_FILE}")


def query_gemini_api(api_key):
    """
    Gemini API를 직접 호출하여 최신 AI 모델 및 MCP 출시 정보를 검색하고 정형화된 JSON으로 받습니다.
    외부 라이브러리 의존성 없이 파이썬 내장 urllib 모듈을 사용하여 안정적으로 호출합니다.
    """
    print("\n🔍 Google Gemini API에 최신 AI 모델 및 MCP 출시 동향을 질의하고 있습니다...")
    
    # Gemini 2.5 Flash 모델 엔드포인트 호출
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    system_instruction = (
        "당신은 AI 백과사전의 데이터 수집가입니다. "
        "최근 3개월 이내에 발표되거나 업데이트된 주요 AI 모델(예: Claude, OpenAI o시리즈, Gemini, Kimi, Qwen 등) 또는 "
        "새롭게 주목받는 유용한 MCP(Model Context Protocol) 서버 1~2개를 찾아 아래 JSON 배열 형식으로만 응답해주세요. "
        "응답은 반드시 유효한 JSON 형식이어야 하며 마크다운 코드블록(```json)을 사용해도 됩니다."
    )
    
    prompt = """
다음 형식의 JSON 배열 구조로 최근 신규 모델이나 MCP 서버 1~2개를 작성해주세요:
[
  {
    "id": "고유id(예: candidate-model-xxx 또는 candidate-mcp-xxx)",
    "name": "공식 명칭",
    "type": "model 또는 mcp",
    "company": "개발사(모델인 경우)",
    "release_date": "YYYY-MM-DD",
    "summary": "한국어 한 줄 요약",
    "strengths": ["강점1", "강점2"],
    "weaknesses": ["약점1"],
    "pricing": "가격 정책 정보",
    "context_window": "컨텍스트 크기",
    "tags": ["태그1", "태그2"],
    "source_url": "공식 발표나 뉴스 URL",
    "discovered_at": "YYYY-MM-DD",
    "status": "pending_approval"
  }
]
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": system_instruction + "\n\n" + prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            content_text = result["candidates"][0]["content"]["parts"][0]["text"]
            
            # JSON 텍스트 파싱
            clean_text = content_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            
            parsed_data = json.loads(clean_text.strip())
            return parsed_data
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"❌ Gemini API 호출 오류 (HTTP {e.code}): {error_body}")
        return None
    except Exception as e:
        print(f"❌ 요청 처리 중 예외 발생: {e}")
        return None


def get_mock_candidates():
    """
    API 키가 없거나 테스트용으로 빠르게 동작을 확인하고자 할 때 사용하는 모의(Mock) 후보 데이터 생성 함수입니다.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    return [
      {
        "id": f"candidate-deepseek-r1-{int(datetime.now().timestamp())}",
        "name": "DeepSeek-R1 (사고 특화 모델)",
        "type": "model",
        "company": "DeepSeek",
        "release_date": "2025-01-20",
        "summary": "대규모 순수 강화학습(RL)을 통해 오픈소스로 완전 공개된 혁신적 추론 모델",
        "strengths": ["수학 및 코딩에서 최고 수준 추론 능력", "오픈소스 가중치 공개로 로컬 실행 가능"],
        "weaknesses": ["검열 및 정책에 따른 편차", "서버 대기열 병목"],
        "pricing": "입력 $0.55 / 출력 $2.19 (1M 토큰당)",
        "context_window": "64k 토큰",
        "tags": ["오픈소스추론", "강화학습", "수학코딩"],
        "source_url": "https://github.com/deepseek-ai/DeepSeek-R1",
        "discovered_at": today_str,
        "status": "pending_approval"
      },
      {
        "id": f"candidate-mcp-slack-{int(datetime.now().timestamp())}",
        "name": "Slack MCP Server",
        "type": "mcp",
        "summary": "AI가 사내 슬랙 채널의 메시지를 읽고 답장을 남길 수 있는 커뮤니케이션 도구",
        "protocol": "Model Context Protocol",
        "maintainer": "커뮤니티",
        "typical_use": "팀 협업 채널 모니터링 및 알림 자동 전송",
        "tags": ["협업툴", "메시징", "자동화"],
        "source_url": "https://github.com/modelcontextprotocol/servers",
        "discovered_at": today_str,
        "status": "pending_approval"
      }
    ]


def main():
    print("=" * 65)
    print("🤖 [AI 백과사전] 신규 모델 및 MCP 서버 후보 자동 탐색 시작")
    print("=" * 65)

    # 1. 환경변수 불러오기
    load_env()
    api_key = os.environ.get("GEMINI_API_KEY")

    candidates = load_candidates()
    print(f"현재 대기 중인 기존 후보 수: {len(candidates)}개")

    new_items = None

    # 2. API 키 유무에 따른 분기 처리
    if not api_key or api_key == "your_gemini_api_key_here":
        print("\n[안내] 등록된 GEMINI_API_KEY가 없습니다.")
        print(".env 파일에 유효한 API 키를 입력하시면 실제 Gemini 실시간 검색을 수행합니다.")
        print("💡 지금은 기능 테스트를 위해 [시뮬레이션 모의 데이터(Mock)]로 후보를 생성합니다.")
        new_items = get_mock_candidates()
    else:
        print("\n🔑 GEMINI_API_KEY가 확인되었습니다. 공식 API로 탐색을 진행합니다.")
        new_items = query_gemini_api(api_key)
        if not new_items:
            print("⚠️ API 호출에 실패하여 시뮬레이션 모의 데이터로 대체합니다.")
            new_items = get_mock_candidates()

    # 3. 중복 방지 및 후보 목록에 추가
    if new_items:
        added_count = 0
        existing_ids = {c.get("id") for c in candidates}
        existing_names = {c.get("name") for c in candidates}

        for item in new_items:
            if item.get("id") not in existing_ids and item.get("name") not in existing_names:
                candidates.append(item)
                added_count += 1
                print(f"  ➕ 새로운 후보 발견: [{item.get('type')}] {item.get('name')}")
            else:
                print(f"  ⏩ 이미 존재하는 항목 스킵: {item.get('name')}")

        if added_count > 0:
            save_candidates(candidates)
            print(f"\n🎉 성공적으로 {added_count}개의 새로운 후보를 candidates.json에 추가했습니다!")
            print("👉 다음 단계: 'py scripts/merge_candidates.py' 를 실행하여 후보를 검토하고 본 데이터로 승인하세요.")
        else:
            print("\n새롭게 추가된 중복 없는 후보 항목이 없습니다.")

    print("\n" + "=" * 65)
    print("작업이 완료되었습니다.")
    print("=" * 65)


if __name__ == "__main__":
    main()
