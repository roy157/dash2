# dash2/models/product.py
from . import db
import datetime

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    precio_compra = db.Column(db.Numeric(10, 2), nullable=True, default=0.0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    fecha_agregado = db.Column(db.DateTime, default=datetime.datetime.now)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    imagenes = db.relationship('ImagenProducto', backref='producto', lazy=True, cascade="all, delete-orphan")
    categoria = db.relationship('Categoria', backref='productos', lazy=True)

    def __repr__(self):
        return f"<Producto {self.nombre} (ID: {self.id})>"

class ImagenProducto(db.Model):
    __tablename__ = 'imagenes_productos'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(512), nullable=False)
    public_id = db.Column(db.String(255), nullable=True) # AÑADIDO: Para almacenar el public_id de Cloudinary
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)

    def __repr__(self):
        return f"<ImagenProducto {self.id} para Producto {self.producto_id}>"