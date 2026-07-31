@echo off
chcp 65001 >nul
rem Local dev server launcher.
rem PYTHONPATH is not set here: Django resolves apps/ via manage.py automatically.
rem If you use a virtualenv, activate it first or set PYTHONPATH to your venv.
set DJANGO_DEBUG=True
set DJANGO_SECRET_KEY=dev-local
python manage.py runserver 0.0.0.0:8000
pause
