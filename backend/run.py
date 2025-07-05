from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, date
import os
import time
import json
import requests
import re
from urllib.parse import urlparse, quote
from bs4 import BeautifulSoup
import hashlib
import secrets
import plag
import aicontentdetector
import web_plagiarism

# Rate limiting configuration
DAILY_DOCUMENT_LIMIT = 25

# User management functions
def get_users_db_path():
    """Get path to users database file"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, 'users.json')

def load_users():
    """Load users from database"""
    users_path = get_users_db_path()
    if os.path.exists(users_path):
        try:
            with open(users_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_users(users_data):
    """Save users to database"""
    users_path = get_users_db_path()
    try:
        with open(users_path, 'w') as f:
            json.dump(users_data, f, indent=2)
    except IOError as e:
        print(f"ERROR: Failed to save users data: {str(e)}")

def hash_password(password):
    """Hash password for secure storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify password against hash"""
    return hashlib.sha256(password.encode()).hexdigest() == hashed

def create_user(username, email, password):
    """Create a new user"""
    users = load_users()

    # Check if user already exists
    if username in users:
        return False, "Username already exists"

    # Check if email already exists
    for user_data in users.values():
        if user_data.get('email') == email:
            return False, "Email already registered"

    # Create new user
    users[username] = {
        'email': email,
        'password': hash_password(password),
        'created_date': datetime.now().isoformat(),
        'daily_usage': {}
    }

    save_users(users)
    return True, "User created successfully"

def authenticate_user(username, password):
    """Authenticate user login"""
    users = load_users()

    if username not in users:
        return False, "Username not found"

    if verify_password(password, users[username]['password']):
        return True, "Login successful"
    else:
        return False, "Invalid password"

def get_current_user():
    """Get current logged-in user"""
    return session.get('username')

def get_user_ip():
    """Get user's IP address"""
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']

def get_usage_log_path():
    """Get path to usage log file"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, 'daily_usage.json')

def load_daily_usage():
    """Load daily usage data from file"""
    log_path = get_usage_log_path()
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_daily_usage(usage_data):
    """Save daily usage data to file"""
    log_path = get_usage_log_path()
    try:
        with open(log_path, 'w') as f:
            json.dump(usage_data, f, indent=2)
    except IOError as e:
        print(f"ERROR: Failed to save usage data: {str(e)}")

def check_daily_limit(user_identifier):
    """Check if user has exceeded daily document limit"""
    # For logged-in users, use username; for guests, use IP
    current_user = get_current_user()
    if current_user:
        # User-based tracking
        users = load_users()
        if current_user in users:
            today = date.today().isoformat()
            user_usage = users[current_user].get('daily_usage', {})
            user_count = user_usage.get(today, 0)
            return user_count < DAILY_DOCUMENT_LIMIT, user_count
    else:
        # IP-based tracking for guests
        usage_data = load_daily_usage()
        today = date.today().isoformat()

        # Clean up old data (keep only today's data)
        usage_data = {k: v for k, v in usage_data.items() if k == today}

        if today not in usage_data:
            usage_data[today] = {}

        user_count = usage_data[today].get(user_identifier, 0)
        return user_count < DAILY_DOCUMENT_LIMIT, user_count

    return False, 0

def increment_daily_usage(user_identifier):
    """Increment user's daily document count"""
    current_user = get_current_user()
    if current_user:
        # User-based tracking
        users = load_users()
        if current_user in users:
            today = date.today().isoformat()
            if 'daily_usage' not in users[current_user]:
                users[current_user]['daily_usage'] = {}
            users[current_user]['daily_usage'][today] = users[current_user]['daily_usage'].get(today, 0) + 1
            save_users(users)
    else:
        # IP-based tracking for guests
        usage_data = load_daily_usage()
        today = date.today().isoformat()

        if today not in usage_data:
            usage_data[today] = {}

        usage_data[today][user_identifier] = usage_data[today].get(user_identifier, 0) + 1
        save_daily_usage(usage_data)

# Fix the template folder path - make sure it's absolute
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(os.path.dirname(current_dir), 'frontend', 'templates')
static_dir = os.path.join(os.path.dirname(current_dir), 'frontend', 'static')

# Create necessary directories
if not os.path.exists(template_dir):
    os.makedirs(template_dir)
    print(f"Created template directory: {template_dir}")

if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    print(f"Created static directory: {static_dir}")

# Create CSS directory if it doesn't exist
css_dir = os.path.join(static_dir, 'css')
if not os.path.exists(css_dir):
    os.makedirs(css_dir)
    print(f"Created CSS directory: {css_dir}")

# Create AI CONTENT directory if it doesn't exist
ai_content_dir = os.path.join(os.path.dirname(current_dir), 'AI CONTENT')
if not os.path.exists(ai_content_dir):
    os.makedirs(ai_content_dir)
    print(f"Created AI CONTENT directory: {ai_content_dir}")

# Check if AI content dataset exists, create a simple one if not
ai_dataset_path = os.path.join(ai_content_dir, 'Training_Essay_Data.csv')
if not os.path.exists(ai_dataset_path):
    print(f"AI content dataset not found, creating a simple placeholder")
    try:
        import pandas as pd
        # Create a simple dataset with a few examples
        data = {
            'text': [
                "This is human-written text for testing purposes.",
                "This text was generated by an AI model for testing.",
                "Humans write text with varied structure and occasional errors.",
                "AI generated text tends to be more formal and structured."
            ],
            'generated': [0, 1, 0, 1]  # 0 = human, 1 = AI
        }
        df = pd.DataFrame(data)
        df.to_csv(ai_dataset_path, index=False)
        print(f"Created placeholder AI dataset at {ai_dataset_path}")
    except Exception as e:
        print(f"Failed to create placeholder dataset: {str(e)}")

print(f"DEBUG: Template directory: {template_dir} (exists: {os.path.exists(template_dir)})")
print(f"DEBUG: Static directory: {static_dir} (exists: {os.path.exists(static_dir)})")

app = Flask(__name__,
           template_folder=template_dir,
           static_folder=static_dir)

# Configure session
app.secret_key = secrets.token_hex(16)  # Generate a random secret key
app.config['SESSION_TYPE'] = 'filesystem'

@app.route("/", methods=["GET"])
def index():
    current_user = get_current_user()
    return render_template('index_cyberpunk.html', current_user=current_user)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # Validation
        if not username or not email or not password:
            flash("All fields are required", "error")
        elif len(username) < 3:
            flash("Username must be at least 3 characters long", "error")
        elif len(password) < 6:
            flash("Password must be at least 6 characters long", "error")
        elif password != confirm_password:
            flash("Passwords do not match", "error")
        else:
            success, message = create_user(username, email, password)
            if success:
                flash("Account created successfully! Please log in.", "success")
                return redirect(url_for('login'))
            else:
                flash(message, "error")

    return render_template('signup.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash("Username and password are required", "error")
        else:
            success, message = authenticate_user(username, password)
            if success:
                session['username'] = username
                flash("Login successful!", "success")
                return redirect(url_for('index'))
            else:
                flash(message, "error")

    return render_template('login.html')

@app.route("/logout")
def logout():
    session.pop('username', None)
    flash("You have been logged out", "info")
    return redirect(url_for('index'))

@app.route("/text-input", methods=["GET", "POST"])
def text_input():
    result = None

    if request.method == "POST":
        # Check daily limit before processing
        current_user = get_current_user()
        user_identifier = current_user if current_user else get_user_ip()
        can_process, current_count = check_daily_limit(user_identifier)

        if not can_process:
            result = f"❌ Daily limit exceeded. You can only analyze {DAILY_DOCUMENT_LIMIT} documents per day. You have used {current_count}/{DAILY_DOCUMENT_LIMIT} today. Please try again tomorrow."
        else:
            option = request.form.get('option', 'Plagiarism Detector')
            text = request.form.get('text', '').strip()

            if not text:
                result = "❌ No text provided. Please enter text."
            else:
                word_count = len(text.split())
                if word_count > 100:
                    result = f"❌ Text exceeds 100 words (current: {word_count})"
                else:
                    try:
                        start_time = time.time()
                        print(f"DEBUG: Processing text with option: {option}")

                        if option == 'Plagiarism Detector':
                            # Local plagiarism check
                            local_result = plag.check_plagiarism(text)

                            # Web plagiarism check
                            web_result = web_plagiarism.check_web_plagiarism(text)

                            # Combine results
                            result = f"<strong>📁 Local Database Results:</strong><br>{local_result}<br><br>"
                            result += f"<strong>🌐 Web Search Results:</strong><br>{web_result}"

                        elif option == 'Web Plagiarism Detector':
                            result = web_plagiarism.check_web_plagiarism(text)
                        else:  # AI Content Detector
                            result = aicontentdetector.detect_ai_content(text)

                        processing_time = time.time() - start_time
                        print(f"DEBUG: Processing completed in {processing_time:.2f} seconds")
                        print(f"DEBUG: Result: {result}")

                        # Increment usage count after successful processing
                        increment_daily_usage(user_identifier)
                        remaining = DAILY_DOCUMENT_LIMIT - (current_count + 1)
                        result += f"<br><br>📊 Daily usage: {current_count + 1}/{DAILY_DOCUMENT_LIMIT} documents used today. {remaining} remaining."

                    except Exception as e:
                        import traceback
                        print(f"ERROR: Text processing failed - {str(e)}")
                        print(traceback.format_exc())
                        result = f"❌ Error processing text: {str(e)}"

    return render_template('text_input.html', result=result)

@app.route("/file-upload", methods=["GET", "POST"])
def file_upload():
    result = None

    if request.method == "POST":
        # Check daily limit before processing
        current_user = get_current_user()
        user_identifier = current_user if current_user else get_user_ip()
        can_process, current_count = check_daily_limit(user_identifier)

        if not can_process:
            result = f"❌ Daily limit exceeded. You can only analyze {DAILY_DOCUMENT_LIMIT} documents per day. You have used {current_count}/{DAILY_DOCUMENT_LIMIT} today. Please try again tomorrow."
        else:
            option = request.form.get('option', 'Plagiarism Detector')

            if 'file' not in request.files:
                result = "❌ No file part in the request"
            else:
                file = request.files['file']

                if file.filename == '':
                    result = "❌ No file selected"
                elif not file.filename.endswith('.txt'):
                    result = "❌ Only .txt files are supported"
                else:
                    try:
                        file_content = file.read().decode('utf-8', errors='ignore')

                        start_time = time.time()
                        if option == 'Plagiarism Detector':
                            # Local plagiarism check
                            local_result = plag.check_plagiarism(file_content)

                            # Web plagiarism check
                            web_result = web_plagiarism.check_web_plagiarism(file_content)

                            # Combine results
                            result = f"<strong>📁 Local Database Results:</strong><br>{local_result}<br><br>"
                            result += f"<strong>🌐 Web Search Results:</strong><br>{web_result}"

                        elif option == 'Web Plagiarism Detector':
                            result = web_plagiarism.check_web_plagiarism(file_content)
                        else:  # Default to AI Content Detector
                            result = aicontentdetector.detect_ai_content(file_content)

                        processing_time = time.time() - start_time
                        print(f"DEBUG: Processing completed in {processing_time:.2f} seconds")

                        # Increment usage count after successful processing
                        increment_daily_usage(user_identifier)
                        remaining = DAILY_DOCUMENT_LIMIT - (current_count + 1)
                        result += f"<br><br>📊 Daily usage: {current_count + 1}/{DAILY_DOCUMENT_LIMIT} documents used today. {remaining} remaining."

                        # Log successful upload
                        log_path = os.path.join(os.path.dirname(__file__), 'upload_log.txt')
                        with open(log_path, 'a') as log:
                            log.write(f"{file.filename} uploaded on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by {user_identifier}\n")

                    except Exception as e:
                        import traceback
                        print(f"ERROR: File processing failed - {str(e)}")
                        print(traceback.format_exc())
                        result = f"❌ Error processing file: {str(e)}"

    return render_template('file_upload.html', result=result)

@app.route("/test")
def test():
    return "<h1>Flask is working!</h1>"

@app.route("/usage-status", methods=["GET"])
def usage_status():
    """Check current daily usage status"""
    try:
        current_user = get_current_user()
        if current_user:
            user_identifier = current_user
            user_type = f"User: {current_user}"
        else:
            user_identifier = get_user_ip()
            user_type = f"Guest (IP: {user_identifier})"

        can_process, current_count = check_daily_limit(user_identifier)
        remaining = DAILY_DOCUMENT_LIMIT - current_count

        status = "✅ Available" if can_process else "❌ Limit Reached"

        return f"""
        <h1>Daily Usage Status</h1>
        <p><strong>Status:</strong> {status}</p>
        <p><strong>Documents used today:</strong> {current_count}/{DAILY_DOCUMENT_LIMIT}</p>
        <p><strong>Remaining:</strong> {remaining}</p>
        <p><strong>Account:</strong> {user_type}</p>
        <p><strong>Reset time:</strong> Tomorrow at midnight</p>
        <br>
        <a href="/">← Back to Home</a>
        """
    except Exception as e:
        return f"<h1>Error checking usage status</h1><p>{str(e)}</p>"

@app.route("/test-ai", methods=["GET"])
def test_ai():
    """Test route for AI content detection"""
    try:
        # Test with a simple text
        test_text = "This is a test text for AI content detection."
        result = aicontentdetector.detect_ai_content(test_text)
        return f"<h1>AI Detection Test</h1><p>Test text: '{test_text}'</p><p>Result: {result}</p>"
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"<h1>Error in AI Detection</h1><p>{str(e)}</p><pre>{error_details}</pre>"

if __name__ == "__main__":
    app.run(debug=True)
