# TIENDA/app.py

from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from config import Config
from models import db, Usuario, Producto, Pedido, Cliente, PedidoProducto, VentaProducto, Categoria
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, current_user
from datetime import date, datetime, timedelta
from sqlalchemy import func
import os # <-- IMPORTACIÓN AÑADIDA
import cloudinary # <-- IMPORTACIÓN AÑADIDA

# =========================================================
# IMPORTE DE BLUEPRINTS
# =========================================================
from routes.auth import auth_bp
from routes.products import products_bp
from routes.clients import clients_bp
from routes.orders import orders_bp
from routes.inventory import inventory_bp
from routes.reports import reports_bp
from routes.main import main_bp
from routes.settings import settings_bp

app = Flask(__name__)
app.config.from_object(Config)

# =========================================================
# INICIALIZACIÓN DE EXTENSIONES DE FLASK
# =========================================================
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# <-- BLOQUE DE CONFIGURACIÓN DE CLOUDINARY AÑADIDO -->
# Es una buena práctica colocarlo junto a otras inicializaciones de servicios.
cloudinary.config(
  cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', 'dv7iofqda'), 
  api_key = os.environ.get('CLOUDINARY_API_KEY', '312927972217246'),
  api_secret = os.environ.get('CLOUDINARY_API_SECRET', 'bKe_P5L16OAtUOdwHZoqLxFRLtw')
)
# <-- FIN DEL BLOQUE AÑADIDO -->

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# =========================================================
# REGISTRO DE BLUEPRINTS
# =========================================================
app.register_blueprint(auth_bp)
app.register_blueprint(products_bp)
app.register_blueprint(clients_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(main_bp)
app.register_blueprint(settings_bp) # <-- 2. REGISTRO AÑADIDO

# =========================================================
# RUTAS PRINCIPALES DEL DASHBOARD (HOME)
# =========================================================
@app.route('/')
@login_required
def index():
    # --- Obtener datos para las tarjetas del Dashboard ---
    total_productos = Producto.query.count()
    total_pedidos = Pedido.query.count()
    total_clientes = Cliente.query.count()

    today = date.today()
    start_of_today = datetime(today.year, today.month, today.day, 0, 0, 0)
    end_of_today = datetime(today.year, today.month, today.day, 23, 59, 59, 999999)

    sales_today_raw = db.session.query(func.sum(Pedido.total)).filter(
        Pedido.fecha_pedido >= start_of_today,
        Pedido.fecha_pedido <= end_of_today,
        (Pedido.estado == 'enviado') | (Pedido.estado == 'entregado')
    ).scalar()
    sales_today = float(sales_today_raw) if sales_today_raw is not None else 0.00

    pedidos_pendientes = Pedido.query.filter_by(estado='pendiente').count()

    nuevos_clientes_hoy = Cliente.query.filter(
        Cliente.fecha_registro >= start_of_today,
        Cliente.fecha_registro <= end_of_today
    ).count()

    stock_bajo = Producto.query.filter(Producto.stock < 10).count()

    pedidos_recientes_query = db.session.query(
        Pedido.id,
        Pedido.total,
        Pedido.estado,
        Cliente.nombre.label('cliente_nombre'),
        Pedido.fecha_pedido,
        func.sum(PedidoProducto.cantidad).label('num_productos_total')
    ).join(Cliente, Pedido.cliente_id == Cliente.id)\
     .outerjoin(PedidoProducto, Pedido.id == PedidoProducto.pedido_id)\
     .group_by(Pedido.id, Pedido.total, Pedido.estado, Cliente.nombre, Pedido.fecha_pedido)\
     .order_by(Pedido.fecha_pedido.desc())\
     .limit(5).all()

    formatted_pedidos_recientes = []
    for p in pedidos_recientes_query:
        formatted_pedidos_recientes.append({
            'id': p.id,
            'cliente_nombre': p.cliente_nombre,
            'num_productos': int(p.num_productos_total) if p.num_productos_total is not None else 0,
            'total': float(p.total),
            'estado': p.estado,
            'fecha_pedido': p.fecha_pedido.strftime('%d/%m/%Y %H:%M')
        })

    productos_mas_vendidos_query = db.session.query(
        Producto.id,
        Producto.nombre,
        Producto.stock,
        Categoria.nombre.label('categoria_nombre'),
        func.sum(VentaProducto.cantidad).label('total_vendido')
    ).join(VentaProducto, Producto.id == VentaProducto.producto_id)\
     .join(Categoria, Producto.categoria_id == Categoria.id) \
     .group_by(Producto.id, Producto.nombre, Producto.stock, Categoria.nombre)\
     .order_by(func.sum(VentaProducto.cantidad).desc())\
     .limit(5).all()

    formatted_productos_mas_vendidos = []
    for p in productos_mas_vendidos_query:
        # Aseguramos que 'id' sea un entero válido para url_for
        product_id_for_url = int(p.id) if p.id is not None else 0 
        formatted_productos_mas_vendidos.append({
            'id': product_id_for_url,
            'nombre': p.nombre,
            'categoria_nombre': p.categoria_nombre,
            'ventas_totales': int(p.total_vendido) if p.total_vendido is not None else 0,
            'stock': p.stock
        })

    return render_template('index.html',
                           total_productos=total_productos,
                           total_pedidos=total_pedidos,
                           total_clientes=total_clientes,
                           sales_today=sales_today,
                           pedidos_pendientes=pedidos_pendientes,
                           nuevos_clientes_hoy=nuevos_clientes_hoy,
                           stock_bajo=stock_bajo,
                           pedidos_recientes=formatted_pedidos_recientes,
                           productos_mas_vendidos=formatted_productos_mas_vendidos)

# =========================================================
# MANEJADORES DE ERRORES
# =========================================================
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# =========================================================
# PUNTO DE ENTRADA PARA EJECUTAR LA APLICACIÓN
# =========================================================
if __name__ == '__main__':
    with app.app_context():
        # db.create_all() # Descomentar SOLO si es la PRIMERA VEZ que inicias la BD y NO tienes migraciones.
                        # Si ya tienes tablas o usas Flask-Migrate, déjalo COMENTADO.

        from werkzeug.security import generate_password_hash
        
        # Crear usuario administrador si no existe
        if Usuario.query.count() == 0:
            hashed_password = generate_password_hash('adminpass', method='pbkdf2:sha256')
            admin_user = Usuario(email='admin@techadmin.com', password=hashed_password)
            db.session.add(admin_user)
            db.session.commit()
            print("Usuario administrador de ejemplo creado: admin@techadmin.com / adminpass")
        
        # Datos de ejemplo para poblar tu BD para pruebas si está vacía.
        # Asegúrate de que los modelos correspondientes estén importados.

        if Categoria.query.count() == 0:
            cat1 = Categoria(nombre='Laptop')
            cat2 = Categoria(nombre='Periféricos')
            db.session.add_all([cat1, cat2])
            db.session.commit()
            print("Categorías de ejemplo creadas.")

        if Cliente.query.count() == 0:
            cliente1 = Cliente(nombre='Juan Pérez', direccion='Calle Falsa 123', telefono='555-1234', email='juan@example.com', fecha_registro=datetime.now())
            db.session.add(cliente1)
            db.session.commit()
            print("Cliente de ejemplo creado.")

        if Producto.query.count() == 0:
            cat_laptop = Categoria.query.filter_by(nombre='Laptop').first()
            cat_perifericos = Categoria.query.filter_by(nombre='Periféricos').first()
            if cat_laptop and cat_perifericos:
                prod1 = Producto(nombre='Laptop Dell Inspiron 15', descripcion='Laptop para uso diario', precio=700.00, stock=10, categoria_id=cat_laptop.id)
                prod2 = Producto(nombre='Mouse Logitech G203', descripcion='Mouse gamer RGB', precio=35.00, stock=50, categoria_id=cat_perifericos.id)
                db.session.add_all([prod1, prod2])
                db.session.commit()
                print("Productos de ejemplo creados.")

        if Pedido.query.count() == 0:
            cliente_ejemplo = Cliente.query.first()
            prod_laptop = Producto.query.filter_by(nombre='Laptop Dell Inspiron 15').first()
            prod_mouse = Producto.query.filter_by(nombre='Mouse Logitech G203').first()

            if cliente_ejemplo and prod_laptop and prod_mouse:
                # Pedido Pendiente
                pedido_p = Pedido(direccion_envio='Direccion de Juan', estado='pendiente', total=735.00, fecha_pedido=datetime.now(), cliente_id=cliente_ejemplo.id)
                db.session.add(pedido_p)
                db.session.commit() # Commit para obtener el ID del pedido
                
                pp1 = PedidoProducto(pedido_id=pedido_p.id, producto_id=prod_laptop.id, cantidad=1, precio_unitario=prod_laptop.precio)
                pp2 = PedidoProducto(pedido_id=pedido_p.id, producto_id=prod_mouse.id, cantidad=1, precio_unitario=prod_mouse.precio)
                db.session.add_all([pp1, pp2])
                db.session.commit()
                print("Pedido pendiente de ejemplo creado.")

                # Pedido Enviado (para ventas de hoy)
                pedido_e = Pedido(direccion_envio='Otra Direccion', estado='enviado', total=700.00, fecha_pedido=datetime.now(), cliente_id=cliente_ejemplo.id)
                db.session.add(pedido_e)
                db.session.commit()
                
                pp3 = PedidoProducto(pedido_id=pedido_e.id, producto_id=prod_laptop.id, cantidad=1, precio_unitario=prod_laptop.precio)
                db.session.add(pp3)
                db.session.commit()
                print("Pedido enviado de ejemplo creado.")

        if VentaProducto.query.count() == 0:
            prod_laptop = Producto.query.filter_by(nombre='Laptop Dell Inspiron 15').first()
            prod_mouse = Producto.query.filter_by(nombre='Mouse Logitech G203').first()
            if prod_laptop and prod_mouse:
                vp1 = VentaProducto(producto_id=prod_laptop.id, cantidad=5, precio_unitario=prod_laptop.precio) # 5 laptops vendidas
                vp2 = VentaProducto(producto_id=prod_mouse.id, cantidad=10, precio_unitario=prod_mouse.precio) # 10 mouses vendidos
                db.session.add_all([vp1, vp2])
                db.session.commit()
                print("VentaProducto de ejemplo creado.")


    app.run(debug=True)
