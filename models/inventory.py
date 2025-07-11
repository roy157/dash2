# dash2/models/inventory.py
from . import db
import datetime

class Inventario(db.Model):
    __tablename__ = 'inventarios'
    id = db.Column(db.Integer, primary_key=True)
    cantidad_movimiento = db.Column(db.Integer, nullable=False) # Cuántas unidades se movieron (+ para entrada, - para salida)
    tipo_movimiento = db.Column(db.String(50), nullable=False) # 'entrada', 'salida', 'ajuste'
    fecha_movimiento = db.Column(db.DateTime, default=datetime.datetime.now)
    descripcion = db.Column(db.Text) # Razón del movimiento (ej. "Recepción de proveedor", "Venta", "Inventario físico")
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)

    # Relaciones
    # 'producto' ya está definido como backref en Producto

    def __repr__(self):
        return f"<Inventario {self.id} - Prod: {self.producto_id} Tipo: {self.tipo_movimiento} Cant: {self.cantidad_movimiento}>"