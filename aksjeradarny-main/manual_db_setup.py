#!/usr/bin/env python3
"""
Manual database creation and notification testing
"""
import sqlite3
import os

def create_notification_tables():
    """Create notification tables manually"""
    db_path = '/workspaces/aksjeradarv6/app.db'
    
    # Remove existing database to start fresh
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Removed existing database")
    
    # Create connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Creating tables...")
    
    # Create users table (basic version)
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(64) UNIQUE,
            email VARCHAR(120) UNIQUE,
            password_hash VARCHAR(128),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            has_subscription BOOLEAN DEFAULT 0,
            subscription_type VARCHAR(20) DEFAULT 'free',
            is_admin BOOLEAN DEFAULT 0
        )
    ''')
    
    # Create notifications table
    cursor.execute('''
        CREATE TABLE notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            type VARCHAR(50) NOT NULL,
            is_read BOOLEAN NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            read_at DATETIME,
            data TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create price_alerts table
    cursor.execute('''
        CREATE TABLE price_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ticker VARCHAR(20) NOT NULL,
            condition VARCHAR(10) NOT NULL,
            target_price REAL NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            triggered_at DATETIME,
            notification_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (notification_id) REFERENCES notifications (id)
        )
    ''')
    
    # Create notification_settings table
    cursor.execute('''
        CREATE TABLE notification_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            price_alerts_enabled BOOLEAN NOT NULL DEFAULT 1,
            news_alerts_enabled BOOLEAN NOT NULL DEFAULT 1,
            portfolio_alerts_enabled BOOLEAN NOT NULL DEFAULT 1,
            ai_insights_enabled BOOLEAN NOT NULL DEFAULT 1,
            email_notifications BOOLEAN NOT NULL DEFAULT 0,
            push_notifications BOOLEAN NOT NULL DEFAULT 1,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create ai_models table
    cursor.execute('''
        CREATE TABLE ai_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            model_type VARCHAR(50) NOT NULL,
            version VARCHAR(20) NOT NULL,
            accuracy REAL,
            training_date DATETIME,
            parameters TEXT,
            is_active BOOLEAN NOT NULL DEFAULT 0,
            is_production BOOLEAN NOT NULL DEFAULT 0,
            model_path VARCHAR(255),
            scaler_path VARCHAR(255),
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create prediction_logs table
    cursor.execute('''
        CREATE TABLE prediction_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER NOT NULL,
            ticker VARCHAR(20) NOT NULL,
            prediction_type VARCHAR(50) NOT NULL,
            predicted_value REAL NOT NULL,
            actual_value REAL,
            confidence REAL,
            prediction_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            target_date DATETIME NOT NULL,
            features_used TEXT,
            market_conditions TEXT,
            FOREIGN KEY (model_id) REFERENCES ai_models (id)
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX ix_notifications_user_id ON notifications (user_id)')
    cursor.execute('CREATE INDEX ix_notifications_created_at ON notifications (created_at)')
    cursor.execute('CREATE INDEX ix_price_alerts_user_id ON price_alerts (user_id)')
    cursor.execute('CREATE INDEX ix_price_alerts_ticker ON price_alerts (ticker)')
    cursor.execute('CREATE INDEX ix_prediction_logs_ticker ON prediction_logs (ticker)')
    cursor.execute('CREATE INDEX ix_prediction_logs_prediction_date ON prediction_logs (prediction_date)')
    
    # Insert test user
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, has_subscription, is_admin)
        VALUES ('testuser', 'test@example.com', 'dummy_hash', 1, 1)
    ''')
    
    # Insert test notification
    cursor.execute('''
        INSERT INTO notifications (user_id, title, message, type)
        VALUES (1, 'Velkommen!', 'Velkommen til Aksjeradar varselsystem!', 'system_alert')
    ''')
    
    # Insert test notification settings
    cursor.execute('''
        INSERT INTO notification_settings (user_id)
        VALUES (1)
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database created successfully at: {db_path}")
    print("✅ Test user created (ID: 1)")
    print("✅ Test notification created")
    print("\nReady to test notification system!")

if __name__ == '__main__':
    create_notification_tables()
