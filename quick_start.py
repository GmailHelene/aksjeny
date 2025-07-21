import os
import sys

# Set all required environment variables
os.environ['EMAIL_USERNAME'] = 'support@luxushair.com'
os.environ['EMAIL_PASSWORD'] = 'suetozoydejwntii'
os.environ['EMAIL_PORT'] = '587'
os.environ['EMAIL_SERVER'] = 'imap.gmail.com'
os.environ['DATABASE_URL'] = 'postgresql://postgres:PsOJBeRqPAAcXyOXYCJvidJqMOpSzhqN@crossover.proxy.rlwy.net:17830/railway'

print("🚀 Quick Starting Flask Server...")
print("🌐 Server will be at: http://localhost:5000")
print("🔗 Reset password page: http://localhost:5000/reset-password")
print("\nDO NOT CLOSE THIS TERMINAL!")
print("=" * 50)

# Import and run Flask app
from app import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
