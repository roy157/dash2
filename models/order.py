# dash2/models/order.py
from . import db
import datetime

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    direccion_envio = db.Column(db.String(255), nullable=False)
    # Enum para estados de pedido (definido como un tipo de base de datos si usas PostgreSQL, aquí como string para SQLite)
    estado = db.Column(db.String(50), nullable=False, default='pendiente') # 'pendiente', 'procesando', 'enviado', 'entregado', 'cancelado'
    total = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_pedido = db.Column(db.DateTime, default=datetime.datetime.now)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)

    # Relaciones
    # 'cliente' ya está definido como backref en Cliente
    pagos = db.relationship('Pago', backref='pedido', lazy=True) # Un pedido puede tener varios pagos (ej. si falla el primero)
    productos_en_pedido = db.relationship('PedidoProducto', backref='pedido', lazy=True) # Relación con la tabla de unión PedidoProducto

    def __repr__(self):
        return f"<Pedido {self.id} de Cliente {self.cliente_id}>"