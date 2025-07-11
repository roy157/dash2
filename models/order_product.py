# dash2/models/order_product.py
from . import db

class PedidoProducto(db.Model):
    __tablename__ = 'pedidos_productos'
    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False) # Precio del producto en el momento exacto de la compra

    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)

    # La restricción de unicidad asegura que una combinación de pedido_id y producto_id solo aparezca una vez
    __table_args__ = (db.UniqueConstraint('pedido_id', 'producto_id', name='_pedido_producto_uc'),)

    def __repr__(self):
        return f"<PedidoProducto Pedido:{self.pedido_id} Producto:{self.producto_id} Cantidad:{self.cantidad}>"