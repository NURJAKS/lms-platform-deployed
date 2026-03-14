# LMS Platform

Образовательная платформа (MVP) с AI-помощником и геймификацией.

**Стек:** Backend — Python (FastAPI, SQLAlchemy, SQLite). Frontend — Next.js 16, React 19, TypeScript, Tailwind CSS.

## Требования

- Python 3.12+
- Node.js 20.9.0+
- Git

## Установка и запуск

### 1. Клонирование

```bash
git clone https://github.com/NURJAKS/LMS-Platform-client.git
cd LMS-Platform-client
```

### 2. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
mkdir -p data
python init_db.py
python seed_data.py
python seed_shop.py
python seed_mock_progress.py
python seed_real_students_progress.py
cp .env.example .env   # при необходимости отредактировать
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

API: http://127.0.0.1:8000  
Документация: http://127.0.0.1:8000/docs

### 3. Frontend

В новом терминале:

```bash
cd frontend-next
npm install
npm run dev
```

Приложение: http://localhost:3000

## Тестовые пользователи

| Роль          | Email           | Пароль    |
|---------------|-----------------|-----------|
| Менеджер      | admin@edu.kz    | admin123  |
| Преподаватель | teacher1@edu.kz | teacher123 |
| Студент       | student1@edu.kz | student123 |

## Структура

- `backend/` — FastAPI, модели, API, скрипты БД
- `frontend-next/` — Next.js: страницы, компоненты, API-клиент

## Docker

```bash
docker compose up -d --build
```

Backend: http://localhost:8000  
Frontend: http://localhost:3000

## Важно

- `.env` и база `backend/data/education.db` не коммитятся
- Для сброса БД повторите команды из шага 2 (init_db, seed_*)
