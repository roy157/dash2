# dash2/models/sale_product.py
from . import db
from sqlalchemy.schema import PrimaryKeyConstraint # Importar para definir PK compuesta si es necesario

class VentaProducto(db.Model):
    __tablename__ = 'ventas_productos'
    # Cambiamos 'id' a 'ventaproducto_id' para que coincida con tu BD
    ventaproducto_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False) # Precio del producto en el momento de la venta

    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)

    # Si tu tabla ventas_productos NO tiene un ID propio y es una tabla de unión pura,
    # y si la clave primaria es la combinación de venta_id y producto_id,
    # entonces deberías usar esto en lugar de 'ventaproducto_id' como PK:
    # __table_args__ = (PrimaryKeyConstraint('venta_id', 'producto_id'),)
    # Pero tu SQL dump muestra que tiene 'ventaproducto_id' como PK, así que la primera opción es correcta.

    def __repr__(self):
        return f"<VentaProducto Venta:{self.venta_id} Producto:{self.producto_id} Cantidad:{self.cantidad}>"

