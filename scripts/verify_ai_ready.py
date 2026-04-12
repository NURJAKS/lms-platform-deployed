import sys
import os
from pathlib import Path

# Добавляем путь к backend, чтобы можно было импортировать настройки и модели
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from app.core.config import settings
    from app.services.ai_service import solve_quiz_questions
    from app.core.database import SessionLocal
    from sqlalchemy import text
    print("✅ Импорт модулей успешен.")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

def verify():
    print(f"--- Проверка ИИ в продакшене ---")
    
    # 1. Проверка ключей
    has_openai = bool(settings.OPENAI_API_KEY)
    has_gemini = bool(settings.GEMINI_API_KEY)
    print(f"Ключ OpenAI: {'Присутствует' if has_openai else 'Отсутствует'}")
    print(f"Ключ Gemini: {'Присутствует' if has_gemini else 'Отсутствует'}")
    
    if not has_openai and not has_gemini:
        print("⚠️ ВНИМАНИЕ: Ключи ИИ не настроены. ИИ будет работать в режиме симуляции.")

    # 2. Проверка базы данных
    db = SessionLocal()
    try:
        # Проверяем таблицу кэша
        db.execute(text("SELECT 1 FROM ai_challenge_cache LIMIT 1"))
        print("✅ Таблица ai_challenge_cache существует.")
        
        # Проверяем таблицу челленджей и новые колонки
        db.execute(text("SELECT ai_level, recommendations FROM ai_challenges LIMIT 1"))
        print("✅ Колонки в ai_challenges существуют.")
        
    except Exception as e:
        print(f"❌ Ошибка БД: {e}")
        print("Подсказка: возможно, нужно запустить миграцию через docker exec.")
    finally:
        db.close()

    # 3. Тестовый запуск ИИ логики
    print("Запуск тестового запроса к ИИ (solve_quiz_questions)...")
    test_questions = [
        {"id": 1, "text": "2+2=?", "correct_answer": "4"}
    ]
    
    try:
        # Создаем временную сессию для теста
        test_db = SessionLocal()
        results = solve_quiz_questions(
            questions=test_questions,
            ai_level="intermediate",
            db=test_db
        )
        test_db.close()
        
        if results and len(results) > 0:
            print(f"✅ ИИ ответил успешно: {results[0].get('answer')}")
            print("🚀 Всё системы ИИ готовы к работе!")
        else:
            print("❌ ИИ вернул пустой результат.")
    except Exception as e:
        print(f"❌ Ошибка при вызове ИИ: {e}")

if __name__ == "__main__":
    verify()
