#!/usr/bin/env bash
# Запуск фронтенда локально. Ожидается, что бэкенд уже запущен на http://127.0.0.1:8000
set -e
cd "$(dirname "$0")/frontend-next"
if [[ ! -d node_modules ]]; then
  echo "Устанавливаю зависимости..."
  npm install
fi
echo "Фронтенд: http://localhost:3000  (API проксируется на бэкенд :8000)"
exec npm run dev
