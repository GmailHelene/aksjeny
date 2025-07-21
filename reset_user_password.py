import os
import psycopg2
import hashlib

RAILWAY_DATABASE_URL = "postgresql://postgres:PsOJBeRqPAAcXyOXYCJvidJqMOpSzhqN@crossover.proxy.rlwy.net:17830/railway"

def get_database_url():
    return os.getenv('DATABASE_URL') or RAILWAY_DATABASE_URL

def reset_user_password(email, new_password):
    """Reset a user's password to a known value"""
    db_url = get_database_url()
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User {email} not found")
            return False
        
        # Hash new password
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        # Update password
        cursor.execute("""
            UPDATE users 
            SET password = %s 
            WHERE email = %s
        """, (password_hash, email))
        
        conn.commit()
        
        print(f"✅ Password updated for {email}")
        print(f"   New password: {new_password}")
        return True
        
    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔒 Reset User Password")
    print("=" * 30)
    
    email = input("Enter user email: ")
    new_password = input("Enter new password: ")
    
    if email and new_password:
        reset_user_password(email, new_password)
    else:
        print("❌ Email and password required")
