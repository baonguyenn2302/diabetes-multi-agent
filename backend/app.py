"""Flask application factory. Run with `cd backend; python app.py`."""
from __future__ import annotations
import logging
import tempfile
from pathlib import Path
from flask import Flask, jsonify
from flask_cors import CORS

try:
    from .config import Config
    from .routes.chat import chat_bp
    from .routes.agents import agents_bp
    from .routes.health import health_bp
    from .routes.history import history_bp
    from .services.sqlite_service import SQLiteService
except ImportError:  # Support `cd backend; python app.py` and `flask --app app run`
    from config import Config
    from routes.chat import chat_bp
    from routes.agents import agents_bp
    from routes.health import health_bp
    from routes.history import history_bp
    from services.sqlite_service import SQLiteService


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    CORS(app, resources={r"/api/*": {"origins": app.config["FRONTEND_ORIGINS"]}})
    # Give each isolated test app its own temporary database unless explicitly overridden.
    # Keep the TemporaryDirectory handle alive for the entire app lifetime.
    if app.config.get("TESTING") and not (test_config or {}).get("SQLITE_PATH"):
        tmp = tempfile.TemporaryDirectory(prefix="diabetes_agent_tests_")
        app.extensions["sqlite_test_directory"] = tmp
        app.config["SQLITE_PATH"] = str(Path(tmp.name) / "test.sqlite3")
    app.extensions["sqlite_service"] = SQLiteService(app.config["SQLITE_PATH"])
    app.register_blueprint(chat_bp)
    app.register_blueprint(agents_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(history_bp)

    @app.errorhandler(413)
    def request_too_large(exc):
        return jsonify({"status": "invalid_input", "error": "Request JSON quá lớn (tối đa 64 KiB)."}), 413

    @app.errorhandler(404)
    def route_not_found(exc):
        return jsonify({"status": "error", "error": "API không tồn tại."}), 404

    return app


if __name__ == "__main__":
    app = create_app()
    # Demo only: accessible from the same computer, never expose debug console.
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
