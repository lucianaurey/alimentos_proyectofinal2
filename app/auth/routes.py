from __future__ import annotations

from datetime import datetime
from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth.forms import LoginForm
from app.extensions import db
from app.models import BitacoraAcceso, Usuario

auth_bp = Blueprint("auth", __name__)


# ── Helpers ──────────────────────────────────────────────────────

def log_access(action: str, detail: str = "", user: Usuario | None = None) -> None:
    """Registra un evento en la bitácora de accesos."""
    actor = user if user is not None else (
        current_user if current_user.is_authenticated else None
    )
    entry = BitacoraAcceso(
        usuario_id=actor.id if actor else None,
        ip=request.headers.get("X-Forwarded-For", request.remote_addr),
        accion=action,
        detalle=detail[:255] if detail else "",
    )
    db.session.add(entry)


def _redirect_by_role(user: Usuario) -> str:
    """Devuelve la URL del dashboard según el rol del usuario."""
    destinos = {
        "admin":       "dashboard.admin",
        "empleado":    "dashboard.empleado",
        "repartidor":  "dashboard.repartidor",
    }
    return url_for(destinos.get(user.rol, "dashboard.admin"))


# ── Decorador de rol ─────────────────────────────────────────────

def role_required(*roles: str):
    """
    Decorador que restringe el acceso a uno o varios roles.
    Uso:
        @role_required("admin")
        @role_required("admin", "empleado")
    """
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if current_user.rol not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator


# ── Rutas ────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Si llega al login estando autenticado, cerramos la sesión previa
    # para forzar una nueva autenticación (más seguro)
    if current_user.is_authenticated:
        logout_user()

    form = LoginForm()
    if form.validate_on_submit():
        # Buscamos por username o correo
        identifier = form.username.data.strip()
        user = (
            Usuario.query.filter_by(username=identifier).first()
            or Usuario.query.filter_by(correo_electronico=identifier).first()
        )

        # Verificamos contraseña, estado activo Y que el rol coincida
        if user and user.is_active and user.check_password(form.password.data):
            if user.rol != form.rol.data:
                flash("El rol seleccionado no corresponde a tu cuenta.", "warning")
                return render_template("auth/login.html", form=form, title="Iniciar sesión")

            login_user(user, remember=form.remember.data)
            user.ultimo_acceso = datetime.utcnow()
            log_access("login", f"Inicio de sesión · rol: {user.rol}", user)
            db.session.commit()

            flash(f"Bienvenido, {user.nombre_completo.split()[0]}.", "success")
            next_url = request.args.get("next")
            return redirect(next_url or _redirect_by_role(user))

        # Credenciales inválidas
        log_access("login_failed", f"Intento fallido: {identifier}")
        db.session.commit()
        flash("Credenciales inválidas o usuario inactivo.", "danger")

    return render_template("auth/login.html", form=form, title="Iniciar sesión")


@auth_bp.route("/logout")
@login_required
def logout():
    log_access("logout", "Cierre de sesión")
    db.session.commit()
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/unauthorized")
def unauthorized():
    return render_template("errors/403.html", title="Sin acceso"), 403