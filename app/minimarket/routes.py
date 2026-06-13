from __future__ import annotations

from flask import Blueprint, render_template
from flask_login import login_required

from app.auth.routes import role_required
from app.models import DireccionMinimarket, Minimarket

minimarket_bp = Blueprint("minimarket", __name__)


@minimarket_bp.route("/")
@login_required
@role_required("admin", "empleado")
def lista():
    minimarkets = (
        Minimarket.query
        .outerjoin(DireccionMinimarket,
                   DireccionMinimarket.id_minimarket == Minimarket.id_minimarket)
        .add_columns(DireccionMinimarket.zona)
        .order_by(Minimarket.nombre)
        .all()
    )
    return render_template(
        "minimarket/lista.html",
        title="Minimarkets",
        minimarkets=minimarkets,
    )


@minimarket_bp.route("/<int:id>")
@login_required
@role_required("admin", "empleado")
def detalle(id: int):
    minimarket = Minimarket.query.get_or_404(id)
    return render_template(
        "minimarket/detalle.html",
        title=minimarket.nombre,
        minimarket=minimarket,
    )