# TIENDA/routes/inventory.py

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import Inventario, Producto, db # Asegúrate de importar los modelos necesarios
from datetime import datetime

# Definimos el Blueprint para inventario
inventory_bp = Blueprint('inventory_bp', __name__, url_prefix='/inventario')

# --- ESTA FUNCIÓN NO CAMBIA ---
# Ruta para listar el stock de productos (tu plantilla inventario.html)
@inventory_bp.route('/')
@login_required
def list_inventory():
    # Esta consulta obtiene todos los productos para mostrar su stock,
    # que es lo que tu plantilla necesita.
    productos = Producto.query.order_by(Producto.nombre).all()

    # Renderiza la plantilla principal de inventario
    return render_template('inventario.html', 
                           productos=productos)

# --- ESTA FUNCIÓN SÍ SE MODIFICA ---
# Ruta para registrar una entrada de inventario
@inventory_bp.route('/entrada', methods=['GET', 'POST'])
@login_required
def add_entry():
    # Si la petición es POST (desde el modal), devuelve JSON
    if request.method == 'POST':
        producto_id = request.form.get('producto_id', type=int)
        cantidad = request.form.get('cantidad_movimiento', type=int)
        descripcion = request.form.get('descripcion')

        if not producto_id or not cantidad or cantidad <= 0:
            return jsonify({'success': False, 'message': 'Datos inválidos.'}), 400
        
        try:
            producto = Producto.query.get_or_404(producto_id)
            
            nuevo_movimiento = Inventario(
                producto_id=producto.id,
                cantidad_movimiento=cantidad,
                tipo_movimiento='entrada',
                fecha_movimiento=datetime.now(),
                descripcion=descripcion
            )
            db.session.add(nuevo_movimiento)
            producto.stock += cantidad
            db.session.commit()
            return jsonify({'success': True, 'message': 'Entrada registrada exitosamente!'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error en el servidor: {str(e)}'}), 500

    # Si la petición es GET, renderiza la página HTML como antes
    # Esto mantiene la compatibilidad por si tienes un enlace directo a esta página.
    productos = Producto.query.all()
    return render_template('inventory/add_entry.html', productos=productos)


# --- ESTA FUNCIÓN TAMBIÉN SE MODIFICA ---
# Ruta para registrar una salida de inventario
@inventory_bp.route('/salida', methods=['GET', 'POST'])
@login_required
def add_exit():
    # Si la petición es POST (desde el modal), devuelve JSON
    if request.method == 'POST':
        producto_id = request.form.get('producto_id', type=int)
        cantidad = request.form.get('cantidad_movimiento', type=int)
        descripcion = request.form.get('descripcion')

        if not producto_id or not cantidad or cantidad <= 0:
            return jsonify({'success': False, 'message': 'Datos inválidos.'}), 400
        
        try:
            producto = Producto.query.get_or_404(producto_id)
            
            if producto.stock < cantidad:
                return jsonify({'success': False, 'message': f'Stock insuficiente. Disponible: {producto.stock}'}), 400

            nuevo_movimiento = Inventario(
                producto_id=producto.id,
                cantidad_movimiento=cantidad,
                tipo_movimiento='salida',
                fecha_movimiento=datetime.now(),
                descripcion=descripcion
            )
            db.session.add(nuevo_movimiento)
            producto.stock -= cantidad
            db.session.commit()
            return jsonify({'success': True, 'message': 'Salida registrada exitosamente!'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error en el servidor: {str(e)}'}), 500

    # Si la petición es GET, renderiza la página HTML como antes
    productos = Producto.query.all()
    return render_template('inventory/add_exit.html', productos=productos)

# --- ESTA FUNCIÓN NO CAMBIA ---
# Ruta API para obtener detalles de un movimiento de inventario
@inventory_bp.route('/<int:movimiento_id>/json')
@login_required
def get_inventory_movement_json(movimiento_id):
    movimiento = Inventario.query.get_or_404(movimiento_id)
    producto = Producto.query.get(movimiento.producto_id)

    return jsonify({
        'id': movimiento.id,
        'producto_nombre': producto.nombre if producto else 'N/A',
        'cantidad_movimiento': movimiento.cantidad_movimiento,
        'tipo_movimiento': movimiento.tipo_movimiento,
        'fecha_movimiento': movimiento.fecha_movimiento.isoformat(),
        'descripcion': movimiento.descripcion
    })