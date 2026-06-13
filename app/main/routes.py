from __future__ import annotations

from flask import Blueprint, jsonify, redirect, render_template, request, url_for, flash

from app.extensions import db
from app.models import (
    DireccionMinimarket, DireccionRestaurante,
    Entrega, Pedido, Promocion, Repartidor, Resena, PedidoResena,
    Restaurante, Minimarket, Producto, TipoPromocion, TelefonoRestaurante,
    UsuarioNegocio,
)
from sqlalchemy import func
from sqlalchemy.orm import joinedload

main_bp = Blueprint("main", __name__)


def _build_restaurantes(limit=20):
    """Devuelve los mejores restaurantes enriquecidos con dirección y teléfono."""
    # Subquery: pick random restaurant IDs limited to `limit`
    subq = (
        db.session.query(Restaurante.id_restaurante)
        .order_by(func.random())
        .limit(limit)
        .subquery()
    )
    rows = (
        Restaurante.query
        .filter(Restaurante.id_restaurante.in_(db.session.query(subq)))
        .outerjoin(DireccionRestaurante,
                   DireccionRestaurante.id_restaurante == Restaurante.id_restaurante)
        .outerjoin(TelefonoRestaurante,
                   TelefonoRestaurante.id_restaurante == Restaurante.id_restaurante)
        .add_columns(
            DireccionRestaurante.ciudad,
            DireccionRestaurante.calle,
            DireccionRestaurante.zona,
            TelefonoRestaurante.numero_telefono.label("telefono"),
        )
        .order_by(Restaurante.nombre)
        .all()
    )
    result = []
    seen = set()
    for row in rows:
        r, ciudad, calle, zona, tel = row
        if r.id_restaurante in seen:
            continue
        seen.add(r.id_restaurante)
        r.ciudad   = ciudad
        r.calle    = calle
        r.zona     = zona
        r.telefono = tel
        r.img      = f"restaurante_{r.id_restaurante}"
        result.append(r)
    return result


def _build_minimarkets(limit=20):
    """Devuelve los mejores minimarkets con dirección."""
    subq = (
        db.session.query(Minimarket.id_minimarket)
        .order_by(func.random())
        .limit(limit)
        .subquery()
    )
    rows = (
        Minimarket.query
        .filter(Minimarket.id_minimarket.in_(db.session.query(subq)))
        .outerjoin(DireccionMinimarket,
                   DireccionMinimarket.id_minimarket == Minimarket.id_minimarket)
        .add_columns(
            DireccionMinimarket.ciudad,
            DireccionMinimarket.calle,
            DireccionMinimarket.zona,
        )
        .order_by(Minimarket.nombre)
        .all()
    )
    result = []
    seen = set()
    for row in rows:
        m, ciudad, calle, zona = row
        if m.id_minimarket in seen:
            continue
        seen.add(m.id_minimarket)
        m.ciudad = ciudad
        m.calle  = calle
        m.zona   = zona
        m.img    = f"minimarket_{m.id_minimarket}"
        result.append(m)
    return result


def _build_productos(limit=12):
    """Devuelve productos con proveedor y origen (restaurante/minimarket)."""
    from app.models import ProductoRestaurante, ProductoMinimarket, DetallePedido
    productos_raw = (
        Producto.query
        .order_by(func.random())
        .limit(limit)
        .all()
    )
    result = []
    for p in productos_raw:
        # Determinar origen
        in_rest = ProductoRestaurante.query.filter_by(id_producto=p.id_producto).first()
        in_mini = ProductoMinimarket.query.filter_by(id_producto=p.id_producto).first()
        p.origen = "Restaurante" if in_rest else ("Minimarket" if in_mini else "General")
        # Precio desde último detalle de pedido
        detalle = (
            DetallePedido.query
            .filter_by(id_producto=p.id_producto)
            .order_by(DetallePedido.id_detalle_pedido.desc())
            .first()
        )
        p.precio = float(detalle.precio_unitario) if detalle and detalle.precio_unitario else 10.0
        # Proveedor
        try:
            prov = p.proveedor
            p.proveedor_nombre = prov.nombre if prov else "Proveedor local"
        except Exception:
            p.proveedor_nombre = "Proveedor local"
        p.img = f"producto_{p.id_producto}"
        result.append(p)
    return result



def _build_promociones():
    """Devuelve promociones activas con su tipo."""
    from datetime import date
    promos = (
        Promocion.query
        .outerjoin(TipoPromocion, TipoPromocion.id_promocion == Promocion.id_promocion)
        .add_columns(
            TipoPromocion.nombre.label("tipo"),
            TipoPromocion.descripcion.label("descripcion_tipo"),
        )
        .filter(
            (Promocion.fecha_fin == None) | (Promocion.fecha_fin >= date.today())
        )
        .limit(6)
        .all()
    )
    result = []
    seen = set()
    for row in promos:
        p, tipo, desc = row
        if p.id_promocion in seen:
            continue
        seen.add(p.id_promocion)
        p.tipo            = tipo or "Descuento"
        p.descripcion_tipo = desc
        result.append(p)
    return result


def _build_resenas(limit=6):
    """Devuelve reseñas recientes."""
    return (
        Resena.query
        .order_by(Resena.horario_atencion.desc().nullslast())
        .limit(limit)
        .all()
    )


@main_bp.route("/landing")
@main_bp.route("/")
def landing():
    try:
        restaurantes = _build_restaurantes()
        minimarkets  = _build_minimarkets()
        productos    = _build_productos()
        promociones  = _build_promociones()
        resenas      = _build_resenas()
    except Exception as e:
        import traceback
        print(f"[LANDING ERROR] {e}")
        traceback.print_exc()
        restaurantes = minimarkets = productos = promociones = resenas = []

    return render_template(
        "landing.html",
        title="Foodly · Delivery Cochabamba",
        restaurantes=restaurantes,
        minimarkets=minimarkets,
        productos=productos,
        promociones=promociones,
        resenas=resenas,
    )


@main_bp.route("/contacto", methods=["POST"])
def contacto():
    """Procesa el formulario de contacto de la landing page."""
    nombre  = request.form.get("nombre", "").strip()
    email   = request.form.get("email", "").strip()
    asunto  = request.form.get("asunto", "consulta")
    mensaje = request.form.get("mensaje", "").strip()

    if nombre and email and mensaje:
        flash("¡Mensaje enviado! Nos pondremos en contacto contigo pronto.", "success")
    else:
        flash("Por favor completa todos los campos requeridos.", "danger")

    return redirect(url_for("main.landing") + "#contacto")


@main_bp.route("/api/landing/stats")
def api_landing_stats():
    """Stats reales para el hero de la landing page."""
    restaurantes  = Restaurante.query.count()
    minimarkets   = Minimarket.query.count()
    pedidos       = Pedido.query.count()
    productos     = Producto.query.count()
    repartidores  = Repartidor.query.count()
    clientes      = UsuarioNegocio.query.count()

    zonas = db.session.query(
        func.count(func.distinct(DireccionRestaurante.zona))
    ).scalar() or 7

    return jsonify({
        "restaurantes": restaurantes,
        "minimarkets":  minimarkets,
        "pedidos":      pedidos,
        "productos":    productos,
        "repartidores": repartidores,
        "clientes":     clientes,
        "zonas":        int(zonas),
    })