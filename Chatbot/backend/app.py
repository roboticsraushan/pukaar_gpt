from flask import Flask
from routes.screen import screen_bp
from routes.follow_up import follow_up_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(screen_bp)
app.register_blueprint(follow_up_bp, url_prefix="/api/followup")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

