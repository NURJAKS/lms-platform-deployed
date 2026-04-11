# Развёртывание на VPS (Docker + SQLite + демо-данные)

Репозиторий уже содержит **`backend/education.db`** и **`backend/uploads/`**. Образ бэкенда кладёт их в **`/opt/lms-bundled`**: при первом запуске с томами пустая БД и пустой каталог uploads **один раз** заполняются из этой копии. Дальше данные живут в Docker-томах и не пропадают при пересоздании контейнеров.

Отдельный PostgreSQL для этого сценария **не нужен** (есть альтернатива: корневой `docker-compose.yml` с сервисом `db`).

## Требования на сервере

- Ubuntu 22.04+ (или другой Linux с Docker)
- [Docker Engine](https://docs.docker.com/engine/install/) и Docker Compose v2
- Открытые порты **3000** (сайт) и **8000** (API; при желании закройте 8000 снаружи и оставьте только прокси)

## Быстрый старт

```bash
sudo apt update && sudo apt install -y git
git clone https://github.com/NURJAKS/lms-platform-deployed.git
cd lms-platform-deployed

cp env.deploy.example .env.deploy
nano .env.deploy   # SECRET_KEY, ALLOWED_ORIGINS, FRONTEND_PUBLIC_URL

docker compose --env-file .env.deploy -f docker-compose.vps.yml up -d --build
```

Откройте в браузере: `http://<IP_сервера>:3000`. Swagger: `http://<IP_сервера>:8000/docs`.

Тестовые логины — как в [README.md](../README.md) (раздел «Тестовые входы»), если используете поставляемую демо-БД без замены.

## Переменные `.env.deploy`

| Переменная | Назначение |
|------------|------------|
| `SECRET_KEY` | Секрет JWT; обязательно уникальный в продакшене |
| `ALLOWED_ORIGINS` | CORS: список origin фронта (например `http://1.2.3.4:3000` или `https://ваш-домен`) |
| `FRONTEND_PUBLIC_URL` | Публичный URL фронта для ссылок в письмах |
| `OPENAI_API_KEY` / `GEMINI_API_KEY` | По желанию; без них ИИ-функции в демо-режиме |

**Важно:** в `ALLOWED_ORIGINS` должен быть **точный** origin, как в адресной строке браузера (схема + хост + порт), иначе браузер заблокирует запросы к API.

## Обновление версии

```bash
cd lms-platform-deployed
git pull
docker compose --env-file .env.deploy -f docker-compose.vps.yml up -d --build
```

Тома `lms_sqlite_data` и `lms_uploads` сохраняют ваши данные; новый образ **не перезаписывает** уже существующий `education.db` на томе. Чтобы заново получить демо из образа, нужно удалить том (это **удалит данные**):

```bash
docker compose --env-file .env.deploy -f docker-compose.vps.yml down
docker volume rm lms-platform-deployed_lms_sqlite_data lms-platform-deployed_lms_uploads
# имена томов посмотрите: docker volume ls
```

## HTTPS и домен (рекомендуется)

Поставьте reverse proxy (Caddy, Traefik или nginx) на порты 80/443, проксируйте на `127.0.0.1:3000`. Обновите `ALLOWED_ORIGINS` и `FRONTEND_PUBLIC_URL` на `https://ваш-домен`.

## Альтернатива: PostgreSQL

Если нужен Postgres вместо SQLite, используйте **`docker-compose.yml`** в корне (сервисы `db`, `backend`, `frontend`). Схема и сиды поднимаются entrypoint’ом бэкенда; **данные из `education.db` в Postgres автоматически не переносятся** — это отдельная миграция/экспорт.

## Без Docker (systemd)

Установите Python 3.12+ и Node 20+, скопируйте `backend/.env.example` → `backend/.env`, укажите `DATABASE_URL=sqlite:///./education.db`, `ALLOWED_ORIGINS`, `FRONTEND_PUBLIC_URL`. Запускайте `uvicorn` и `npm run start` за процесс-менеджером. Подробнее в [README.md](../README.md).
