# dash2/models/payment.py
from . import db
import datetime

class Pago(db.Model):
    __tablename__ = 'pagos'
    id = db.Column(db.Integer, primary_key=True)
    monto_pago = db.Column(db.Numeric(10, 2), nullable=False)
    metodo_pago = db.Column(db.String(50), nullable=False) # Ej: "Tarjeta de Crédito", "PayPal", "Transferencia Bancaria"
    fecha_pago = db.Column(db.DateTime, default=datetime.datetime.now)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)

    # Relaciones
    # 'pedido' ya está definido como backref en Pedido

    def __repr__(self):
        return f"<Pago {self.id} de ${self.monto_pago} para Pedido {self.pedido_id}>"