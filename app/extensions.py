from __future__ import annotations

from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

# ── Instancias globales ──────────────────────────────────────────
# Se crean aquí SIN inicializar para evitar importaciones circulares.
# Se inicializan dentro de create_app() en __init__.py
db           = SQLAlchemy()
migrate      = Migrate()
login_manager = LoginManager()
csrf         = CSRFProtect()