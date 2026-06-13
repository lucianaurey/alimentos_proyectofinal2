from __future__ import annotations

import click
from flask import Flask, redirect, url_for
from werkzeug.security import generate_password_hash

from app.config import Config
from app.extensions import csrf, db, login_manager, migrate


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ── Inicializar extensiones ──────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # ── Configurar Flask-Login ───────────────────────────────────
    login_manager.login_view     = "auth.login"
    login_manager.login_message  = "Inicia sesión para continuar."
    login_manager.login_message_category = "warning"

    # ── User loader ──────────────────────────────────────────────
    from app.models import Usuario

    @login_manager.user_loader
    def load_user(user_id: str) -> Usuario | None:
        return db.session.get(Usuario, int(user_id))

    # ── Registrar Blueprints ─────────────────────────────────────
    from app.auth.routes        import auth_bp
    from app.main.routes        import main_bp
    from app.dashboard.routes   import dashboard_bp
    from app.data.routes        import data_bp
    from app.restaurantes.routes import restaurantes_bp
    from app.minimarket.routes  import minimarket_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp,   url_prefix="/dashboard")
    app.register_blueprint(data_bp,        url_prefix="/data")
    app.register_blueprint(restaurantes_bp, url_prefix="/restaurantes")
    app.register_blueprint(minimarket_bp,  url_prefix="/minimarket")

    # ── Ruta raíz ────────────────────────────────────────────────
    @app.route("/")
    def index():
        return redirect(url_for("main.landing"))

    # ── CLI y filtros ────────────────────────────────────────────
    _register_cli(app)
    _register_filters(app)

    return app


# ── Filtros de plantilla ─────────────────────────────────────────
def _register_filters(app: Flask) -> None:

    @app.template_filter("money")
    def money(value):
        """Formatea un número como moneda boliviana.  {{ 1234.5 | money }}"""
        if value is None:
            return "Bs 0.00"
        return f"Bs {float(value):,.2f}"

    @app.template_filter("pct")
    def pct(value):
        """Formatea un número como porcentaje.  {{ 0.123 | pct }}"""
        if value is None:
            return "0%"
        return f"{float(value):.1f}%"


# ── Comandos CLI ─────────────────────────────────────────────────
def _register_cli(app: Flask) -> None:

    @app.cli.command("create-admin")
    def create_admin_command():
        """Crea o actualiza el usuario administrador desde las variables de entorno."""
        from app.models import Usuario

        username  = app.config["ADMIN_USERNAME"]
        email     = app.config["ADMIN_EMAIL"]
        password  = app.config["ADMIN_PASSWORD"]
        full_name = app.config["ADMIN_FULL_NAME"]

        if not password:
            raise click.ClickException("ADMIN_PASSWORD no está definido en el entorno.")

        user   = Usuario.query.filter_by(username=username).first()
        action = "actualizado"
        if user is None:
            user   = Usuario(username=username)
            db.session.add(user)
            action = "creado"

        user.nombre_completo  = full_name
        user.correo_electronico = email
        user.password_hash    = generate_password_hash(password)
        user.rol              = "admin"
        user.estado           = "activo"
        db.session.commit()
        click.echo(f"✔  Usuario admin {action}: {username}")

    @app.cli.command("create-all-users")
    def create_all_users_command():
        """Crea los 3 usuarios del sistema: admin, empleado y repartidor."""
        from app.models import Usuario

        usuarios = [
            # ── Admin ────────────────────────────────────────────
            {
                "username":          "admin",
                "nombre_completo":   "Administrador Foodly",
                "correo_electronico": "admin@foodly.bo",
                "password":          "admin123",
                "rol":               "admin",
            },
            # ── Empleado ─────────────────────────────────────────
            {
                "username":          "empleado1",
                "nombre_completo":   "María Quispe",
                "correo_electronico": "empleado@foodly.bo",
                "password":          "empleado123",
                "rol":               "empleado",
            },
            # ── Repartidor ───────────────────────────────────────
            {
                "username":          "repartidor1",
                "nombre_completo":   "Carlos Mamani",
                "correo_electronico": "repartidor@foodly.bo",
                "password":          "repartidor123",
                "rol":               "repartidor",
            },
        ]

        for data in usuarios:
            user = Usuario.query.filter_by(username=data["username"]).first()
            if user is None:
                user = Usuario(username=data["username"])
                db.session.add(user)
            user.nombre_completo    = data["nombre_completo"]
            user.correo_electronico = data["correo_electronico"]
            user.password_hash      = generate_password_hash(data["password"])
            user.rol                = data["rol"]
            user.estado             = "activo"

        db.session.commit()
        click.echo("✔  Usuarios creados:")
        click.echo("   admin       →  admin@foodly.bo       /  admin123")
        click.echo("   empleado1   →  empleado@foodly.bo    /  empleado123")
        click.echo("   repartidor1 →  repartidor@foodly.bo  /  repartidor123")