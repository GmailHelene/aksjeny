import os
from flask import Flask, request

# Set environment variables
os.environ['EMAIL_USERNAME'] = 'support@luxushair.com'
os.environ['EMAIL_PASSWORD'] = 'suetozoydejwntii'
os.environ['EMAIL_PORT'] = '587'
os.environ['EMAIL_SERVER'] = 'imap.gmail.com'
os.environ['DATABASE_URL'] = 'postgresql://postgres:PsOJBeRqPAAcXyOXYCJvidJqMOpSzhqN@crossover.proxy.rlwy.net:17830/railway'

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>Password Reset Test Server</h1>
    <p><a href="/reset-password?token=TEST">Test Reset Password</a></p>
    <p>Server is running successfully!</p>
    '''

@app.route('/reset-password')
def reset_password():
    token = request.args.get('token')
    return f'''
    <h1>Reset Password</h1>
    <p>Token: {token}</p>
    <form method="POST">
        <p>New Password: <input type="password" name="password" required></p>
        <button type="submit">Reset</button>
    </form>
    '''

if __name__ == '__main__':
    print("🚀 Starting simple test server...")
    print("🌐 Go to: http://localhost:8000")
    app.run(debug=True, host='0.0.0.0', port=8000)
