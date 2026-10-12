# -*- coding: utf-8 -*-
"""
=============================================================================
[AI 백과사전] 후보 데이터 검토 및 본 데이터 병합 도구 (merge_candidates.py)
=============================================================================
이 스크립트는 'candidates.json'에 모인 신규 모델/MCP 후보들을
터미널에서 하나씩 눈으로 확인하고, 사람이 직접 승인(y) 여부를 결정하여
정식 백과사전 데이터인 'nodes.json'과 'edges.json'에 안전하게 병합하는 도구입니다.

[기획서 핵심 원칙]
- 자동 검색 결과의 오류 가능성을 방지하기 위해 반드시 사람이 최종 승인합니다.
- 승인된 데이터는 즉시 웹 지식 그래프 화면에 반영됩니다.
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
CANDIDATES_FILE = os.path.join(DATA_DIR, "candidates.json")


def load_json(filepath, default_value):
    """지정된 JSON 파일을 안전하게 읽어오는 유틸리티 함수입니다."""
    if not os.path.exists(filepath):
        return default_value
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[오류] {filepath} 읽기 실패: {e}")
        return default_value


def save_json(filepath, data):
    """JSON 데이터를 포맷팅하여 안전하게 저장하는 함수입니다."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    print("=" * 65)
    print("📋 [AI 백과사전] 신규 후보 검토 및 본 데이터 병합 도우미")
    print("=" * 65)

    candidates = load_json(CANDIDATES_FILE, [])
    nodes = load_json(NODES_FILE, [])
    edges = load_json(EDGES_FILE, [])

    pending_items = [c for c in candidates if c.get("status") == "pending_approval"]

    if not pending_items:
        print("\n현재 검토 대기 중인 신규 후보가 없습니다.")
        print("💡 먼저 'py scripts/search_candidates.py' 를 실행해 후보를 수집해보세요.")
        return

    print(f"\n총 {len(pending_items)}개의 후보 항목이 대기 중입니다. 하나씩 확인합니다.\n")

    remaining_candidates = []
    approved_count = 0
    rejected_count = 0

    for idx, item in enumerate(pending_items, 1):
        print("-" * 65)
        print(f"[{idx}/{len(pending_items)}] 검토 대상: {item.get('name')} ({item.get('type')})")
        print("-" * 65)
        print(f"• ID         : {item.get('id')}")
        print(f"• 유형       : {item.get('type')}")
        if item.get('company'):
            print(f"• 개발사     : {item.get('company')}")
        print(f"• 출시/발견일: {item.get('release_date', item.get('discovered_at', '-'))}")
        print(f"• 한 줄 요약 : {item.get('summary', '-')}")
        if item.get('strengths'):
            print(f"• 주요 강점  : {', '.join(item.get('strengths'))}")
        if item.get('pricing'):
            print(f"• 가격 정보  : {item.get('pricing')}")
        if item.get('context_window'):
            print(f"• 컨텍스트 창: {item.get('context_window')}")
        print(f"• 출처 URL   : {item.get('source_url', '-')}")
        print("-" * 65)

        # 사용자 선택 입력받기
        while True:
            choice = input("이 항목을 정식 데이터로 승인하시겠습니까? [y: 승인 / n: 거절삭제 / s: 보류건너뛰기]: ").strip().lower()
            if choice in ['y', 'n', 's']:
                break
            print("올바른 옵션을 입력해주세요 (y, n, s 중 하나)")

        if choice == 'y':
            # 승인된 노드로 변환
            new_node = {
                "id": item.get("id"),
                "name": item.get("name"),
                "type": item.get("type"),
                "summary": item.get("summary"),
                "last_verified": datetime.now().strftime("%Y-%m-%d"),
                "source_url": item.get("source_url")
            }

            if item.get("type") == "model":
                new_node["release_date"] = item.get("release_date")
                new_node["strengths"] = item.get("strengths", [])
                new_node["weaknesses"] = item.get("weaknesses", [])
                new_node["pricing"] = item.get("pricing", "-")
                new_node["context_window"] = item.get("context_window", "-")
                new_node["tags"] = item.get("tags", [])

                # 기본 연결 엣지(관계선) 자동 구성
                edges.append({
                    "source": new_node["id"],
                    "target": "effort-high",
                    "relation": "provides_effort",
                    "label": "심층 사고 지원"
                })

            elif item.get("type") == "mcp":
                new_node["protocol"] = item.get("protocol", "Model Context Protocol")
                new_node["tags"] = item.get("tags", [])
                new_node["typical_use"] = item.get("typical_use", "-")
                # MCP 개념 노드와 연결선 자동 추가
                edges.append({
                    "source": new_node["id"],
                    "target": "concept-mcp",
                    "relation": "relates_to",
                    "label": "MCP 구현체"
                })

            # 중복 체크 후 노드 추가
            if not any(n["id"] == new_node["id"] for n in nodes):
                nodes.append(new_node)
                approved_count += 1
                print(f"  ✨ '{new_node['name']}' 노드가 nodes.json 및 edges.json에 추가되었습니다.")

        elif choice == 'n':
            rejected_count += 1
            print(f"  🗑️ '{item.get('name')}' 후보가 삭제(기각)되었습니다.")

        elif choice == 's':
            # 보류 상태로 남김
            remaining_candidates.append(item)
            print(f"  ⏸️ '{item.get('name')}' 후보가 보류되었습니다.")

    # 파일 저장
    save_json(NODES_FILE, nodes)
    save_json(EDGES_FILE, edges)
    save_json(CANDIDATES_FILE, remaining_candidates)

    print("\n" + "=" * 65)
    print(f"🎉 병합 작업 완료! (승인: {approved_count}개, 기각: {rejected_count}개, 보류: {len(remaining_candidates)}개)")
    print(f"현재 백과사전 등록 노드 총계: {len(nodes)}개")
    print("브라우저에서 web/index.html을 새로고침하여 반영된 모습을 확인해보세요.")
    print("=" * 65)


if __name__ == "__main__":
    main()
