# Migration script to add 'language' column to notification_settings table if missing
from app import db, create_app
from sqlalchemy import text


def add_language_column():
    app = create_app()
    with app.app_context():
        try:
            # Check if column exists using SQLAlchemy 2.0+ syntax
            column_exists = False
            
            # Use db.session.execute instead of engine.execute
            result = db.session.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name='notification_settings' AND column_name='language';
            """))
            
            if result.fetchone():
                column_exists = True
                
            if not column_exists:
                print("Adding 'language' column to notification_settings...")
                db.session.execute(text("ALTER TABLE notification_settings ADD COLUMN language VARCHAR(10) DEFAULT 'en';"))
                db.session.commit()
                print("✅ Language column added successfully!")
            else:
                print("ℹ️ 'language' column already exists.")
                
        except Exception as e:
            print(f"❌ Error in migration: {e}")
            db.session.rollback()

if __name__ == "__main__":
    add_language_column()
