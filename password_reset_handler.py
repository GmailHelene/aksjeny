import os
import psycopg2
import secrets
import hashlib
from datetime import datetime, timedelta

# Hardcoded Railway database URL for production
RAILWAY_DATABASE_URL = "postgresql://postgres:PsOJBeRqPAAcXyOXYCJvidJqMOpSzhqN@crossover.proxy.rlwy.net:17830/railway"

class PasswordResetHandler:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL') or RAILWAY_DATABASE_URL
        if self.db_url == RAILWAY_DATABASE_URL:
            print("🔧 Using hardcoded Railway database URL")
        else:
            print("✅ Using DATABASE_URL from environment")
    
    def generate_reset_token(self):
        """Generate a secure reset token"""
        return secrets.token_urlsafe(32)
    
    def create_reset_request(self, email):
        """Create a password reset request for a user"""
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if not user:
                return {"success": False, "message": "User not found"}
            
            user_id = user[0]
            
            # Generate token and expiry (24 hours from now)
            reset_token = self.generate_reset_token()
            expires_at = datetime.now() + timedelta(hours=24)
            
            # Update user with reset token
            cursor.execute("""
                UPDATE users 
                SET reset_token = %s, reset_token_expires = %s 
                WHERE id = %s
            """, (reset_token, expires_at, user_id))
            
            conn.commit()
            
            print(f"✅ Reset token created for user {email}")
            print(f"Token: {reset_token}")
            print(f"Expires: {expires_at}")
            
            return {
                "success": True, 
                "token": reset_token,
                "expires": expires_at,
                "message": "Reset token created successfully"
            }
            
        except Exception as e:
            print(f"❌ Error creating reset request: {e}")
            return {"success": False, "message": str(e)}
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    def verify_reset_token(self, token):
        """Verify if a reset token is valid and not expired"""
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, email, reset_token_expires 
                FROM users 
                WHERE reset_token = %s
            """, (token,))
            
            result = cursor.fetchone()
            
            if not result:
                return {"valid": False, "message": "Invalid token"}
            
            user_id, email, expires_at = result
            
            if datetime.now() > expires_at:
                return {"valid": False, "message": "Token expired"}
            
            return {
                "valid": True, 
                "user_id": user_id, 
                "email": email,
                "message": "Token is valid"
            }
            
        except Exception as e:
            print(f"❌ Error verifying token: {e}")
            return {"valid": False, "message": str(e)}
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    def reset_password(self, token, new_password):
        """Reset password using a valid token"""
        # First verify the token
        token_result = self.verify_reset_token(token)
        
        if not token_result["valid"]:
            return token_result
        
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            # Hash the new password (you should use bcrypt in production)
            password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            
            # Update password and clear reset token
            cursor.execute("""
                UPDATE users 
                SET password = %s, reset_token = NULL, reset_token_expires = NULL
                WHERE id = %s
            """, (password_hash, token_result["user_id"]))
            
            conn.commit()
            
            print(f"✅ Password reset successful for user {token_result['email']}")
            
            return {"success": True, "message": "Password reset successfully"}
            
        except Exception as e:
            print(f"❌ Error resetting password: {e}")
            return {"success": False, "message": str(e)}
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    def list_users(self):
        """List all users in the database"""
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, email, username FROM users LIMIT 10")
            users = cursor.fetchall()
            
            if users:
                print("📋 Users in database:")
                for user_id, email, username in users:
                    print(f"  - ID: {user_id}, Email: {email}, Username: {username}")
                return users
            else:
                print("❌ No users found in database")
                return []
                
        except Exception as e:
            print(f"❌ Error listing users: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    def create_test_user(self, email="test@example.com", username="testuser"):
        """Create a test user for testing password reset"""
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                print(f"✅ Test user {email} already exists")
                return True
            
            # Create test user with hashed password
            password_hash = hashlib.sha256("testpassword123".encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO users (email, username, password, created_at) 
                VALUES (%s, %s, %s, %s)
            """, (email, username, password_hash, datetime.now()))
            
            conn.commit()
            print(f"✅ Test user created: {email}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating test user: {e}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

# Test function
def test_password_reset():
    """Test the password reset functionality"""
    handler = PasswordResetHandler()
    
    print("🧪 Testing password reset functionality...")
    
    # First, list existing users
    users = handler.list_users()
    
    # If no users, create a test user
    if not users:
        print("\n🔧 No users found, creating test user...")
        if not handler.create_test_user():
            print("❌ Failed to create test user")
            return
    
    # Use first existing user or test user
    if users:
        test_email = users[0][1]  # Use first user's email
        print(f"\n🧪 Testing with existing user: {test_email}")
    else:
        test_email = "test@example.com"
        print(f"\n🧪 Testing with test user: {test_email}")
    
    # Create reset request
    result = handler.create_reset_request(test_email)
    print(f"Create request result: {result}")
    
    if result["success"]:
        token = result["token"]
        
        # Verify token
        verify_result = handler.verify_reset_token(token)
        print(f"Verify token result: {verify_result}")
        
        if verify_result["valid"]:
            print("✅ Password reset functionality is working!")
            print(f"✅ Reset token: {token}")
            print(f"✅ Token expires: {result['expires']}")
        else:
            print("❌ Token verification failed")
    else:
        print("❌ Failed to create reset request")

if __name__ == "__main__":
    test_password_reset()
