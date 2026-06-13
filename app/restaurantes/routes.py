from __future__ import annotations

from flask import Blueprint, render_template
from flask_login import login_required

from app.auth.routes import role_required
from app.models import Restaurante, DireccionRestaurante

restaurantes_bp = Blueprint("restaurantes", __name__)


@restaurantes_bp.route("/")
@login_required
@role_required("admin", "empleado")
def lista():
    restaurantes = Restaurante.query.order_by(Restaurante.nombre).all()
    return render_template(
        "restaurantes/lista.html",
        title="Restaurantes",
        restaurantes=restaurantes,
    )


@restaurantes_bp.route("/<int:id>")
@login_required
@role_required("admin", "empleado")
def detalle(id: int):
    restaurante = Restaurante.query.get_or_404(id)
    return render_template(
        "restaurantes/detalles.html",
        title=restaurante.nombre,
        restaurante=restaurante,
    )