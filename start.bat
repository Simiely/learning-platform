@echo off
set DJANGO_DEBUG=True
set DJANGO_SECRET_KEY=dev-local
"D:\workbuddy\2026-07-27-20-28-39\venv\Scripts\python.exe" manage.py runserver 0.0.0.0:8000
pause
