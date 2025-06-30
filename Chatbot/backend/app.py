from flask import Flask, render_template
from routes.screen import screen_bp
from routes.follow_up import follow_up_bp
from flask_cors import CORS
import markdown
import os

app = Flask(__name__)
CORS(app)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

