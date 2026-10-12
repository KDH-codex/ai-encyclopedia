@echo off
chcp 65001 > nul
title [AI 백과사전] Gemini 노트북(NotebookLM) 지식 문서 추출기
echo ===================================================
echo   📖 NotebookLM용 마크다운 백과사전 문서를 생성합니다
echo ===================================================
echo.

cd /d "%~dp0"
py scripts\export_for_notebook.py

echo.
echo ===================================================
echo   생성 완료! ai_encyclopedia_knowledge_base.md 확인
echo ===================================================
pause > nul
