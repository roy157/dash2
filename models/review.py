# dash2/models/review.py
from . import db
import datetime

class Reseña(db.Model):
    __tablename__ = 'reseñas'
    id = db.Column(db.Integer, primary_key=True)
    calificacion = db.Column(db.Integer, nullable=False) # Ej: 1, 2, 3, 4, 5 estrellas
    comentario = db.Column(db.Text)
    fecha_reseña = db.Column(db.DateTime, default=datetime.datetime.now)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)

    # Relaciones
    # 'producto' y 'cliente' ya están definidos como backrefs en Producto y Cliente respectivamente

    def __repr__(self):
        return f"<Reseña {self.id} (Cal: {self.calificacion}) de Cliente {self.cliente_id} para Producto {self.producto_id}>"