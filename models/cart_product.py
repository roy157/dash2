# dash2/models/cart_product.py
from . import db

class CarritoProducto(db.Model):
    __tablename__ = 'carritos_productos'
    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False, default=1)

    carrito_id = db.Column(db.Integer, db.ForeignKey('carritos.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)

    # Restricción de unicidad para evitar duplicados del mismo producto en el mismo carrito
    __table_args__ = (db.UniqueConstraint('carrito_id', 'producto_id', name='_carrito_producto_uc'),)

    def __repr__(self):
        return f"<CarritoProducto Carrito:{self.carrito_id} Producto:{self.producto_id} Cantidad:{self.cantidad}>"