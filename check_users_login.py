import os
import psycopg2
import hashlib
import getpass
from werkzeug.security import check_password_hash

# Set database URL
RAILWAY_DATABASE_URL = "postgresql://postgres:PsOJBeRqPAAcXyOXYCJvidJqMOpSzhqN@crossover.proxy.rlwy.net:17830/railway"

def get_database_url():
        else:
            print(f"❌ Incorrect password for {email}")
            print(f"Provided hash: {hashlib.sha256(password.encode()).hexdigest()[:20]}...")
            print(f"Stored hash: {stored_password_hash[:20] if stored_password_hash else 'None'}...")
            return Falsecheck_password_hash

# Set database URL
RAILWAY_DATABASE_URL = "postgresql://postgres:PsOJBeRqPAAcXyOXYCJvidJqMOpSzhqN@crossover.proxy.rlwy.net:17830/railway"

def get_database_url():
    # Always use Railway PostgreSQL URL, not SQLite
    return "postgresql://postgres:PsOJBeRqPAAcXyOXYCJvidJqMOpSzhqN@crossover.proxy.rlwy.net:17830/railway"

def list_all_users():
    """List all users with their information"""
    db_url = get_database_url()
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Get all users with their columns
        cursor.execute("""
            SELECT id, email, username, password_hash, created_at, reset_token, reset_token_expires
            FROM users 
            ORDER BY id;
        """)
        
        users = cursor.fetchall()
        
        if users:
            print("👥 All users in database:")
            print("=" * 80)
            for user_id, email, username, password_hash, created_at, reset_token, reset_expires in users:
                print(f"ID: {user_id}")
                print(f"Email: {email}")
                print(f"Username: {username}")
                print(f"Password Hash: {password_hash[:20]}..." if password_hash else "No password")
                print(f"Created: {created_at}")
                print(f"Reset Token: {'Yes' if reset_token else 'No'}")
                print(f"Token Expires: {reset_expires if reset_expires else 'N/A'}")
                print("-" * 40)
            
            return users
        else:
            print("❌ No users found in database!")
            return []
            
    except Exception as e:
        print(f"❌ Error listing users: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def test_login(email, password):
    """Test if email/password combination works"""
    db_url = get_database_url()
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Get user by email
        cursor.execute("SELECT id, email, password_hash FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User with email {email} not found")
            return False
        
        user_id, user_email, stored_password_hash = user
        
        # Hash the provided password (assuming SHA256 - adjust if different)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if password_hash == stored_password:
            print(f"✅ Login successful for {email}")
            return True
        else:
            print(f"❌ Incorrect password for {email}")
            print(f"Provided hash: {password_hash[:20]}...")
            print(f"Stored hash: {stored_password[:20]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error testing login: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def create_test_user():
    """Create a test user with known credentials"""
    db_url = get_database_url()
    
    email = "test@example.com"
    username = "testuser"
    password = "testpassword123"
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            print(f"✅ Test user {email} already exists")
            return email, password
        
        # Create test user with hashed password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute("""
            INSERT INTO users (email, username, password, created_at) 
            VALUES (%s, %s, %s, NOW())
        """, (email, username, password_hash))
        
        conn.commit()
        print(f"✅ Test user created:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        return email, password
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return None, None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def main():
    print("🔍 Checking user login information...")
    print("=" * 50)
    
    # List all users
    users = list_all_users()
    
    if not users:
        print("\n🔧 No users found. Creating test user...")
        email, password = create_test_user()
        if email and password:
            print(f"\n🧪 Testing login with test user...")
            test_login(email, password)
    else:
        print(f"\n🧪 Testing login functionality...")
        
        # Test with first user
        if users:
            first_user = users[0]
            email = first_user[1]  # email is second column
            
            print(f"\nTo test login for {email}:")
            print("1. Try common passwords: password, 123456, admin, etc.")
            print("2. Or if you know the password, test it below")
            
            test_password = getpass.getpass(f"Enter password for {email} (or press Enter to skip): ")
            if test_password:
                test_login(email, test_password)
        
        # Offer to create a test user
        create_test = input("\nCreate test user with known password? (y/n): ")
        if create_test.lower() == 'y':
            email, password = create_test_user()
            if email and password:
                test_login(email, password)

if __name__ == "__main__":
    main()
