# dash2/models/user.py
from . import db # Importa el objeto db desde __init__.py en la misma carpeta 'models'
from flask_login import UserMixin # Necesario si vas a usar Flask-Login para gestionar usuarios/sesiones
import datetime

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios' # Nombre de la tabla en la base de datos
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False) # Para almacenar el hash de la contraseña (¡NO contraseñas en texto plano!)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now)
    ultimo_acceso = db.Column(db.DateTime, onupdate=datetime.datetime.now) # Se actualiza automáticamente al modificar el registro

    # Relaciones (si un Usuario es también un Cliente o Admin, etc.)
    # cliente = db.relationship('Cliente', backref='usuario', uselist=False) # Ejemplo de relación uno a uno

    def __repr__(self):
        return f"<Usuario {self.email}>"

    # Métodos requeridos por Flask-Login (para autenticación y gestión de sesiones)
    def get_id(self):
        return str(self.id)

    def is_active(self):
        return True # Asumimos que los usuarios están siempre activos; puedes añadir lógica aquí

    def is_authenticated(self):
        return True # Si el usuario fue cargado, se asume que está autenticado

    def is_anonymous(self):
        return False # No es un usuario anónimo