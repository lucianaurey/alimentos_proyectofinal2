from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required

from app.auth.routes import role_required

data_bp = Blueprint("data", __name__)


@data_bp.route("/olap")
@login_required
@role_required("admin")
def olap():
    return render_template("data/olap.html", title="Análisis OLAP")


@data_bp.route("/reportes")
@login_required
@role_required("admin")
def reportes():
    return render_template("data/reportes.html", title="Reportes")


@data_bp.route("/api/filtros")
@login_required
@role_required("admin")
def api_filtros():
    """Devuelve los valores únicos disponibles para los filtros del dashboard."""
    from sqlalchemy import func
    from app.extensions import db
    from app.models import DireccionUsuario, Pedido, Restaurante

    anios = [
        int(r[0]) for r in
        db.session.query(func.extract("year", Pedido.fecha_pedido).label("a"))
        .distinct().order_by("a").all()
        if r[0] is not None
    ]
    meses = list(range(1, 13))
    zonas = [
        r[0] for r in
        db.session.query(DireccionUsuario.zona).distinct()
        .filter(DireccionUsuario.zona.isnot(None)).order_by(DireccionUsuario.zona).all()
    ]
    restaurantes = [
        {"id": r.id_restaurante, "nombre": r.nombre}
        for r in Restaurante.query.order_by(Restaurante.nombre).all()
    ]

    return jsonify({
        "anios":        anios,
        "meses":        meses,
        "zonas":        zonas,
        "restaurantes": restaurantes,
    })