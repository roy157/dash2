# dash2/models/cart.py
from . import db
import datetime

class Carrito(db.Model):
    __tablename__ = 'carritos'
    id = db.Column(db.Integer, primary_key=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False, unique=True) # Un cliente suele tener solo un carrito activo

    # Relaciones
    # 'cliente' ya está definido como backref en Cliente
    productos_en_carrito = db.relationship('CarritoProducto', backref='carrito', lazy=True, cascade="all, delete-orphan") # Eliminar productos del carrito si se elimina el carrito

    def __repr__(self):
        return f"<Carrito {self.id} (Cliente {self.cliente_id})>"