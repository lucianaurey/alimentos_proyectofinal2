from __future__ import annotations

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


# ══════════════════════════════════════════════════════════════════
#  USUARIO  (Flask-Login · 3 roles: admin, empleado, repartidor)
# ══════════════════════════════════════════════════════════════════

class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario_sistema"   # tabla propia del sistema de login

    id               = db.Column(db.Integer, primary_key=True)
    username         = db.Column(db.String(80),  unique=True, nullable=False, index=True)
    nombre_completo  = db.Column(db.String(160), nullable=False)
    correo_electronico = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash    = db.Column(db.String(255), nullable=False)
    rol              = db.Column(db.String(20),  nullable=False, default="empleado", index=True)
    # rol: "admin" | "empleado" | "repartidor"
    estado           = db.Column(db.String(20),  nullable=False, default="activo",   index=True)
    fecha_creacion   = db.Column(db.DateTime,    nullable=False, default=datetime.utcnow)
    ultimo_acceso    = db.Column(db.DateTime)

    # relación con la bitácora
    accesos = db.relationship("BitacoraAcceso", back_populates="usuario", lazy="dynamic")

    # ── Flask-Login ──────────────────────────────────────────────
    @property
    def is_active(self) -> bool:
        return self.estado == "activo"

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def has_role(self, role: str) -> bool:
        return self.rol == role

    def __repr__(self) -> str:
        return f"<Usuario {self.username} [{self.rol}]>"


# ══════════════════════════════════════════════════════════════════
#  BITÁCORA DE ACCESO
# ══════════════════════════════════════════════════════════════════

class BitacoraAcceso(db.Model):
    __tablename__ = "bitacora_acceso"

    id         = db.Column(db.Integer,  primary_key=True)
    usuario_id = db.Column(db.Integer,  db.ForeignKey("usuario_sistema.id"), nullable=True, index=True)
    fecha_hora = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    ip         = db.Column(db.String(64))
    accion     = db.Column(db.String(80),  nullable=False)   # "login" | "logout" | "dashboard"
    detalle    = db.Column(db.String(255))

    usuario = db.relationship("Usuario", back_populates="accesos")


# ══════════════════════════════════════════════════════════════════
#  TABLAS DE LA BD DE NEGOCIO  (mapean tu schema existente)
# ══════════════════════════════════════════════════════════════════

# ── Rol de usuario (tabla de negocio, distinta de usuario_sistema) ─
class RolUsuario(db.Model):
    __tablename__ = "rol_usuario"

    id_rol_usuario  = db.Column(db.Integer, primary_key=True)
    cliente         = db.Column(db.String(45))
    repartidor      = db.Column(db.String(45))
    administrador   = db.Column(db.String(45))
    empleado        = db.Column(db.String(45))
    nivel_fidelidad = db.Column(db.String(45))
    calificacion    = db.Column(db.String(45))
    nivel           = db.Column(db.String(45))
    cargo           = db.Column(db.String(45))
    fecha_ingreso   = db.Column(db.String(45))
    horario         = db.Column(db.String(45))

    usuarios = db.relationship("UsuarioNegocio", back_populates="rol", lazy="dynamic")


# ── Usuario de negocio (clientes del sistema de pedidos) ──────────
class UsuarioNegocio(db.Model):
    __tablename__ = "usuario"

    id_usuario          = db.Column(db.Integer, primary_key=True)
    nombre              = db.Column(db.String(100))
    apellido_paterno    = db.Column(db.String(45))
    apellido_materno    = db.Column(db.String(45))
    correo_electronico  = db.Column(db.String(100))
    id_rol_usuario      = db.Column(db.Integer, db.ForeignKey("rol_usuario.id_rol_usuario"), nullable=False)

    rol       = db.relationship("RolUsuario",    back_populates="usuarios")
    pedidos   = db.relationship("Pedido",        back_populates="usuario",   lazy="dynamic")
    telefonos = db.relationship("TelefonoUsuario", back_populates="usuario", lazy="dynamic")
    direcciones = db.relationship("DireccionUsuario", back_populates="usuario", lazy="dynamic")
    soportes  = db.relationship("SoporteChat",   back_populates="usuario",   lazy="dynamic")

    def __repr__(self) -> str:
        return f"<UsuarioNegocio {self.nombre} {self.apellido_paterno}>"


# ── Proveedor ─────────────────────────────────────────────────────
class Proveedor(db.Model):
    __tablename__ = "proveedor"

    id_proveedor       = db.Column(db.Integer, primary_key=True)
    contacto           = db.Column(db.String(45))
    correo_electronico = db.Column(db.String(45))
    tipo_proveedor     = db.Column(db.String(45))
    nombre             = db.Column(db.String(100))

    productos  = db.relationship("Producto", back_populates="proveedor", lazy="dynamic")
    compras    = db.relationship("Compra",   back_populates="proveedor", lazy="dynamic")
    telefonos  = db.relationship("TelefonoProveedor", back_populates="proveedor", lazy="dynamic")


# ── Menú ──────────────────────────────────────────────────────────
class Menu(db.Model):
    __tablename__ = "menu"

    id_menu            = db.Column(db.Integer, primary_key=True)
    descripcion        = db.Column(db.String(200))
    fecha_actualizacion = db.Column(db.Date)
    nombre_menu        = db.Column(db.String(100))
    estado             = db.Column(db.String(10), default="activo")

    restaurantes = db.relationship("Restaurante", back_populates="menu", lazy="dynamic")


# ── Inventario ────────────────────────────────────────────────────
class Inventario(db.Model):
    __tablename__ = "inventario"

    id_inventario       = db.Column(db.Integer, primary_key=True)
    cantidad_disponible = db.Column(db.Integer)
    fecha_actualizacion = db.Column(db.Date)

    productos = db.relationship("Producto", back_populates="inventario", lazy="dynamic")


# ── Promoción ─────────────────────────────────────────────────────
class Promocion(db.Model):
    __tablename__ = "promocion"

    id_promocion  = db.Column(db.Integer, primary_key=True)
    codigo        = db.Column(db.String(45))
    fecha_inicio  = db.Column(db.Date)
    fecha_fin     = db.Column(db.Date)
    valor         = db.Column(db.Numeric(18, 2))
    uso_maximo    = db.Column(db.String(45))

    pedidos       = db.relationship("Pedido",        back_populates="promocion",      lazy="dynamic")
    tipos         = db.relationship("TipoPromocion", back_populates="promocion",      lazy="dynamic")


# ── Minimarket ────────────────────────────────────────────────────
class Minimarket(db.Model):
    __tablename__ = "minimarket"

    id_minimarket = db.Column(db.Integer, primary_key=True)
    nombre        = db.Column(db.String(100))
    encargado     = db.Column(db.String(100))

    productos   = db.relationship("ProductoMinimarket",  back_populates="minimarket", lazy="dynamic")
    direcciones = db.relationship("DireccionMinimarket", back_populates="minimarket", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Minimarket {self.nombre}>"


# ── Restaurante ───────────────────────────────────────────────────
class Restaurante(db.Model):
    __tablename__ = "restaurante"

    id_restaurante    = db.Column(db.Integer, primary_key=True)
    nombre            = db.Column(db.String(100), index=True)
    descripcion       = db.Column(db.Text)
    horario_atencion  = db.Column(db.Date)
    ruc               = db.Column(db.String(45))
    id_menu           = db.Column(db.Integer, db.ForeignKey("menu.id_menu"), nullable=False)

    menu        = db.relationship("Menu",                  back_populates="restaurantes")
    productos   = db.relationship("ProductoRestaurante",   back_populates="restaurante", lazy="dynamic")
    telefonos   = db.relationship("TelefonoRestaurante",   back_populates="restaurante", lazy="dynamic")
    direcciones = db.relationship("DireccionRestaurante",  back_populates="restaurante", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Restaurante {self.nombre}>"


# ── Empleado ──────────────────────────────────────────────────────
class Empleado(db.Model):
    __tablename__ = "empleado"

    id_empleado        = db.Column(db.Integer, primary_key=True)
    nombre             = db.Column(db.String(100))
    ci                 = db.Column(db.String(45))
    apellido_paterno   = db.Column(db.String(45))
    apellido_materno   = db.Column(db.String(45))
    correo_electronico = db.Column(db.String(100))

    pedidos     = db.relationship("EmpleadoPedido",    back_populates="empleado",   lazy="dynamic")
    telefonos   = db.relationship("TelefonoEmpleado",  back_populates="empleado",   lazy="dynamic")
    direcciones = db.relationship("DireccionEmpleado", back_populates="empleado",   lazy="dynamic")


# ── Repartidor ────────────────────────────────────────────────────
class Repartidor(db.Model):
    __tablename__ = "repartidor"

    id_repartidor          = db.Column(db.Integer, primary_key=True)
    nombre                 = db.Column(db.String(100), index=True)
    apellido_paterno       = db.Column(db.String(45))
    apellido_materno       = db.Column(db.String(45))
    fecha_prevista_entrega = db.Column(db.DateTime)
    control                = db.Column(db.String(45))
    disponibilidad         = db.Column(db.String(45), index=True)

    pedidos   = db.relationship("RepartidorPedido",    back_populates="repartidor", lazy="dynamic")
    entregas  = db.relationship("Entrega",             back_populates="repartidor", lazy="dynamic")
    telefonos = db.relationship("TelefonoRepartidor",  back_populates="repartidor", lazy="dynamic")
    vehiculos = db.relationship("Vehiculo",            back_populates="repartidor", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Repartidor {self.nombre}>"


# ── Producto ──────────────────────────────────────────────────────
class Producto(db.Model):
    __tablename__ = "producto"

    id_producto       = db.Column(db.Integer, primary_key=True)
    nombre            = db.Column(db.String(100), index=True)
    descripcion       = db.Column(db.String(200))
    stock_disponible  = db.Column(db.Integer)
    id_proveedor      = db.Column(db.Integer, db.ForeignKey("proveedor.id_proveedor"),   nullable=False)
    id_inventario     = db.Column(db.Integer, db.ForeignKey("inventario.id_inventario"), nullable=False)

    proveedor         = db.relationship("Proveedor",  back_populates="productos")
    inventario        = db.relationship("Inventario", back_populates="productos")
    minimarkets       = db.relationship("ProductoMinimarket",  back_populates="producto", lazy="dynamic")
    restaurantes      = db.relationship("ProductoRestaurante", back_populates="producto", lazy="dynamic")
    detalles_pedido   = db.relationship("DetallePedido",       back_populates="producto", lazy="dynamic")
    detalles_compra   = db.relationship("DetalleCompra",       back_populates="producto", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Producto {self.nombre}>"


# ── Producto ↔ Minimarket ─────────────────────────────────────────
class ProductoMinimarket(db.Model):
    __tablename__ = "producto_minimarket"

    id_producto_minimarket = db.Column(db.Integer, primary_key=True)
    id_producto            = db.Column(db.Integer, db.ForeignKey("producto.id_producto"),       nullable=False)
    id_minimarket          = db.Column(db.Integer, db.ForeignKey("minimarket.id_minimarket"),   nullable=False)

    producto   = db.relationship("Producto",   back_populates="minimarkets")
    minimarket = db.relationship("Minimarket", back_populates="productos")


# ── Producto ↔ Restaurante ────────────────────────────────────────
class ProductoRestaurante(db.Model):
    __tablename__ = "producto_restaurante"

    id_producto_restaurante = db.Column(db.Integer, primary_key=True)
    id_producto             = db.Column(db.Integer, db.ForeignKey("producto.id_producto"),         nullable=False)
    id_restaurante          = db.Column(db.Integer, db.ForeignKey("restaurante.id_restaurante"),   nullable=False)

    producto    = db.relationship("Producto",    back_populates="restaurantes")
    restaurante = db.relationship("Restaurante", back_populates="productos")


# ── Pedido ────────────────────────────────────────────────────────
class Pedido(db.Model):
    __tablename__ = "pedido"

    id_pedido = db.Column(
        db.Integer,
        primary_key=True
    )

    fecha_pedido = db.Column(
        db.Date,
        index=True
    )

    metodo_entrega = db.Column(
        db.String(100)
    )

    costo_envio = db.Column(
        db.Numeric(18, 2)
    )

    fecha_prevista_entrega = db.Column(
        db.Date
    )

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario"),
        nullable=False,
        index=True
    )

    id_promocion = db.Column(
        db.Integer,
        db.ForeignKey("promocion.id_promocion")
    )

    # RELACIONES
    usuario = db.relationship(
        "UsuarioNegocio",
        back_populates="pedidos"
    )

    promocion = db.relationship(
        "Promocion",
        back_populates="pedidos"
    )

    detalles = db.relationship(
        "DetallePedido",
        back_populates="pedido",
        lazy="dynamic"
    )

    pagos = db.relationship(
        "PagoUnico",
        back_populates="pedido",
        lazy="dynamic"
    )

    repartidores = db.relationship(
        "RepartidorPedido",
        back_populates="pedido",
        lazy="dynamic"
    )

    empleados = db.relationship(
        "EmpleadoPedido",
        back_populates="pedido",
        lazy="dynamic"
    )

    resenas = db.relationship(
        "PedidoResena",
        back_populates="pedido",
        lazy="dynamic"
    )

    alertas = db.relationship(
        "AlertaPedido",
        back_populates="pedido",
        lazy="dynamic"
    )

    def __repr__(self) -> str:
        return f"<Pedido {self.id_pedido} [{self.fecha_pedido}]>"

# ── Detalle de pedido ─────────────────────────────────────────────
class DetallePedido(db.Model):
    __tablename__ = "detalle_pedido"

    id_detalle_pedido = db.Column(db.Integer, primary_key=True)
    precio_unitario   = db.Column(db.Numeric(18, 2))
    cantidad          = db.Column(db.Integer)
    id_pedido         = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"),     nullable=False, index=True)
    id_producto       = db.Column(db.Integer, db.ForeignKey("producto.id_producto"), nullable=False, index=True)

    pedido   = db.relationship("Pedido",   back_populates="detalles")
    producto = db.relationship("Producto", back_populates="detalles_pedido")

    @property
    def subtotal(self):
        if self.precio_unitario and self.cantidad:
            return float(self.precio_unitario) * self.cantidad
        return 0.0


# ── Pago único ────────────────────────────────────────────────────
class PagoUnico(db.Model):
    __tablename__ = "pago_unico"

    id_pago_unico   = db.Column(db.Integer, primary_key=True)
    fecha_pago      = db.Column(db.Date,    index=True)
    monto           = db.Column(db.Numeric(18, 2), index=True)
    nombre_banco    = db.Column(db.String(100))
    comprobante     = db.Column(db.String(100))
    numero_cuenta   = db.Column(db.String(100))
    cambio          = db.Column(db.Numeric(18, 2))
    tipo            = db.Column(db.String(45))
    numero_tarjeta  = db.Column(db.String(45))
    id_pedido       = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"), nullable=False, index=True)

    pedido          = db.relationship("Pedido", back_populates="pagos")
    detalles_factura = db.relationship("DetalleFactura", back_populates="pago", lazy="dynamic")


# ── Factura ───────────────────────────────────────────────────────
class Factura(db.Model):
    __tablename__ = "factura"

    id_factura = db.Column(db.Integer, primary_key=True)
    cuf        = db.Column(db.String(100))

    detalles = db.relationship("DetalleFactura", back_populates="factura", lazy="dynamic")


class DetalleFactura(db.Model):
    __tablename__ = "detalle_factura"

    id_detalle_factura   = db.Column(db.Integer, primary_key=True)
    nit                  = db.Column(db.String(45),  nullable=False)
    razon_social         = db.Column(db.String(100), nullable=False)
    fecha_emision        = db.Column(db.DateTime,    nullable=False)
    monto_total          = db.Column(db.Numeric(18, 2), nullable=False)
    cantidad             = db.Column(db.Integer,     nullable=False)
    descripcion_producto = db.Column(db.String(200))
    total                = db.Column(db.Numeric(18, 2))
    id_pago_unico        = db.Column(db.Integer, db.ForeignKey("pago_unico.id_pago_unico"), nullable=False)
    id_factura           = db.Column(db.Integer, db.ForeignKey("factura.id_factura"),       nullable=False)

    pago    = db.relationship("PagoUnico", back_populates="detalles_factura")
    factura = db.relationship("Factura",   back_populates="detalles")


# ── Compra (a proveedores) ────────────────────────────────────────
class Compra(db.Model):
    __tablename__ = "compra"

    id_compra    = db.Column(db.Integer, primary_key=True)
    fecha        = db.Column(db.Date)
    monto_total  = db.Column(db.Numeric(18, 2))
    id_proveedor = db.Column(db.Integer, db.ForeignKey("proveedor.id_proveedor"), nullable=False)

    proveedor = db.relationship("Proveedor", back_populates="compras")
    detalles  = db.relationship("DetalleCompra", back_populates="compra", lazy="dynamic")


class DetalleCompra(db.Model):
    __tablename__ = "detalle_compra"

    id_detalle_compra = db.Column(db.Integer, primary_key=True)
    cantidad          = db.Column(db.Integer, nullable=False)
    precio_unitario   = db.Column(db.Numeric(18, 2))
    id_compra         = db.Column(db.Integer, db.ForeignKey("compra.id_compra"),       nullable=False)
    id_producto       = db.Column(db.Integer, db.ForeignKey("producto.id_producto"),   nullable=False)

    compra   = db.relationship("Compra",   back_populates="detalles")
    producto = db.relationship("Producto", back_populates="detalles_compra")


# ── Seguimiento de entrega ────────────────────────────────────────
class SeguimientoEntrega(db.Model):
    __tablename__ = "seguimiento_entrega"

    id_seguimiento_entrega = db.Column(db.Integer, primary_key=True)
    longitud               = db.Column(db.Numeric(12, 6))
    direccion              = db.Column(db.String(200))
    velocidad              = db.Column(db.Integer)
    ts_timestamp           = db.Column(db.DateTime)

    entregas = db.relationship("Entrega", back_populates="seguimiento", lazy="dynamic")


# ── Entrega ───────────────────────────────────────────────────────
class Entrega(db.Model):
    __tablename__ = "entrega"

    id_entrega              = db.Column(db.Integer, primary_key=True)
    tipo_proveedor          = db.Column(db.String(100))
    fecha_asignacion        = db.Column(db.Date, index=True)
    fecha_aceptacion        = db.Column(db.Date, index=True)
    id_seguimiento_entrega  = db.Column(db.Integer, db.ForeignKey("seguimiento_entrega.id_seguimiento_entrega"))
    id_repartidor           = db.Column(db.Integer, db.ForeignKey("repartidor.id_repartidor"), nullable=False, index=True)

    seguimiento = db.relationship("SeguimientoEntrega", back_populates="entregas")
    repartidor  = db.relationship("Repartidor",          back_populates="entregas")


# ── Repartidor ↔ Pedido ───────────────────────────────────────────
class RepartidorPedido(db.Model):
    __tablename__ = "repartidor_pedido"

    id_repartidor_pedido = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(100)
    )

    ubicacion_repartidor = db.Column(
        db.String(200)
    )

    id_repartidor = db.Column(
        db.Integer,
        db.ForeignKey("repartidor.id_repartidor"),
        nullable=False
    )

    pedido_id_pedido = db.Column(
        db.Integer,
        db.ForeignKey("pedido.id_pedido"),
        nullable=False
    )

    repartidor = db.relationship(
        "Repartidor",
        back_populates="pedidos"
    )

    pedido = db.relationship(
        "Pedido",
        back_populates="repartidores"
    )

    seguimientos = db.relationship(
        "SeguimientoPedido",
        back_populates="repartidor_pedido",
        lazy="dynamic"
    )


# ── Seguimiento de pedido ─────────────────────────────────────────
class SeguimientoPedido(db.Model):
    __tablename__ = "seguimiento_pedido"

    id_seguimiento_pedido = db.Column(
        db.Integer,
        primary_key=True
    )

    tiempo_estimado = db.Column(
        db.Date
    )

    hora_llegada = db.Column(
        db.Date
    )

    estado = db.Column(
        db.String(45),
        index=True
    )

    id_repartidor_pedido = db.Column(
        db.Integer,
        db.ForeignKey(
            "repartidor_pedido.id_repartidor_pedido"
        ),
        nullable=False
    )

    repartidor_pedido = db.relationship(
        "RepartidorPedido",
        back_populates="seguimientos"
    )
# ── Empleado ↔ Pedido ─────────────────────────────────────────────
class EmpleadoPedido(db.Model):
    __tablename__ = "empleado_pedido"

    id_empleado_pedido = db.Column(db.Integer, primary_key=True)
    fecha_registro     = db.Column(db.Date)
    fecha_entrega      = db.Column(db.Date)
    id_empleado        = db.Column(db.Integer, db.ForeignKey("empleado.id_empleado"), nullable=False)
    id_pedido          = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"),     nullable=False)

    empleado = db.relationship("Empleado", back_populates="pedidos")
    pedido   = db.relationship("Pedido",   back_populates="empleados")


# ── Soporte chat ──────────────────────────────────────────────────
class SoporteChat(db.Model):
    __tablename__ = "soporte_chat"

    id_soporte_chat  = db.Column(db.Integer, primary_key=True)
    fecha_inicio     = db.Column(db.Date)
    tipo_chat        = db.Column(db.String(25))
    estado           = db.Column(db.String(45))
    fecha_cierre     = db.Column(db.Date)
    usuario_id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)

    usuario = db.relationship("UsuarioNegocio", back_populates="soportes")


# ── Reseña ────────────────────────────────────────────────────────
class Resena(db.Model):
    __tablename__ = "resena"

    id_resena        = db.Column(db.Integer, primary_key=True)
    descripcion      = db.Column(db.Text)
    comentario       = db.Column(db.Text)
    horario_atencion = db.Column(db.DateTime)
    calificacion     = db.Column(db.String(45), index=True)

    pedidos = db.relationship("PedidoResena", back_populates="resena", lazy="dynamic")


class PedidoResena(db.Model):
    __tablename__ = "pedido_resena"

    id_pedido_resena = db.Column(db.Integer, primary_key=True)
    id_pedido        = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"),   nullable=False)
    id_resena        = db.Column(db.Integer, db.ForeignKey("resena.id_resena"),   nullable=False)

    pedido = db.relationship("Pedido",  back_populates="resenas")
    resena = db.relationship("Resena",  back_populates="pedidos")


# ── Vehículo ──────────────────────────────────────────────────────
class Vehiculo(db.Model):
    __tablename__ = "vehiculo"

    id_vehiculo   = db.Column(db.Integer, primary_key=True)
    tipo          = db.Column(db.String(45))
    placa         = db.Column(db.String(45))
    marca         = db.Column(db.String(45))
    id_repartidor = db.Column(db.Integer, db.ForeignKey("repartidor.id_repartidor"), nullable=False)

    repartidor = db.relationship("Repartidor", back_populates="vehiculos")


# ── Alerta ────────────────────────────────────────────────────────
class Alerta(db.Model):
    __tablename__ = "alerta"

    id_alerta           = db.Column(db.Integer, primary_key=True)
    tiempo_estimado     = db.Column(db.Time)
    hora_llegada        = db.Column(db.Time)
    confirmacion_pedido = db.Column(db.String(45))

    pedidos = db.relationship("AlertaPedido", back_populates="alerta", lazy="dynamic")


class AlertaPedido(db.Model):
    __tablename__ = "alerta_pedido"

    id_alerta_pedido = db.Column(db.Integer, primary_key=True)
    fecha_registro   = db.Column(db.Date)
    id_alerta        = db.Column(db.Integer, db.ForeignKey("alerta.id_alerta"),   nullable=False)
    id_pedido        = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"),   nullable=False)

    alerta = db.relationship("Alerta", back_populates="pedidos")
    pedido = db.relationship("Pedido", back_populates="alertas")


# ── Tipo de promoción ─────────────────────────────────────────────
class TipoPromocion(db.Model):
    __tablename__ = "tipo_promocion"

    id_tipo_promocion = db.Column(db.Integer, primary_key=True)
    nombre            = db.Column(db.String(100))
    descripcion       = db.Column(db.String(200))
    id_promocion      = db.Column(db.Integer, db.ForeignKey("promocion.id_promocion"), nullable=False)

    promocion = db.relationship("Promocion", back_populates="tipos")


# ══════════════════════════════════════════════════════════════════
#  TABLAS DE TELÉFONOS
# ══════════════════════════════════════════════════════════════════

class TelefonoUsuario(db.Model):
    __tablename__ = "telefono_usuario"
    id_telefono_usuario = db.Column(db.Integer, primary_key=True)
    numero_telefono     = db.Column(db.String(45))
    id_usuario          = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    usuario = db.relationship("UsuarioNegocio", back_populates="telefonos")


class TelefonoEmpleado(db.Model):
    __tablename__ = "telefono_empleado"
    id_telefono_empleado = db.Column(db.Integer, primary_key=True)
    numero_telefono      = db.Column(db.String(45))
    id_empleado          = db.Column(db.Integer, db.ForeignKey("empleado.id_empleado"), nullable=False)
    empleado = db.relationship("Empleado", back_populates="telefonos")


class TelefonoRepartidor(db.Model):
    __tablename__ = "telefono_repartidor"
    id_telefono_repartidor = db.Column(db.Integer, primary_key=True)
    numero_telefono        = db.Column(db.String(45))
    id_repartidor          = db.Column(db.Integer, db.ForeignKey("repartidor.id_repartidor"), nullable=False)
    repartidor = db.relationship("Repartidor", back_populates="telefonos")


class TelefonoRestaurante(db.Model):
    __tablename__ = "telefono_restaurante"
    id_telefono_restaurante = db.Column(db.Integer, primary_key=True)
    numero_telefono         = db.Column(db.String(45))
    id_restaurante          = db.Column(db.Integer, db.ForeignKey("restaurante.id_restaurante"), nullable=False)
    restaurante = db.relationship("Restaurante", back_populates="telefonos")


class TelefonoProveedor(db.Model):
    __tablename__ = "telefono_proveedor"
    id_telefono_proveedor = db.Column(db.Integer, primary_key=True)
    numero_telefono       = db.Column(db.String(45))
    id_proveedor          = db.Column(db.Integer, db.ForeignKey("proveedor.id_proveedor"), nullable=False)
    proveedor = db.relationship("Proveedor", back_populates="telefonos")


# ══════════════════════════════════════════════════════════════════
#  TABLAS DE DIRECCIONES
# ══════════════════════════════════════════════════════════════════

class DireccionUsuario(db.Model):
    __tablename__ = "direccion_usuario"
    id_direccion_usuario = db.Column(db.Integer, primary_key=True)
    ciudad               = db.Column(db.String(45))
    numero               = db.Column(db.String(45))
    calle                = db.Column(db.String(100))
    zona                 = db.Column(db.String(45), index=True)   # ← clave para analytics por zona
    id_usuario           = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    usuario = db.relationship("UsuarioNegocio", back_populates="direcciones")


class DireccionEmpleado(db.Model):
    __tablename__ = "direccion_empleado"
    id_direccion_empleado = db.Column(db.Integer, primary_key=True)
    ciudad                = db.Column(db.String(45))
    numero                = db.Column(db.String(45))
    calle                 = db.Column(db.String(100))
    zona                  = db.Column(db.String(45))
    id_empleado           = db.Column(db.Integer, db.ForeignKey("empleado.id_empleado"), nullable=False)
    empleado = db.relationship("Empleado", back_populates="direcciones")


class DireccionMinimarket(db.Model):
    __tablename__ = "direccion_minimarket"
    id_direccion_minimarket = db.Column(db.Integer, primary_key=True)
    ciudad                  = db.Column(db.String(45))
    numero                  = db.Column(db.String(45))
    calle                   = db.Column(db.String(100))
    zona                    = db.Column(db.String(45), index=True)
    id_minimarket           = db.Column(db.Integer, db.ForeignKey("minimarket.id_minimarket"), nullable=False)
    minimarket = db.relationship("Minimarket", back_populates="direcciones")


class DireccionRestaurante(db.Model):
    __tablename__ = "direccion_restaurante"
    id_direccion_restaurante = db.Column(db.Integer, primary_key=True)
    ciudad                   = db.Column(db.String(45))
    numero                   = db.Column(db.String(45))
    calle                    = db.Column(db.String(100))
    zona                     = db.Column(db.String(45), index=True)  # ← clave para analytics
    id_restaurante           = db.Column(db.Integer, db.ForeignKey("restaurante.id_restaurante"), nullable=False)
    restaurante = db.relationship("Restaurante", back_populates="direcciones")