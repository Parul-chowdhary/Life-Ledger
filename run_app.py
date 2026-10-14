"""
LifeLedger Application Server & Factory.
Initializes database connections, creates tables, mounts blueprints,
and runs the local development server.
"""
import os
import sys
from pathlib import Path

# Fix Windows console encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add all internal packages to sys.path so modules resolve cleanly without pip install -e
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR / "packages" / "lifeledger-core" / "src"))
sys.path.insert(0, str(ROOT_DIR / "packages" / "lifeledger-models" / "src"))
sys.path.insert(0, str(ROOT_DIR / "packages" / "lifeledger-repositories" / "src"))
sys.path.insert(0, str(ROOT_DIR / "packages" / "lifeledger-services" / "src"))
sys.path.insert(0, str(ROOT_DIR / "packages" / "lifeledger-web" / "src"))
sys.path.insert(0, str(ROOT_DIR / "packages" / "lifeledger-api" / "src"))

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from lifeledger_api import api_v1_bp
from lifeledger_core.config import settings
from lifeledger_models.base import Base
from lifeledger_web import web_bp


def create_app() -> Flask:
    """Application factory for LifeLedger."""
    app = Flask(
        __name__,
        static_folder=str(ROOT_DIR / "packages" / "lifeledger-web" / "src" / "lifeledger_web" / "static"),
        template_folder=str(ROOT_DIR / "packages" / "lifeledger-web" / "src" / "lifeledger_web" / "templates"),
    )
    app.config["SECRET_KEY"] = settings.secret_key
    app.config["MAX_CONTENT_LENGTH"] = settings.max_upload_size_bytes

    # Ensure instance directory exists
    instance_dir = ROOT_DIR / "instance"
    instance_dir.mkdir(parents=True, exist_ok=True)

    # Initialize SQLAlchemy database engine
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
        echo=False,
    )
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db_session = scoped_session(session_factory)

    app.extensions["sqlalchemy_engine"] = engine
    app.extensions["sqlalchemy_session"] = db_session

    # Automatically create tables if not present
    Base.metadata.create_all(bind=engine)

    # Register blueprints
    app.register_blueprint(web_bp)
    app.register_blueprint(api_v1_bp, url_prefix="/api/v1")

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app


if __name__ == "__main__":
    app = create_app()
    print(f"[*] LifeLedger running on http://{settings.host}:{settings.port}")
    app.run(host=settings.host, port=settings.port, debug=False)
