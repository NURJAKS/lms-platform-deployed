#!/usr/bin/env bash
# Запуск бэкенда локально (без Docker). Использует backend/.venv и backend/education.db
set -e
cd "$(dirname "$0")/backend"
if [[ ! -d .venv ]]; then
  echo "Создаю виртуальное окружение backend/.venv..."
  python3 -m venv .venv
  . .venv/bin/activate
  pip install -q -r requirements.txt
else
  source .venv/bin/activate
fi
if [[ ! -f .env ]]; then
  echo "Скопируйте backend/.env.example в backend/.env и настройте (минимум DATABASE_URL)."
  exit 1
fi
echo "Бэкенд: http://127.0.0.1:8000  (документация: http://127.0.0.1:8000/docs)"
exec python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
