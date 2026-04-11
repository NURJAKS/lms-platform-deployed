# LMS Platform

Образовательная платформа (MVP). **Автор учебного проекта:** Жандос Сахиев.

В репозитории уже есть демо-БД (`backend/education.db`) и `backend/uploads/`. Файл `backend/.env` в git не входит — при первом запуске копируется из `backend/.env.example`.

**Стек:** FastAPI, SQLite · Next.js, TypeScript, Tailwind.

---

## Запуск на Windows

### 1. Что установить

| Что | Зачем |
|-----|--------|
| **Python 3.12+** | бэкенд ([python.org/downloads](https://www.python.org/downloads/) — включите **Add python.exe to PATH**) |
| **Node.js 20.9+** | фронтенд ([nodejs.org](https://nodejs.org/) LTS) |
| **Git** (по желанию) | клонирование ([git-scm.com/download/win](https://git-scm.com/download/win)) |

В PowerShell: `python --version` и `node --version`. Если нет `python`, попробуйте `py -3 --version`.

Распакуйте или клонируйте проект в **короткий путь на латинице** (например `C:\dev\lms-platform`), в корне должны лежать папки **`backend`** и **`frontend-next`**.

Освободите порты **8000** и **3000**. Брандмауэр может запросить доступ для Python и Node — разрешите для частной сети.

### 2. Получить код

```powershell
cd C:\dev
git clone https://github.com/NURJAKS/lms-platfrom-localversion.git
cd lms-platfrom-localversion
```

Или скачайте ZIP с GitHub и распакуйте так же.

### 3. Запуск одной командой

1. PowerShell в **корне** проекта (рядом с `start-windows.ps1`, папками `backend` и `frontend-next`).

2. При ошибке политики скриптов (один раз):

   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   ```

3. Запуск:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\start-windows.ps1
   ```

   Либо двойной щелчок по **`start-windows.cmd`**.

Скрипт создаст `backend\.venv`, установит зависимости, при необходимости скопирует **`backend\.env.example` → `backend\.env`**, запустит API и фронт.

4. В браузере: **http://localhost:3000** · Swagger: **http://127.0.0.1:8000/docs**

Остановка: **Ctrl+C** в том же окне.

### 4. Два окна (отдельный лог бэкенда)

**Окно 1 — API**

```powershell
powershell -ExecutionPolicy Bypass -File .\start-backend-windows.ps1
```

**Окно 2 — фронт**

```powershell
powershell -ExecutionPolicy Bypass -File .\start-frontend-windows.ps1
```

В `scripts\` есть **`start-backend.bat`** и **`start-frontend.bat`** (то же самое).

### 5. Секреты и база

- **`backend\.env`** — не коммитится; шаблон: **`backend\.env.example`**.
- **ИИ (чат):** при необходимости укажите **`OPENAI_API_KEY`** и/или **`GEMINI_API_KEY`**. Без ключей приложение работает в демо-режиме.
- **SQLite:** файл **`backend\education.db`**. Если файл удалён или повреждён:

  ```powershell
  cd backend
  .\.venv\Scripts\python.exe init_db.py
  .\.venv\Scripts\python.exe seed_data.py
  ```

### 6. Тестовые входы

| Роль | Email | Пароль |
|------|--------|--------|
| Администратор | admin@edu.kz | admin123 |
| Директор | director@edu.kz | director123 |
| Куратор | curator@edu.kz | curator123 |
| Преподаватель | teacher1@edu.kz, teacher2@edu.kz | teacher123 |
| Родитель | parent@edu.kz | parent123 |
| Студент | student1@edu.kz … student5@edu.kz | student123 |

---

## Важно

- **`backend/.env`** в репозиторий не добавляйте.
- После **`git clone`** приходят те же **`education.db`** и **`uploads`**, что в коммите (если они в репозитории).
