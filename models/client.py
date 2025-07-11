# dash2/models/client.py
from . import db
import datetime

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(90), nullable=False)
    email = db.Column(db.String(90), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False) # Si los clientes tienen login propio
    direccion = db.Column(db.String(255))
    telefono = db.Column(db.String(20))
    fecha_registro = db.Column(db.DateTime, default=datetime.datetime.now)

    # Definición de relaciones con otras tablas
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True) # Un cliente puede tener muchos pedidos
    reseñas = db.relationship('Reseña', backref='cliente', lazy=True) # Un cliente puede escribir muchas reseñas
    carritos = db.relationship('Carrito', backref='cliente', lazy=True) # Un cliente puede tener un carrito (o varios si permites historial)
    ventas = db.relationship('Venta', backref='cliente', lazy=True) # Un cliente puede realizar muchas ventas

    def __repr__(self):
        return f"<Cliente {self.nombre} ({self.email})>"