from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user

from app.auth.routes import role_required
from app.data import services as svc
from app.models import Empleado, Repartidor

dashboard_bp = Blueprint("dashboard", __name__)


# ── Vistas HTML ──────────────────────────────────────────────────

@dashboard_bp.route("/admin")
@login_required
@role_required("admin")
def admin():
    return render_template(
        "dashboard/admin.html",
        title="Dashboard Administrador",
        dashboard="admin",
    )


@dashboard_bp.route("/admin/empleados")
@login_required
@role_required("admin")
def admin_empleados():
    empleados = (
        Empleado.query
        .order_by(Empleado.nombre, Empleado.apellido_paterno)
        .all()
    )
    return render_template(
        "dashboard/admin_empleados.html",
        title="Dashboard Empleados",
        dashboard="admin",
        empleados=empleados,
    )


@dashboard_bp.route("/admin/repartidores")
@login_required
@role_required("admin")
def admin_repartidores():
    repartidores = (
        Repartidor.query
        .order_by(Repartidor.nombre, Repartidor.apellido_paterno)
        .all()
    )
    return render_template(
        "dashboard/admin_repartidores.html",
        title="Dashboard Repartidores",
        dashboard="admin",
        repartidores=repartidores,
    )


@dashboard_bp.route("/empleado")
@login_required
@role_required("admin", "empleado")
def empleado():
    from app.models import Empleado as EmpleadoModel
    emp = EmpleadoModel.query.filter_by(
        correo_electronico=current_user.correo_electronico
    ).first()
    emp_id = emp.id_empleado if emp else None
    return render_template(
        "dashboard/empleado.html",
        title="Dashboard Empleado",
        dashboard="empleado",
        emp_id=emp_id,
    )


@dashboard_bp.route("/repartidor")
@login_required
@role_required("admin", "repartidor")
def repartidor():
    return render_template(
        "dashboard/repartidor.html",
        title="Dashboard Repartidor",
        dashboard="repartidor",
    )


@dashboard_bp.route("/financiero")
@login_required
@role_required("admin")
def financiero():
    return render_template(
        "dashboard/financiero.html",
        title="Dashboard Financiero",
        dashboard="financiero",
    )


# ── APIs JSON · Admin ────────────────────────────────────────────

@dashboard_bp.route("/api/admin/kpis")
@login_required
@role_required("admin")
def api_admin_kpis():
    return jsonify(svc.kpis_admin(_get_filtros()))


@dashboard_bp.route("/api/admin/ventas-mes")
@login_required
@role_required("admin")
def api_ventas_mes():
    return jsonify(svc.ventas_por_mes(_get_filtros()))


@dashboard_bp.route("/api/admin/top-restaurantes")
@login_required
@role_required("admin")
def api_top_restaurantes():
    return jsonify(svc.top_restaurantes(_get_filtros()))


@dashboard_bp.route("/api/admin/pedidos-zona")
@login_required
@role_required("admin")
def api_pedidos_zona():
    return jsonify(svc.pedidos_por_zona(_get_filtros()))


@dashboard_bp.route("/api/admin/pedidos-estado")
@login_required
@role_required("admin")
def api_pedidos_estado():
    return jsonify(svc.pedidos_por_estado())


@dashboard_bp.route("/api/admin/ranking")
@login_required
@role_required("admin")
def api_ranking():
    return jsonify(svc.ranking_restaurantes(_get_filtros()))


# ── APIs JSON · Empleado (por ID específico) ─────────────────────

@dashboard_bp.route("/api/empleado/pedidos-estado")
@login_required
@role_required("admin", "empleado")
def api_empleado_pedidos_estado():
    # Si admin consulta un empleado específico por id, se respeta; si es el
    # propio empleado logueado, se busca su registro por correo.
    emp_id = request.args.get("id", type=int)
    if not emp_id and current_user.rol == "empleado":
        from app.models import Empleado as EmpleadoModel
        emp = EmpleadoModel.query.filter_by(
            correo_electronico=current_user.correo_electronico
        ).first()
        if emp:
            emp_id = emp.id_empleado
    return jsonify(svc.pedidos_por_estado_empleado(emp_id))


@dashboard_bp.route("/api/empleado/kpis")
@login_required
@role_required("admin", "empleado")
def api_empleado_kpis():
    emp_id = request.args.get("id", type=int)
    return jsonify(svc.kpis_empleado(emp_id))


@dashboard_bp.route("/api/empleado/productos-vendidos")
@login_required
@role_required("admin", "empleado")
def api_productos_vendidos():
    emp_id = request.args.get("id", type=int)
    return jsonify(svc.productos_mas_vendidos(emp_id=emp_id))


@dashboard_bp.route("/api/empleado/pedidos-hora")
@login_required
@role_required("admin", "empleado")
def api_pedidos_hora():
    emp_id = request.args.get("id", type=int)
    return jsonify(svc.pedidos_por_hora(emp_id=emp_id))


@dashboard_bp.route("/api/empleado/ultimos-pedidos")
@login_required
@role_required("admin", "empleado")
def api_ultimos_pedidos():
    emp_id = request.args.get("id", type=int)
    return jsonify(svc.ultimos_pedidos(emp_id=emp_id))


@dashboard_bp.route("/api/empleado/ingresos-metodo")
@login_required
@role_required("admin", "empleado")
def api_ingresos_metodo():
    emp_id = request.args.get("id", type=int)
    return jsonify(svc.ingresos_por_metodo(emp_id=emp_id))


@dashboard_bp.route("/api/empleado/tipo-pago")
@login_required
@role_required("admin", "empleado")
def api_tipo_pago():
    emp_id = request.args.get("id", type=int)
    return jsonify(svc.tipo_pago_empleado(emp_id=emp_id))


# ── APIs JSON · Repartidor (por ID específico) ───────────────────

@dashboard_bp.route("/api/repartidor/kpis")
@login_required
@role_required("admin", "repartidor")
def api_repartidor_kpis():
    rep_id = request.args.get("id", type=int)
    return jsonify(svc.kpis_repartidor(rep_id))


@dashboard_bp.route("/api/repartidor/entregas-dia")
@login_required
@role_required("admin", "repartidor")
def api_entregas_dia():
    rep_id = request.args.get("id", type=int)
    return jsonify(svc.entregas_por_dia(rep_id=rep_id))


@dashboard_bp.route("/api/repartidor/entregas-zona")
@login_required
@role_required("admin", "repartidor")
def api_entregas_zona():
    rep_id = request.args.get("id", type=int)
    return jsonify(svc.entregas_por_zona(rep_id=rep_id))


@dashboard_bp.route("/api/repartidor/historial")
@login_required
@role_required("admin", "repartidor")
def api_historial_entregas():
    rep_id = request.args.get("id", type=int)
    return jsonify(svc.historial_entregas(rep_id=rep_id))


@dashboard_bp.route("/api/repartidor/vehiculos-tipo")
@login_required
@role_required("admin", "repartidor")
def api_vehiculos_tipo():
    rep_id = request.args.get("id", type=int)
    return jsonify(svc.disponibilidad_repartidores(rep_id=rep_id))


@dashboard_bp.route("/api/repartidor/rendimiento-semanal")
@login_required
@role_required("admin", "repartidor")
def api_rendimiento_semanal():
    rep_id = request.args.get("id", type=int)
    return jsonify(svc.estados_pedidos_repartidor(rep_id=rep_id))


# ── APIs JSON · Financiero ───────────────────────────────────────

@dashboard_bp.route("/api/financiero/kpis")
@login_required
@role_required("admin")
def api_financiero_kpis():
    return jsonify(svc.kpis_financiero())


@dashboard_bp.route("/api/financiero/evolucion")
@login_required
@role_required("admin")
def api_ingresos_evolucion():
    return jsonify(svc.ingresos_evolucion())


@dashboard_bp.route("/api/financiero/por-restaurante")
@login_required
@role_required("admin")
def api_ingresos_restaurante():
    return jsonify(svc.ingresos_por_restaurante())


# ── Helper filtros ───────────────────────────────────────────────

def _get_filtros() -> dict:
    return {
        "anio":         request.args.get("anio"),
        "mes":          request.args.get("mes"),
        "zona":         request.args.get("zona"),
        "restaurante":  request.args.get("restaurante"),
        "fecha_inicio": request.args.get("fecha_inicio"),
        "fecha_fin":    request.args.get("fecha_fin"),
    }