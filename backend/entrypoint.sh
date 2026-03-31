#!/bin/sh
set -e

# Wait for database to be ready
echo "Waiting for postgres..."
python << END
import socket
import time
import os
from urllib.parse import urlparse

db_url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/education_platform")
u = urlparse(db_url)
host = u.hostname
port = u.port or 5432

while True:
    try:
        with socket.create_connection((host, port), timeout=1):
            break
    except (OSError, ConnectionRefusedError):
        time.sleep(1)
END
echo "Postgres is up!"

# Create tables and seed demo data (each seed skips if data exists)
python init_db.py
python seed_data.py 2>/dev/null || true
python seed_shop.py 2>/dev/null || true
python seed_mock_progress.py 2>/dev/null || true
python seed_real_students_progress.py 2>/dev/null || true
# seed_leaderboard_students.py отключен - моковые студенты создаются только для ручного тестирования
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

