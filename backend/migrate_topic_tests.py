"""
Replace topic test questions with topic-specific sets for Python (course 1) and Web (course 2).
Fixes Web course showing Python questions. Run from backend dir: python migrate_topic_tests.py
"""
import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from app.models import CourseTopic, Test, TestQuestion

from seed_data import (
    TOPIC_QUESTIONS_PYTHON,
    PYTHON_FINAL_QUESTIONS,
    TOPIC_QUESTIONS_WEB,
    WEB_FINAL_QUESTIONS,
    _add_questions_to_test,
)


def migrate():
    db = SessionLocal()
    try:
        # Course 1: Python — per-topic tests
        topics1 = db.query(CourseTopic).filter(CourseTopic.course_id == 1).order_by(CourseTopic.order_number).all()
        for idx, topic in enumerate(topics1):
            if idx >= len(TOPIC_QUESTIONS_PYTHON):
                continue
            test = db.query(Test).filter(Test.topic_id == topic.id, Test.is_final == 0).first()
            if not test:
                continue
            db.query(TestQuestion).filter(TestQuestion.test_id == test.id).delete()
            qs = TOPIC_QUESTIONS_PYTHON[idx]
            _add_questions_to_test(db, test.id, qs)
            test.question_count = len(qs)
            print(f"Python topic {topic.id} ({topic.title[:30]}...): test {test.id} — {len(qs)} questions")
        # Course 1: final test
        final1 = db.query(Test).filter(Test.course_id == 1, Test.is_final == 1).first()
        if final1:
            db.query(TestQuestion).filter(TestQuestion.test_id == final1.id).delete()
            _add_questions_to_test(db, final1.id, PYTHON_FINAL_QUESTIONS)
            final1.question_count = len(PYTHON_FINAL_QUESTIONS)
            print(f"Python final test {final1.id}: {len(PYTHON_FINAL_QUESTIONS)} questions")

        # Course 2: Web — per-topic tests
        topics2 = db.query(CourseTopic).filter(CourseTopic.course_id == 2).order_by(CourseTopic.order_number).all()
        for idx, topic in enumerate(topics2):
            if idx >= len(TOPIC_QUESTIONS_WEB):
                continue
            test = db.query(Test).filter(Test.topic_id == topic.id, Test.is_final == 0).first()
            if not test:
                continue
            db.query(TestQuestion).filter(TestQuestion.test_id == test.id).delete()
            qs = TOPIC_QUESTIONS_WEB[idx]
            _add_questions_to_test(db, test.id, qs)
            test.question_count = len(qs)
            print(f"Web topic {topic.id} ({topic.title[:30]}...): test {test.id} — {len(qs)} questions")
        # Course 2: final test
        final2 = db.query(Test).filter(Test.course_id == 2, Test.is_final == 1).first()
        if final2:
            db.query(TestQuestion).filter(TestQuestion.test_id == final2.id).delete()
            _add_questions_to_test(db, final2.id, WEB_FINAL_QUESTIONS)
            final2.question_count = len(WEB_FINAL_QUESTIONS)
            print(f"Web final test {final2.id}: {len(WEB_FINAL_QUESTIONS)} questions")

        db.commit()
        print("Done. All topic and final tests updated with topic-specific questions.")
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
