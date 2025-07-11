# dash2/models/category.py
from . import db

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(45), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    imagen_url = db.Column(db.String(255)) # URL de imagen para la categoría (si tienes)

    # La relación inversa 'productos' ya está definida en el modelo Producto

    def __repr__(self):
        return f"<Categoria {self.nombre}>"