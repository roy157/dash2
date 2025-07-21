# dash2/models/__init__.py

from flask_sqlalchemy import SQLAlchemy

# Crea una instancia de SQLAlchemy pero no la inicialices con la app aquí.
# La inicializaremos en app.py usando db.init_app(app).
# Esto permite que 'db' sea importado en los modelos sin una dependencia circular con la 'app'.
db = SQLAlchemy()

# Importa todos tus modelos aquí.
# ASEGÚRATE de que el nombre del archivo (ej. user.py)
# y el nombre de la clase (ej. Usuario) coincidan con estas importaciones.
# Si cambias un nombre de archivo, o agregas uno nuevo, actualiza esta lista.

from .user import Usuario
from .client import Cliente
from .product import Producto, ImagenProducto
from .category import Categoria
from .order import Pedido
from .payment import Pago
from .review import Reseña
from .cart import Carrito
from .sale import Venta
from .inventory import Inventario
from .order_product import PedidoProducto
from .cart_product import CarritoProducto
from .sale_product import VentaProducto

# Puedes definir funciones o clases comunes a todos los modelos aquí si es necesario.