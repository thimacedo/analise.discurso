@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
python -X utf8 scripts\work_session.py > debug_session.log 2>&1