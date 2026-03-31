import os
import sys
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker

# Add app directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "app"))

from app.core.database import Base
from app.models import (
    User, CourseCategory, Course, CourseModule, CourseTopic, Test, TestQuestion,
    StudentProgress, CourseEnrollment, Certificate, AIChallenge, UserActivityLog,
    StudySchedule, StudentGoal, TeacherGroup, GroupStudent, TeacherAssignment,
    TeacherAssignmentRubric, AssignmentSubmission, AssignmentSubmissionGrade,
    Notification, AIChatHistory, Payment, CoinTransactionLog, DailyLeaderboardReward,
    ShopItem, UserPurchase, UserFavorite, CartItem, PremiumSubscription,
    CourseApplication, AddStudentTask, TeacherMaterial, TeacherQuestion,
    TeacherQuestionAnswer, CourseReview, CommunityPost, CommunityPostLike,
    TopicNote, StudentProfile
)

# Configuration
SQLITE_URL = "sqlite:///./education.db"
POSTGRES_URL = "postgresql://postgres:postgres@localhost:5432/education_platform"

# Models in dependency order (matching __init__.py)
MODELS = [
    User, CourseCategory, Course, CourseModule, CourseTopic, Test, TestQuestion,
    StudentProgress, CourseEnrollment, Certificate, AIChallenge, UserActivityLog,
    StudySchedule, StudentGoal, TeacherGroup, GroupStudent, TeacherAssignment,
    TeacherAssignmentRubric, AssignmentSubmission, AssignmentSubmissionGrade,
    Notification, AIChatHistory, Payment, CoinTransactionLog, DailyLeaderboardReward,
    ShopItem, UserPurchase, UserFavorite, CartItem, PremiumSubscription,
    CourseApplication, AddStudentTask, TeacherMaterial, TeacherQuestion,
    TeacherQuestionAnswer, CourseReview, CommunityPost, CommunityPostLike,
    TopicNote, StudentProfile
]

def migrate():
    print(f"Connecting to Source: {SQLITE_URL}")
    print(f"Connecting to Target: {POSTGRES_URL}")

    # Engines
    sqlite_engine = create_engine(SQLITE_URL)
    postgres_engine = create_engine(POSTGRES_URL)

    # 1. Create tables in Postgres
    print("Initializing Postgres schema...")
    Base.metadata.create_all(postgres_engine)

    # 2. Sessions
    SqliteSession = sessionmaker(bind=sqlite_engine)
    PostgresSession = sessionmaker(bind=postgres_engine)

    sqlite_db = SqliteSession()
    postgres_db = PostgresSession()

    try:
        # Disable all triggers/constraints for migration (to handle orphans in SQLite)
        postgres_db.execute(text("SET session_replication_role = 'replica'"))
        
        for model in MODELS:
            table_name = model.__tablename__
            print(f"Migrating table: {table_name}...", end=" ", flush=True)
            
            # Fetch all from SQLite
            items = sqlite_db.query(model).all()
            if not items:
                print("Empty.")
                continue

            # Clear existing data in Postgres (safety check)
            postgres_db.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"))
            
            # Convert to dictionary and insert
            count = 0
            for item in items:
                # Copy attributes
                data = {c.name: getattr(item, c.name) for c in item.__table__.columns}
                new_item = model(**data)
                postgres_db.add(new_item)
                count += 1
            
            postgres_db.commit()
            print(f"Done. Migrated {count} rows.")

        # Re-enable triggers/constraints
        postgres_db.execute(text("SET session_replication_role = 'origin'"))

        # 3. Synchronize Serial sequences in Postgres
        print("\nSynchronizing PostgreSQL sequences...")
        for model in MODELS:
            table_name = model.__tablename__
            # Find the primary key column (usually 'id')
            pk_col = "id" # Most of our models use 'id'
            
            # Find the max ID and set the sequence to it
            postgres_db.execute(text(f"SELECT setval(pg_get_serial_sequence('{table_name}', '{pk_col}'), (SELECT MAX({pk_col}) FROM {table_name}))"))
        
        postgres_db.commit()
        print("\nSUCCESS: Migration completed successfully!")

    except Exception as e:
        print(f"\nERROR during migration: {str(e)}")
        postgres_db.rollback()
    finally:
        sqlite_db.close()
        postgres_db.close()

if __name__ == "__main__":
    migrate()
