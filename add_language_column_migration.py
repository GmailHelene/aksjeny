# Migration script to add 'language' column to notification_settings table if missing
from app import db, create_app
from sqlalchemy import text


def add_language_column():
    app = create_app()
    with app.app_context():
        with db.engine.connect() as conn:
            dialect = conn.engine.dialect.name
            column_exists = False
            if dialect == 'sqlite':
                result = conn.execute(text("PRAGMA table_info(notification_settings);"))
                for row in result:
                    # row[1] is the column name in PRAGMA table_info
                    if row[1] == 'language':
                        column_exists = True
                        break
            else:
                result = conn.execute(text("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name='notification_settings' AND column_name='language';
                """))
                if result.fetchone():
                    column_exists = True
            if not column_exists:
                print("Adding 'language' column to notification_settings...")
                conn.execute(text("ALTER TABLE notification_settings ADD COLUMN language VARCHAR(10) DEFAULT 'en';"))
                print("Column added.")
            else:
                print("'language' column already exists.")

if __name__ == "__main__":
    add_language_column()
