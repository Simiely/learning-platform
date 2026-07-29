@echo off
chcp 65001 >nul
set PYTHONPATH=D:\workbuddy\2026-07-29-14-04-53\learning-platform\.venv\site-packages
set DJANGO_DEBUG=True
set DJANGO_SECRET_KEY=dev-local
"C:\Users\2504\.workbuddy\binaries\python\versions\3.13.12\python.exe" manage.py runserver 0.0.0.0:8000
pause
