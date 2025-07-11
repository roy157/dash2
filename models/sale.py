# dash2/models/sale.py
from . import db
import datetime

class Venta(db.Model):
    __tablename__ = 'ventas'
    id = db.Column(db.Integer, primary_key=True)
    fecha_venta = db.Column(db.DateTime, default=datetime.datetime.now)
    total = db.Column(db.Numeric(10, 2), nullable=True)
    # Enum para estados de venta
    estado_venta = db.Column(db.String(50), nullable=False, default='completada') # 'completada', 'devuelta', 'cancelada'
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True) # Puede ser nulo para ventas a invitados

    # Relaciones
    # 'cliente' ya está definido como backref en Cliente
    productos_vendidos = db.relationship('VentaProducto', backref='venta', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Venta {self.id} (Total: ${self.total})>"