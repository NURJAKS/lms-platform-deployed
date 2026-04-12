# Развёртывание LMS на VPS (Docker + Nginx + HTTPS)

Домен и DNS должны указывать на IP сервера (записи **A** для `@` и `www`). Дальше — команды для **Ubuntu 22.04+** (root или `sudo`).

---

## 1. Docker Engine

```bash
apt update && apt install -y ca-certificates curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${VERSION_CODENAME:-jammy}") stable" > /etc/apt/sources.list.d/docker.list
apt update && apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
docker compose version
```

---

## 2. Клонирование и переменные окружения

```bash
mkdir -p ~/projects && cd ~/projects
git clone https://github.com/NURJAKS/lms-platfrom-localversion.git
cd lms-platfrom-localversion

cp env.deploy.example .env.deploy
nano .env.deploy
```

Обязательно:

| Переменная | Значение |
|------------|----------|
| `SECRET_KEY` | `openssl rand -hex 32` — вставьте вывод |
| `POSTGRES_PASSWORD` | Надёжный пароль. Избегайте в пароле символов `@`, `:`, `#` (они ломают URL) или задайте `DATABASE_URL` вручную. По умолчанию пользователь и БД: `lms` / `education_platform`. |
| `ALLOWED_ORIGINS` | `https://qazaqitacademy-edu.pp.ua,https://www.qazaqitacademy-edu.pp.ua` (при отладке можно добавить `,http://localhost:3000`) |
| `FRONTEND_PUBLIC_URL` | `https://qazaqitacademy-edu.pp.ua` |

Ключи `OPENAI_API_KEY` / `GEMINI_API_KEY` — по желанию (без них ИИ в демо-режиме). Приоритет: OpenAI, если ключ задан, иначе Gemini. Опционально: `OPENAI_CHAT_MODEL`, `OPENAI_CHALLENGE_MODEL`, `GEMINI_MODEL` (см. `env.deploy.example`).

Файл `.env.deploy` **не коммитьте** (уже в `.gitignore`).

### PostgreSQL и перенос с SQLite (сохранить данные)

На VPS теперь используется **PostgreSQL** (том `lms_postgres_data`). Старый вариант с SQLite (`lms_sqlite_data`, файл `education.db`) можно перенести скриптом `backend/migrate_sqlite_to_pg.py`.

**Рекомендуемый порядок:**

1. **Бэкап:** сохраните копию `education.db` и при необходимости том `lms_uploads`. Пример:  
   `docker run --rm -v ИМЯ_ТОМА_SQLITE:/data:ro alpine cat /data/education.db > ~/education-backup.db`  
   (имя тома: `docker volume ls`.)
2. Остановите стек: `docker compose --env-file .env.deploy -f docker-compose.vps.yml down`.
3. В `.env.deploy` задайте `POSTGRES_PASSWORD` (и при необходимости `POSTGRES_USER` / `POSTGRES_DB`).
4. Запустите перенос (поднимает только `db`, затем копирует строки в Postgres):  
   `chmod +x deploy/migrate-sqlite-to-pg.sh`  
   `./deploy/migrate-sqlite-to-pg.sh /полный/путь/education-backup.db`  
   **Не** запускайте полный `up` до миграции, если в пустой Postgres уже успели попасть демо-данные от предыдущего запуска — в этом случае остановите стек, удалите том `lms_postgres_data` и повторите шаг 4 (удаление тома стирает текущую БД в Postgres).
5. Поднимите всё: `docker compose --env-file .env.deploy -f docker-compose.vps.yml up -d --build`

После переноса `seed_data.py` при старте увидит существующих пользователей и не зальёт демо с нуля; `seed_shop.py` добавит только отсутствующие товары.

Эквивалент вручную: поднять `db`, затем  
`docker compose --env-file .env.deploy -f docker-compose.vps.yml run --rm --no-deps --entrypoint python -v /путь/education.db:/tmp/migrate_source.db:ro backend migrate_sqlite_to_pg.py --sqlite-url sqlite:////tmp/migrate_source.db --force`  
(`DATABASE_URL` в контейнере `backend` задаётся compose.)

---

## 3. Запуск контейнеров

Из **корня** репозитория (где лежат `docker-compose.vps.yml` и `.env.deploy`):

```bash
chmod +x deploy/bootstrap-vps.sh
./deploy/bootstrap-vps.sh
```

Скрипт при отсутствии `.env.deploy` создаст его из примера и подставит случайный `SECRET_KEY`.

Или вручную:

```bash
docker compose --env-file .env.deploy -f docker-compose.vps.yml up -d --build
docker compose --env-file .env.deploy -f docker-compose.vps.yml ps
```

Проверка локально на сервере:

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000/
```

Должен вернуться код **200** (или 307/302).

- **Фронт** слушает **3000** на хосте (Next.js).
- **Бэкенд** (:8000) **не** пробрасывается наружу — нет конфликта с другим проектом на порту 8000. API для браузера — через тот же домен (`/api` проксирует Next).

Если порт **3000** занят — в `docker-compose.vps.yml` замените у `frontend` строку портов на `"3010:3000"` и в Nginx (шаг 4) укажите `proxy_pass http://127.0.0.1:3010`.

---

## 4. Nginx (reverse proxy)

Если при `nginx -t` ошибка **`could not build server_names_hash`**, в **`/etc/nginx/nginx.conf`** внутри блока **`http {`** добавьте (сразу после открывающей скобки):

```nginx
    server_names_hash_bucket_size 64;
```

(при необходимости **128** — для очень длинных доменов и многих `server_name`.)

```bash
apt install -y nginx
cp deploy/nginx-qazaqitacademy.example.conf /etc/nginx/sites-available/qazaqitacademy-edu.pp.ua
ln -sf /etc/nginx/sites-available/qazaqitacademy-edu.pp.ua /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

Убедитесь, что в конфиге `proxy_pass` совпадает с портом фронта (3000 или 3010).

---

## 5. HTTPS (Certbot)

Когда по **HTTP** сайт открывается по домену (DNS уже «дошёл»):

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d qazaqitacademy-edu.pp.ua -d www.qazaqitacademy-edu.pp.ua
```

После выпуска сертификата в `.env.deploy` должны быть **https://** в `ALLOWED_ORIGINS` (как в примере). Затем:

```bash
docker compose --env-file .env.deploy -f docker-compose.vps.yml up -d
```

---

## 6. Файрвол (по желанию)

```bash
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
ufw status
```

Прямой доступ к порту 3000 с интернета не обязателен — достаточно 80/443 через Nginx.

---

## 7. Обновление версии (тот же сервер, уже PostgreSQL)

Если на VPS уже развёрнута **актуальная схема** с Postgres и томами из текущего `docker-compose.vps.yml`:

```bash
cd ~/projects/lms-platfrom-localversion
git pull
docker compose --env-file .env.deploy -f docker-compose.vps.yml up -d --build
```

Данные БД и `uploads` хранятся в Docker-томах (`lms_postgres_data`, `lms_uploads`).

**Переход со старой версии** (раньше был SQLite или другой compose): см. **раздел 10** — бэкапы, миграция БД, том `uploads`.

---

## 8. Логи и отладка

```bash
docker compose --env-file .env.deploy -f docker-compose.vps.yml logs -f --tail=100
```

Отдельно бэкенд / фронт:

```bash
docker compose --env-file .env.deploy -f docker-compose.vps.yml logs -f backend
docker compose --env-file .env.deploy -f docker-compose.vps.yml logs -f frontend
```

---

## 9. Чеклист: готовность к VPS (после обновлений кода)

Перед `up -d --build` убедитесь:

| Что | Зачем |
|-----|--------|
| `.env.deploy` из `env.deploy.example`, заполнены `SECRET_KEY`, `POSTGRES_PASSWORD`, `ALLOWED_ORIGINS`, `FRONTEND_PUBLIC_URL` | Без этого контейнеры не поднимутся или API отрежет браузер (CORS). |
| Ключи `OPENAI_API_KEY` / `GEMINI_API_KEY` (хотя бы один) | Иначе ИИ-чат и часть AI Challenge работают в демо/симуляции. |
| `docker-compose.vps.yml` — сервисы `db`, `backend`, `frontend`; тома `lms_postgres_data`, `lms_uploads` | PostgreSQL для продакшена; файлы загрузок отдельно от БД. |
| Nginx с таймаутами для прокси (как в `deploy/nginx-qazaqitacademy.example.conf`) | Снижает 504 на долгих запросах к `/api` (ИИ). |
| Переход со **старого SQLite на VPS**: бэкап `education.db` + миграция (раздел 2) | Данные пользователей и курсов переносятся скриптом; файлы — из тома `uploads`. |

Продакшен-режим: в compose для backend задано `DEBUG: "false"`; документация API (`/docs`) в этом режиме отключена — это ожидаемо.

---

## 10. Обновление на сервере, где уже стоит старая версия

Цель: подтянуть **новый код** и перейти на текущий стек (**PostgreSQL**, новый `docker-compose.vps.yml`), **сохранив данные** (БД + загрузки).

### 10.1. Резервные копии (обязательно)

На сервере, в каталоге проекта (путь может отличаться, например `~/projects/lms-platfrom-localversion`):

```bash
cd /путь/к/проекту
docker compose --env-file .env.deploy -f docker-compose.vps.yml ps
```

1. **Сохраните `.env.deploy`** (секреты не потерять):
   ```bash
   cp .env.deploy ~/lms-env-backup-$(date +%F).txt
   ```

2. **Тома Docker** (имена смотрите: `docker volume ls | grep -E 'lms|project'`):
   - Старый **SQLite** (если был): снять файл БД:
     ```bash
     docker run --rm -v ИМЯ_ТОМА_SQLITE:/data:ro alpine cat /data/education.db > ~/education-backup-$(date +%F).db
     ```
   - **Загрузки** (`uploads`): том обычно называется `…_lms_uploads` (префикс — имя проекта compose). Сохраните архив или скопируйте в бэкап:
     ```bash
     docker run --rm -v ИМЯ_ТОМА_UPLOADS:/data:ro -v ~:/backup alpine \
       tar czf /backup/lms-uploads-backup-$(date +%F).tar.gz -C /data .
     ```

3. Остановите стек:
   ```bash
   docker compose --env-file .env.deploy -f docker-compose.vps.yml down
   ```

### 10.2. Новый код

```bash
cd /путь/к/проекту
git stash   # если были локальные правки
git pull origin main   # или ваша ветка
```

Если репозиторий клонировали заново в другую папку — скопируйте сюда **сохранённый** `~/lms-env-backup-….txt` как `.env.deploy` и **дополните** новыми переменными из актуального `env.deploy.example` (в первую очередь `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`).

### 10.3. Переменные окружения

- Сохраните прежний **`SECRET_KEY`**, если не хотите разлогинить всех пользователей (иначе JWT станут невалидны).
- Задайте **`POSTGRES_PASSWORD`** (и при желании пользователя/имя БД как в примере).
- Проверьте **`ALLOWED_ORIGINS`** / **`FRONTEND_PUBLIC_URL`** под ваш домен (https).

### 10.4. База: переход SQLite → PostgreSQL

Если на старом VPS была **только SQLite** в томе:

1. Файл `~/education-backup-….db` уже снят (шаг 10.1).
2. Восстановите **новый** `docker-compose.vps.yml` из репозитория, убедитесь что `.env.deploy` готов.
3. Выполните миграцию данных (поднимется только Postgres, данные перельются):
   ```bash
   chmod +x deploy/migrate-sqlite-to-pg.sh
   ./deploy/migrate-sqlite-to-pg.sh ~/education-backup-YYYY-MM-DD.db
   ```
4. Если вы **уже** успели поднять backend с пустым Postgres и там появились демо-данные — остановите стек, удалите том `lms_postgres_data` (имя уточните: `docker volume ls`) и снова запустите `migrate-sqlite-to-pg.sh` (данные в этом томе Postgres будут стёрты).

Если на сервере **уже был PostgreSQL** с тем же compose — достаточно `git pull` и `up -d --build` (раздел 7), миграция SQLite не нужна.

### 10.5. Том `uploads`

- Если **имя проекта compose** и каталог тот же, том `lms_uploads` может подхватиться сам.
- Если том новый/пустой — распакуйте бэкап загрузок в том **после** первого `up` (контейнер остановлен) или скопируйте через временный контейнер с монтированием двух томов (см. документацию Docker по копированию между volume).

### 10.6. Запуск и проверка

```bash
docker compose --env-file .env.deploy -f docker-compose.vps.yml up -d --build
docker compose --env-file .env.deploy -f docker-compose.vps.yml ps
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3000/
docker compose --env-file .env.deploy -f docker-compose.vps.yml logs -f --tail=50 backend
```

Nginx и Certbot менять не нужно, если домен и порт фронта (3000) не менялись. Если обновляли пример конфига — снова скопируйте `deploy/nginx-qazaqitacademy.example.conf`, `nginx -t`, `reload`.

---

## Типичные проблемы

| Симптом | Что проверить |
|---------|----------------|
| `dependency failed to start: container … backend … is unhealthy` | Логи: `docker compose … logs backend --tail=200` и `docker compose … logs db --tail=100`. Часто — нет `SECRET_KEY`/`POSTGRES_PASSWORD`, Postgres не готов. После правок: `docker compose … up -d --force-recreate`. |
| CORS / «blocked by CORS» | `ALLOWED_ORIGINS` содержит **точный** origin из адресной строки (с `https://` и при необходимости `www`). |
| 502 Bad Gateway | Контейнер фронта не слушает: `docker compose ps`, `curl 127.0.0.1:3000`. Порт в Nginx = порт в compose. |
| **504** на `/api/...` при долгом ИИ | В примере `deploy/nginx-qazaqitacademy.example.conf` заданы `proxy_read_timeout` и др. (300s). После правок Nginx: `nginx -t && systemctl reload nginx`. Старый конфиг без таймаутов — обновите с репозитория. |
| Другой проект на :8000 | Нормально: бэкенд LMS не публикует 8000 на хост. |
| Swagger | Откройте `https://ваш-домен/docs` — запрос идёт через фронт/прокси к API. |
| `buildx isn't installed` | Предупреждение можно игнорировать или: `apt install -y docker-buildx-plugin`. |

---

Учебный проект: **Жандос Сахиев**.
