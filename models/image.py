from . import db

class ImagenProducto(db.Model):
    __tablename__ = 'imagenes_productos'
    id = db.Column(db.Integer, primary_key=True)
    # URL segura que nos devolverá Cloudinary
    url = db.Column(db.String(512), nullable=False)
    # ID del producto al que pertenece esta imagen
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)

    def __repr__(self):
        return f"<ImagenProducto {self.id} para Producto {self.producto_id}>"