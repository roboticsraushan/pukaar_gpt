from flask import Flask, render_template, session
from routes.screen import screen_bp
from routes.follow_up import follow_up_bp
from flask_cors import CORS
from flask_session import Session
import markdown
import os
import redis

app = Flask(__name__)
CORS(app)

# Configure Flask-Session with Redis
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'pukaar:'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours in seconds

# Set up Redis connection
redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = int(os.environ.get('REDIS_PORT', 6379))
redis_password = os.environ.get('REDIS_PASSWORD', None)
redis_db = int(os.environ.get('REDIS_DB', 0))

try:
    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        db=redis_db
    )
    redis_client.ping()  # Test connection
    print(f"[INFO] Connected to Redis at {redis_host}:{redis_port}")
    app.config['SESSION_REDIS'] = redis_client
except Exception as e:
    print(f"[WARNING] Redis connection failed: {e}. Using filesystem session.")
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = '/tmp/pukaar_sessions'
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

# Initialize Flask-Session
Session(app)

# Register blueprints
app.register_blueprint(screen_bp)
app.register_blueprint(follow_up_bp)

# Serve API documentation from markdown file
@app.route('/api-doc')
def api_documentation():
    try:
        # Read the markdown file - try multiple possible paths
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'API_DOCUMENTATION.md'),  # Relative to backend folder
            os.path.join(os.getcwd(), 'API_DOCUMENTATION.md'),  # Current working directory
            '/app/API_DOCUMENTATION.md',  # Docker container path
            'API_DOCUMENTATION.md'  # Direct path
        ]
        
        md_content = None
        used_path = None
        
        for path in possible_paths:
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    md_content = file.read()
                    used_path = path
                    break
            except FileNotFoundError:
                continue
        
        if md_content is None:
            # If file not found, return error with all attempted paths
            error_paths = '\n'.join([f"- {path}" for path in possible_paths])
            return f'''
            <!DOCTYPE html>
            <html>
            <head><title>Documentation Not Found</title></head>
            <body>
                <h1>Documentation Not Found</h1>
                <p>The API_DOCUMENTATION.md file was not found. Tried these paths:</p>
                <pre>{error_paths}</pre>
                <p>Current working directory: {os.getcwd()}</p>
                <p>Files in current directory: {os.listdir('.')}</p>
            </body>
            </html>
            ''', 404
        
        # Convert markdown to HTML
        html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables', 'codehilite'])
        
        # Render the template with the converted content
        return render_template('api_doc_template.html', content=html_content)
        
    except Exception as e:
        return f'''
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body>
            <h1>Error Loading Documentation</h1>
            <p>Error: {str(e)}</p>
            <p>Current working directory: {os.getcwd()}</p>
            <p>Files in current directory: {os.listdir('.')}</p>
        </body>
        </html>
        ''', 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check Redis connection
        redis_status = "Connected" if app.config['SESSION_TYPE'] == 'redis' and app.config['SESSION_REDIS'].ping() else "Not connected"
        
        return {
            "status": "healthy",
            "redis": redis_status,
            "session_type": app.config['SESSION_TYPE']
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

