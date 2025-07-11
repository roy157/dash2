# TIENDA/routes/inventory.py

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import Inventario, Producto, db # Asegúrate de importar los modelos necesarios
from datetime import datetime

# Definimos el Blueprint para inventario
inventory_bp = Blueprint('inventory_bp', __name__, url_prefix='/inventario')

# Ruta para listar movimientos de inventario
@inventory_bp.route('/')
@login_required
def list_inventory(): # <--- ¡Cambiado de 'view_inventory' a 'list_inventory'!
    # Obtener todos los movimientos de inventario, ordenados por fecha descendente
    movimientos = Inventario.query.order_by(Inventario.fecha_movimiento.desc()).all()
    
    # También puedes obtener una lista de productos para filtros o información adicional
    productos = Producto.query.all()

    return render_template('inventory/list.html', # Asegúrate de que este template exista
                           movimientos=movimientos,
                           productos=productos)

# --- Rutas adicionales para inventario (ejemplos, puedes tener más) ---

# Ruta para registrar una entrada de inventario
@inventory_bp.route('/entrada', methods=['GET', 'POST'])
@login_required
def add_entry():
    if request.method == 'POST':
        producto_id = request.form.get('producto_id', type=int)
        cantidad = request.form.get('cantidad_movimiento', type=int) # Usar cantidad_movimiento
        descripcion = request.form.get('descripcion')

        if not producto_id or not cantidad or cantidad <= 0:
            flash('Por favor, selecciona un producto y una cantidad válida.', 'danger')
            return redirect(url_for('inventory_bp.add_entry'))
        
        try:
            producto = Producto.query.get_or_404(producto_id)
            
            # Crear el movimiento de inventario
            nuevo_movimiento = Inventario(
                producto_id=producto.id,
                cantidad_movimiento=cantidad, # Asegúrate de que el modelo Inventario tenga 'cantidad_movimiento'
                tipo_movimiento='entrada',
                fecha_movimiento=datetime.now(),
                descripcion=descripcion
            )
            db.session.add(nuevo_movimiento)
            
            # Actualizar el stock del producto
            producto.stock += cantidad
            
            db.session.commit()
            flash('Entrada de inventario registrada exitosamente!', 'success')
            return redirect(url_for('inventory_bp.list_inventory'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la entrada: {str(e)}', 'danger')
            return redirect(url_for('inventory_bp.add_entry'))

    productos = Producto.query.all()
    return render_template('inventory/add_entry.html', productos=productos)

# Ruta para registrar una salida de inventario
@inventory_bp.route('/salida', methods=['GET', 'POST'])
@login_required
def add_exit():
    if request.method == 'POST':
        producto_id = request.form.get('producto_id', type=int)
        cantidad = request.form.get('cantidad_movimiento', type=int)
        descripcion = request.form.get('descripcion')

        if not producto_id or not cantidad or cantidad <= 0:
            flash('Por favor, selecciona un producto y una cantidad válida.', 'danger')
            return redirect(url_for('inventory_bp.add_exit'))
        
        try:
            producto = Producto.query.get_or_404(producto_id)
            
            if producto.stock < cantidad:
                flash(f'Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}', 'danger')
                return redirect(url_for('inventory_bp.add_exit'))

            # Crear el movimiento de inventario
            nuevo_movimiento = Inventario(
                producto_id=producto.id,
                cantidad_movimiento=cantidad,
                tipo_movimiento='salida',
                fecha_movimiento=datetime.now(),
                descripcion=descripcion
            )
            db.session.add(nuevo_movimiento)
            
            # Actualizar el stock del producto
            producto.stock -= cantidad
            
            db.session.commit()
            flash('Salida de inventario registrada exitosamente!', 'success')
            return redirect(url_for('inventory_bp.list_inventory'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la salida: {str(e)}', 'danger')
            return redirect(url_for('inventory_bp.add_exit'))

    productos = Producto.query.all()
    return render_template('inventory/add_exit.html', productos=productos)

# Ruta API para obtener detalles de un movimiento de inventario (si necesitas un modal de detalle)
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
