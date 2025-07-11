from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config  # Asegúrate de que este sea el nombre correcto de tu archivo

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

def test_connection():
    try:
        # ¡Importante! Usa app.app_context() para crear un contexto de aplicación
        with app.app_context():
            # Opción 1: Prueba básica de conexión
            db.engine.connect()
            print("✅ ¡Conexión exitosa a la base de datos!")

            # Opción 2: Ejecuta una consulta SQL simple para mayor seguridad
            # result = db.session.execute("SELECT 1")
            # print("Resultado de prueba:", result.fetchone())
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    test_connection()  # Llama a la función dentro del contexto adecuado