# dash2/models/product.py
from . import db
import datetime

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    imagen_url = db.Column(db.String(255)) # URL de la imagen del producto
    fecha_agregado = db.Column(db.DateTime, default=datetime.datetime.now)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)

    # Definición de relaciones con otras tablas
    categoria = db.relationship('Categoria', backref='productos', lazy=True) # Un producto pertenece a una categoría
    reseñas = db.relationship('Reseña', backref='producto', lazy=True) # Un producto puede tener muchas reseñas
    pedidos_productos = db.relationship('PedidoProducto', backref='producto', lazy=True) # Relación con la tabla de unión PedidoProducto
    carritos_productos = db.relationship('CarritoProducto', backref='producto', lazy=True) # Relación con la tabla de unión CarritoProducto
    ventas_productos = db.relationship('VentaProducto', backref='producto', lazy=True) # Relación con la tabla de unión VentaProducto
    inventarios = db.relationship('Inventario', backref='producto', lazy=True) # Un producto puede tener muchos movimientos de inventario

    def __repr__(self):
        return f"<Producto {self.nombre} (ID: {self.id})>"