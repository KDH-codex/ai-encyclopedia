# -*- coding: utf-8 -*-
"""
=============================================================================
[AI 백과사전] Gemini 노트북 / LLM 질의용 지식 문서 내보내기 (export_for_notebook.py)
=============================================================================
이 스크립트는 'nodes.json'과 'edges.json'의 모든 정형 데이터를
NotebookLM(제미나이 노트북)이나 ChatGPT, Claude 등에 소스 문서로
업로드하기 가장 적합한 고품질 마크다운(Markdown) 백과사전 문서로 변환합니다.

[활용 방법]
1. 'py scripts/export_for_notebook.py' 실행
2. 생성된 'ai_encyclopedia_knowledge_base.md' 파일을 NotebookLM에 업로드
3. "이 중 코딩에 가장 가성비가 좋은 모델은?", "MCP 서버 설치 방법은?" 등 자연어로 질의응답!
=============================================================================
"""

import os
import sys
import io
import json
from datetime import datetime

# Windows 콘솔 환경(cp949)에서 한글 및 이모지 출력 시 인코딩 오류가 발생하지 않도록 UTF-8 설정
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

NODES_FILE = os.path.join(DATA_DIR, "nodes.json")
EDGES_FILE = os.path.join(DATA_DIR, "edges.json")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "ai_encyclopedia_knowledge_base.md")


def load_json(filepath):
    """지정된 JSON 파일을 안전하게 읽어옵니다."""
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print("=" * 65)
    print("📖 [AI 백과사전] Gemini 노트북용 지식 문서 내보내기 시작")
    print("=" * 65)

    nodes = load_json(NODES_FILE)
    edges = load_json(EDGES_FILE)

    if not nodes:
        print("[오류] nodes.json 파일에 데이터가 없습니다.")
        return

    # 마크다운 문서 생성
    md_lines = []
    md_lines.append("# AI 모델 및 MCP 생태계 종합 지식 백과사전\n")
    md_lines.append(f"> **문서 생성일**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md_lines.append("> 본 문서는 NotebookLM 및 대형 언어 모델(LLM)에 소스로 업로드하여 질의응답 및 추천을 받기 위해 자동 생성된 통합 지식 베이스입니다.\n")

    # 1. 목차 및 통계
    companies = [n for n in nodes if n.get("type") == "company"]
    models = [n for n in nodes if n.get("type") == "model"]
    efforts = [n for n in nodes if n.get("type") == "effort"]
    mcps = [n for n in nodes if n.get("type") == "mcp"]
    concepts = [n for n in nodes if n.get("type") == "concept"]

    md_lines.append("## 📊 데이터셋 요약 현황")
    md_lines.append(f"- **AI 개발사**: {len(companies)}개사")
    md_lines.append(f"- **주요 AI 모델**: {len(models)}개")
    md_lines.append(f"- **추론 에포트 단계**: {len(efforts)}단계")
    md_lines.append(f"- **공식 및 인기 MCP 서버**: {len(mcps)}개")
    md_lines.append(f"- **핵심 개념 및 용어**: {len(concepts)}개\n")

    # 2. AI 모델 비교 일람표
    md_lines.append("## 🏆 주요 AI 모델 스펙 비교표\n")
    md_lines.append("| 모델명 | 출시일 | 컨텍스트 윈도우 | 가격 (1M 토큰) | 추천 태그 |")
    md_lines.append("| :--- | :--- | :--- | :--- | :--- |")
    for m in models:
        tags_str = ", ".join(m.get("tags", []))
        md_lines.append(f"| **{m.get('name')}** | {m.get('release_date', '-')} | {m.get('context_window', '-')} | {m.get('pricing', '-')} | {tags_str} |")
    md_lines.append("\n---\n")

    # 3. 모델별 상세 분석
    md_lines.append("## 🧠 모델별 상세 스펙 및 장단점 분석\n")
    for m in models:
        md_lines.append(f"### {m.get('name')}")
        md_lines.append(f"- **한 줄 요약**: {m.get('summary')}")
        md_lines.append(f"- **출시일**: {m.get('release_date', '-')}")
        md_lines.append(f"- **컨텍스트 길이**: {m.get('context_window', '-')}")
        md_lines.append(f"- **가격 정책**: {m.get('pricing', '-')}")
        
        if m.get("strengths"):
            md_lines.append("- **주요 강점**:")
            for s in m.get("strengths"):
                md_lines.append(f"  * {s}")
        if m.get("weaknesses"):
            md_lines.append("- **유의점 / 약점**:")
            for w in m.get("weaknesses"):
                md_lines.append(f"  * {w}")
        if m.get("source_url"):
            md_lines.append(f"- **공식 출처**: {m.get('source_url')}")
        md_lines.append("")

    md_lines.append("---\n")

    # 4. MCP 서버 목록
    md_lines.append("## 🔌 대중적인 MCP(Model Context Protocol) 서버 목록\n")
    for m in mcps:
        md_lines.append(f"### {m.get('name')}")
        md_lines.append(f"- **한 줄 요약**: {m.get('summary')}")
        md_lines.append(f"- **주요 용도**: {m.get('typical_use', '-')}")
        md_lines.append(f"- **태그**: {', '.join(m.get('tags', []))}")
        if m.get("source_url"):
            md_lines.append(f"- **소스 저장소**: {m.get('source_url')}")
        md_lines.append("")

    md_lines.append("---\n")

    # 5. 핵심 개념
    md_lines.append("## 💡 핵심 개념 및 용어 사전\n")
    for c in concepts:
        md_lines.append(f"### {c.get('name')}")
        md_lines.append(f"- **정의**: {c.get('summary')}")
        if c.get("details"):
            md_lines.append(f"- **세부 설명**: {c.get('details')}")
        md_lines.append("")

    # 파일 저장
    content = "\n".join(md_lines)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ 성공적으로 지식 베이스 문서가 생성되었습니다!")
    print(f"👉 파일 위치: {OUTPUT_FILE}")
    print("이 파일을 NotebookLM(제미나이 노트북)에 추가하여 다양한 질문을 던져보세요.")
    print("=" * 65)


if __name__ == "__main__":
    main()
