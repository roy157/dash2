# models/user.py
from . import db
from flask_login import UserMixin
# Asegúrate de importar esto al principio del archivo
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(80), nullable=False, default='Vendedor')
    
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now)
    ultimo_acceso = db.Column(db.DateTime, onupdate=datetime.datetime.now)

    def __repr__(self):
        return f"<Usuario {self.email}>"

    # --- AÑADE ESTOS MÉTODOS ---
    def set_password(self, password):
        """Crea un hash de la contraseña y la guarda."""
        self.password = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Verifica la contraseña contra el hash guardado."""
        return check_password_hash(self.password, password)
    # ---------------------------

    # Métodos de Flask-Login (sin cambios)
    def get_id(self):
        return str(self.id)
    # ... (el resto de tus métodos)