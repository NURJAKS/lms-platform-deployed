from __future__ import annotations

from sqlalchemy import Engine, text

from app.core.database import engine


def _ensure_user_city_column(db_engine: Engine) -> None:
    """
    Backward‑compatible migration for legacy SQLite DBs that lack users.city.

    In older versions, the users table did not have the city column. Newer
    application versions expect it to exist, which causes "no such column:
    users.city" errors on any query against the users table.

    For SQLite databases only, we:
    - read PRAGMA table_info(users)
    - if the table exists and the city column is missing, run
      ALTER TABLE users ADD COLUMN city VARCHAR(100)
    """
    try:
        # Only run this lightweight migration for SQLite connections.
        url = str(db_engine.url)
        if "sqlite" not in url:
            return

        with db_engine.begin() as conn:
            result = conn.execute(text("PRAGMA table_info(users)"))
            rows = list(result)
            if not rows:
                # Table does not exist yet; fresh databases will be created
                # with the correct schema via Base.metadata.create_all.
                return

            column_names = {row[1] for row in rows}
            if "city" in column_names:
                return

            conn.execute(text("ALTER TABLE users ADD COLUMN city VARCHAR(100)"))
    except Exception:
        # Schema migration issues should not crash the API startup in dev;
        # failures will still surface as DB errors if they persist.
        return


def _ensure_user_teacher_columns(db_engine: Engine) -> None:
    """
    Backward‑compatible migration for legacy SQLite DBs that lack teacher profile fields on users.

    We store teacher profile fields on the users table for simplicity. For SQLite only:
    - read PRAGMA table_info(users)
    - add missing columns via ALTER TABLE ... ADD COLUMN ...
    """
    try:
        url = str(db_engine.url)
        if "sqlite" not in url:
            return

        needed_columns = {
            "gender": "VARCHAR(20)",
            "identity_card": "VARCHAR(100)",
            "iin": "VARCHAR(20)",
            # curator-specific fields (teacher role)
            # arrays/objects stored as JSON text in SQLite
            "curated_courses": "TEXT",
            "consultation_schedule": "TEXT",
            "consultation_location": "VARCHAR(255)",
            "can_view_performance": "BOOLEAN",
            "can_message_students": "BOOLEAN",
            "can_view_attendance": "BOOLEAN",
            "can_call_parent_teacher_meetings": "BOOLEAN",
            "can_create_group_announcements": "BOOLEAN",
            "education": "VARCHAR(500)",
            "academic_degree": "VARCHAR(255)",
            "email_work": "VARCHAR(255)",
            "phone_work": "VARCHAR(50)",
            "office": "VARCHAR(100)",
            "reception_hours": "VARCHAR(255)",
            "employee_number": "VARCHAR(100)",
            "position": "VARCHAR(255)",
            "department": "VARCHAR(255)",
            "hire_date": "DATE",
            "employment_status": "VARCHAR(50)",
            "academic_interests": "TEXT",
            "teaching_hours": "VARCHAR(100)",
            # arrays (stored as JSON text in SQLite)
            "subjects_taught": "TEXT",
            "student_counts": "TEXT",
            "status": "VARCHAR(20)",
            "interface_language": "VARCHAR(20)",
        }

        with db_engine.begin() as conn:
            result = conn.execute(text("PRAGMA table_info(users)"))
            rows = list(result)
            if not rows:
                return
            existing = {row[1] for row in rows}
            for name, ddl_type in needed_columns.items():
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {name} {ddl_type}"))
    except Exception:
        return


def _ensure_user_admin_columns(db_engine: Engine) -> None:
    """
    Backward‑compatible migration for legacy SQLite DBs that lack admin profile fields on users.

    We store admin profile fields on the users table for simplicity. For SQLite only:
    - read PRAGMA table_info(users)
    - add missing columns via ALTER TABLE ... ADD COLUMN ...
    """
    try:
        url = str(db_engine.url)
        if "sqlite" not in url:
            return

        needed_columns = {
            "education_level": "VARCHAR(255)",
            "email_personal": "VARCHAR(255)",
            "system_role": "VARCHAR(50)",
            # arrays (stored as JSON text in SQLite)
            "permissions": "TEXT",
            "areas_of_responsibility": "TEXT",
            "can_create_users": "BOOLEAN",
            "can_delete_users": "BOOLEAN",
            "can_edit_courses": "BOOLEAN",
            "can_view_analytics": "BOOLEAN",
            "can_configure_system": "BOOLEAN",
        }

        with db_engine.begin() as conn:
            result = conn.execute(text("PRAGMA table_info(users)"))
            rows = list(result)
            if not rows:
                return
            existing = {row[1] for row in rows}
            for name, ddl_type in needed_columns.items():
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {name} {ddl_type}"))
    except Exception:
        return


def _ensure_user_parent_columns(db_engine: Engine) -> None:
    """
    Backward‑compatible migration for legacy SQLite DBs that lack parent profile fields on users.
    """
    try:
        url = str(db_engine.url)
        if "sqlite" not in url:
            return

        needed_columns = {
            "work_place": "VARCHAR(255)",
            "kinship_degree": "VARCHAR(20)",
            "educational_process_role": "VARCHAR(30)",
        }

        with db_engine.begin() as conn:
            result = conn.execute(text("PRAGMA table_info(users)"))
            rows = list(result)
            if not rows:
                return
            existing = {row[1] for row in rows}
            for name, ddl_type in needed_columns.items():
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {name} {ddl_type}"))
    except Exception:
        return


def _ensure_student_profile_iin_column(db_engine: Engine) -> None:
    """
    Backward‑compatible migration for legacy SQLite DBs that lack student_profiles.iin.
    """
    try:
        url = str(db_engine.url)
        if "sqlite" not in url:
            return

        with db_engine.begin() as conn:
            result = conn.execute(text("PRAGMA table_info(student_profiles)"))
            rows = list(result)
            if not rows:
                return
            existing = {row[1] for row in rows}
            if "iin" not in existing:
                conn.execute(text("ALTER TABLE student_profiles ADD COLUMN iin VARCHAR(20)"))
    except Exception:
        return


def _ensure_course_applications_columns(db_engine: Engine) -> None:
    """
    Backward‑compatible migration for legacy SQLite DBs that lack the extended
    fields on course_applications (city, parent_*).
    """
    try:
        url = str(db_engine.url)
        if "sqlite" not in url:
            return

        needed_columns = {
            "city": "VARCHAR(100)",
            "parent_email": "VARCHAR(255)",
            "parent_full_name": "VARCHAR(255)",
            "parent_phone": "VARCHAR(50)",
            "parent_city": "VARCHAR(100)",
            # новые поля анкеты студента и родителя
            "student_birth_date": "DATE",
            "student_age": "INTEGER",
            "student_iin": "VARCHAR(30)",
            "parent_birth_date": "DATE",
            "parent_age": "INTEGER",
            "parent_iin": "VARCHAR(30)",
        }

        with db_engine.begin() as conn:
            result = conn.execute(text("PRAGMA table_info(course_applications)"))
            rows = list(result)
            if not rows:
                return
            existing = {row[1] for row in rows}
            for name, ddl_type in needed_columns.items():
                if name not in existing:
                    conn.execute(
                        text(f"ALTER TABLE course_applications ADD COLUMN {name} {ddl_type}")
                    )
    except Exception:
        # Schema migration issues should not crash the API startup in dev;
        # failures will still surface as DB errors if they persist.
        return


def _ensure_teacher_materials_columns(db_engine: Engine) -> None:
    """
    Backward‑compatible migration for teacher_materials table.
    """
    try:
        url = str(db_engine.url)
        if "sqlite" not in url:
            return

        needed_columns = {
            "attachment_urls": "TEXT",
            "attachment_links": "TEXT",
        }

        with db_engine.begin() as conn:
            result = conn.execute(text("PRAGMA table_info(teacher_materials)"))
            rows = list(result)
            if not rows:
                return
            existing = {row[1] for row in rows}
            for name, ddl_type in needed_columns.items():
                if name not in existing:
                    conn.execute(
                        text(f"ALTER TABLE teacher_materials ADD COLUMN {name} {ddl_type}")
                    )
    except Exception:
        return


def _ensure_student_progress_updated_at_column(db_engine: Engine) -> None:
    """
    Backward‑compatible migration for legacy SQLite DBs that lack student_progress.updated_at.

    Newer code expects the column to exist (see StudentProgress model). Without it,
    any ORM query against student_progress fails with:
      sqlite3.OperationalError: no such column: student_progress.updated_at
    """
    try:
        url = str(db_engine.url)
        if "sqlite" not in url:
            return

        with db_engine.begin() as conn:
            result = conn.execute(text("PRAGMA table_info(student_progress)"))
            rows = list(result)
            if not rows:
                return
            existing = {row[1] for row in rows}
            if "updated_at" in existing:
                return

            # SQLite supports adding a nullable column via ALTER TABLE.
            conn.execute(text("ALTER TABLE student_progress ADD COLUMN updated_at DATETIME"))
    except Exception:
        return


def _ensure_user_purchases_price_paid_column(db_engine: Engine) -> None:
    """Add price_paid column to user_purchases for correct refund calculations."""
    try:
        url = str(db_engine.url)
        if "sqlite" not in url:
            return

        with db_engine.begin() as conn:
            result = conn.execute(text("PRAGMA table_info(user_purchases)"))
            rows = list(result)
            if not rows:
                return
            existing = {row[1] for row in rows}
            if "price_paid" not in existing:
                conn.execute(text("ALTER TABLE user_purchases ADD COLUMN price_paid INTEGER"))
    except Exception:
        return


def run_migrations() -> None:
    """Entry point for running lightweight, in‑app migrations."""
    _ensure_user_city_column(engine)
    _ensure_user_teacher_columns(engine)
    _ensure_user_admin_columns(engine)
    _ensure_user_parent_columns(engine)
    _ensure_student_profile_iin_column(engine)
    _ensure_course_applications_columns(engine)
    _ensure_teacher_materials_columns(engine)
    _ensure_student_progress_updated_at_column(engine)
    _ensure_user_purchases_price_paid_column(engine)

