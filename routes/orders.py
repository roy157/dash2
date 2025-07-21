# TIENDA/routes/orders.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from models import Pedido, db, Cliente, PedidoProducto, Producto, VentaProducto, Categoria
from sqlalchemy import func
from datetime import datetime, date

orders_bp = Blueprint('orders_bp', __name__, url_prefix='/pedidos')

@orders_bp.route('/')
@login_required
def list_orders():
    pedidos = Pedido.query.order_by(Pedido.fecha_pedido.desc()).all() 

    # --- Cálculo de estadísticas para las tarjetas ---
    total_pedidos = Pedido.query.count()
    pedidos_pendientes = Pedido.query.filter_by(estado='pendiente').count()

    ventas_totales_query = db.session.query(func.sum(Pedido.total)).filter(
        (Pedido.estado == 'enviado') | (Pedido.estado == 'entregado')
    ).scalar()
    ventas_totales = float(ventas_totales_query) if ventas_totales_query is not None else 0.00
    
    today = date.today()
    start_of_today = datetime(today.year, today.month, today.day, 0, 0, 0)
    end_of_today = datetime(today.year, today.month, today.day, 23, 59, 59, 999999)

    pedidos_hoy = Pedido.query.filter(
        Pedido.fecha_pedido >= start_of_today,
        Pedido.fecha_pedido <= end_of_today
    ).count()
    
    ventas_hoy_query = db.session.query(func.sum(Pedido.total)).filter(
        Pedido.fecha_pedido >= start_of_today,
        Pedido.fecha_pedido <= end_of_today,
        (Pedido.estado == 'enviado') | (Pedido.estado == 'entregado')
    ).scalar()
    ventas_hoy = float(ventas_hoy_query) if ventas_hoy_query is not None else 0.00

    return render_template('orders/list.html', 
                           pedidos=pedidos,
                           total_pedidos=total_pedidos,
                           pedidos_pendientes=pedidos_pendientes,
                           ventas_totales=ventas_totales,
                           pedidos_hoy=pedidos_hoy,
                           ventas_hoy=ventas_hoy)

# --- Ruta para ver los detalles de un pedido específico (versión HTML) ---
@orders_bp.route('/<int:order_id>')
@login_required
def view_order(order_id):
    order = Pedido.query.get_or_404(order_id)
    client = Cliente.query.get_or_404(order.cliente_id)

    # MODIFICADO: Añadimos .options(db.joinedload(Producto.imagenes)) para cargar las imágenes eficientemente
    products_in_order_query = db.session.query(
        PedidoProducto,
        Producto,
        Categoria
    ).join(Producto, PedidoProducto.producto_id == Producto.id)\
     .join(Categoria, Producto.categoria_id == Categoria.id)\
     .options(db.joinedload(Producto.imagenes))\
     .filter(PedidoProducto.pedido_id == order_id).all()

    formatted_products = []
    for pp, product, category in products_in_order_query:
        # LÍNEA CORREGIDA: Usamos la nueva relación 'imagenes'
        image_url = product.imagenes[0].url if product.imagenes else 'https://via.placeholder.com/50x50?text=No+Img'
        
        formatted_products.append({
            'product_id': product.id,
            'name': product.nombre,
            'description': product.descripcion,
            'quantity': pp.cantidad,
            'unit_price': float(pp.precio),
            'subtotal': float(pp.cantidad * pp.precio),
            'stock': product.stock,
            'image_url': image_url, # Variable con la URL corregida
            'category_name': category.nombre
        })
    
    return render_template('orders/view_order.html', 
                           order=order, 
                           client=client, 
                           products=formatted_products)

# --- NUEVA RUTA: Para obtener detalles del pedido en formato JSON para el modal ---
@orders_bp.route('/<int:order_id>/json')
@login_required
def get_order_details_json(order_id):
    order = Pedido.query.get_or_404(order_id)
    client = Cliente.query.get(order.cliente_id) if order.cliente_id else None

    # MODIFICADO: Añadimos .options(db.joinedload(Producto.imagenes)) para cargar las imágenes eficientemente
    products_in_order_query = db.session.query(
        PedidoProducto,
        Producto,
        Categoria
    ).join(Producto, PedidoProducto.producto_id == Producto.id)\
     .join(Categoria, Producto.categoria_id == Categoria.id)\
     .options(db.joinedload(Producto.imagenes))\
     .filter(PedidoProducto.pedido_id == order_id).all()

    formatted_products = []
    for pp, product, category in products_in_order_query:
        # LÍNEA CORREGIDA: Usamos la nueva relación 'imagenes'
        image_url = product.imagenes[0].url if product.imagenes else 'https://via.placeholder.com/50x50?text=No+Img'

        formatted_products.append({
            'product_id': product.id,
            'name': product.nombre,
            'description': product.descripcion,
            'quantity': pp.cantidad,
            'unit_price': float(pp.precio),
            'subtotal': float(pp.cantidad * pp.precio),
            'stock': product.stock,
            'image_url': image_url, # Variable con la URL corregida
            'category_name': category.nombre
        })
    
    order_data = {
        'id': order.id,
        'cliente_id': order.cliente_id,
        'fecha_pedido': order.fecha_pedido.isoformat(),
        'direccion_envio': order.direccion_envio,
        'total': float(order.total),
        'estado': order.estado
    }

    client_data = {
        'id': client.id if client else None,
        'nombre': client.nombre if client else 'Invitado',
        'email': client.email if client else 'N/A',
        'telefono': client.telefono if client else 'N/A',
    }

    return jsonify(order=order_data, client=client_data, products=formatted_products)

# --- Ruta para crear un nuevo pedido ---
@orders_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def create_order():
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id', type=int)
        direccion_envio = request.form.get('direccion_envio')
        
        productos_seleccionados = []
        for key, value in request.form.items():
            if key.startswith('producto_id_'):
                prod_id_str = request.form.get(key)
                if not prod_id_str:
                    continue
                prod_id = int(prod_id_str)
                
                cantidad_key = f'cantidad_{key.split("_")[-1]}'
                cantidad_str = request.form.get(cantidad_key, '0')
                cantidad = int(cantidad_str)

                if cantidad > 0:
                    productos_seleccionados.append({'producto_id': prod_id, 'cantidad': cantidad})

        if not cliente_id or not productos_seleccionados or not direccion_envio:
            flash('Debes seleccionar un cliente, una dirección de envío y al menos un producto con cantidad mayor a cero.', 'danger')
            return redirect(url_for('orders_bp.create_order'))

        try:
            total_pedido = 0.0
            pedido_productos_list = []
            
            for item in productos_seleccionados:
                producto = Producto.query.get(item['producto_id'])
                if not producto:
                    flash(f"Producto con ID {item['producto_id']} no encontrado.", 'danger')
                    db.session.rollback()
                    return redirect(url_for('orders_bp.create_order'))
                
                if producto.stock < item['cantidad']:
                    flash(f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}", 'danger')
                    db.session.rollback()
                    return redirect(url_for('orders_bp.create_order'))

                total_item = float(producto.precio) * item['cantidad']
                total_pedido += total_item
                
                pedido_productos_list.append(
                    PedidoProducto(
                        producto_id=producto.id,
                        cantidad=item['cantidad'],
                        precio=producto.precio
                    )
                )

            new_order = Pedido(
                cliente_id=cliente_id,
                fecha_pedido=datetime.now(),
                direccion_envio=direccion_envio,
                total=total_pedido,
                estado='pendiente'
            )
            
            db.session.add(new_order)
            db.session.flush() 

            for pp_item in pedido_productos_list:
                pp_item.pedido_id = new_order.id
                db.session.add(pp_item)
                
                producto_a_actualizar = Producto.query.get(pp_item.producto_id)
                if producto_a_actualizar:
                    producto_a_actualizar.stock -= pp_item.cantidad
            
            db.session.commit()

            flash('Pedido creado exitosamente.', 'success')
            return redirect(url_for('orders_bp.list_orders'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el pedido: {e}', 'danger')
            return redirect(url_for('orders_bp.create_order'))

    clientes = Cliente.query.all()
    productos = Producto.query.all()
    return render_template('orders/create_order.html', clientes=clientes, productos=productos)

# --- Ruta para editar un pedido ---
@orders_bp.route('/editar/<int:order_id>', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    order = Pedido.query.get_or_404(order_id)
    clientes = Cliente.query.all()
    
    current_order_items = PedidoProducto.query.filter_by(pedido_id=order_id).all()
    productos_disponibles = Producto.query.all()
    
    if request.method == 'POST':
        try:
            estado_original = request.form.get('estado_original')

            order.cliente_id = request.form.get('cliente_id', type=int)
            order.estado = request.form.get('estado')
            order.direccion_envio = request.form.get('direccion_envio')

            if order.estado == 'cancelado' and estado_original != 'cancelado':
                for item in current_order_items:
                    producto = Producto.query.get(item.producto_id)
                    if producto:
                        producto.stock += item.cantidad
            
            db.session.commit()
            flash('Pedido actualizado exitosamente.', 'success')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'Pedido actualizado exitosamente!'})
            else:
                return redirect(url_for('orders_bp.view_order', order_id=order.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el pedido: {e}', 'danger')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': f'Error al actualizar el pedido: {str(e)}'}), 500
            else:
                return redirect(url_for('orders_bp.edit_order', order_id=order.id))

    return render_template('orders/edit_order.html', 
                           order=order, 
                           clientes=clientes,
                           current_order_items=current_order_items,
                           productos_disponibles=productos_disponibles)

# --- Ruta para eliminar un pedido ---
@orders_bp.route('/eliminar/<int:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    order = Pedido.query.get_or_404(order_id)
    try:
        order_items_to_delete = PedidoProducto.query.filter_by(pedido_id=order_id).all()
        for item in order_items_to_delete:
            producto = Producto.query.get(item.producto_id)
            if producto:
                producto.stock += item.cantidad
            db.session.delete(item)

        db.session.delete(order)
        db.session.commit()
        flash('Pedido eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el pedido: {e}', 'danger')
    return redirect(url_for('orders_bp.list_orders'))

# --- Ruta para cambiar el estado de un pedido (ejemplo rápido) ---
@orders_bp.route('/cambiar_estado/<int:order_id>/<string:new_status>', methods=['POST'])
@login_required
def change_order_status(order_id, new_status):
    order = Pedido.query.get_or_404(order_id)
    allowed_statuses = ['pendiente', 'procesando', 'enviado', 'entregado', 'cancelado']

    if new_status not in allowed_statuses:
        flash(f'Estado "{new_status}" no válido.', 'danger')
        return redirect(url_for('orders_bp.view_order', order_id=order.id))
    
    try:
        if (new_status == 'enviado' or new_status == 'entregado') and \
           (order.estado != 'enviado' and order.estado != 'entregado'):
            
            # Asumiendo que no tienes un modelo Venta separado y que la lógica de ventas es conceptual
            for pp_item in PedidoProducto.query.filter_by(pedido_id=order.id).all():
                existing_venta_producto = VentaProducto.query.filter_by(
                    producto_id=pp_item.producto_id
                ).first()

                if existing_venta_producto:
                    # Si ya existe una entrada para este producto, actualiza la cantidad
                    # Esta lógica puede necesitar ser más compleja (ej. agrupar por mes/año)
                    # Por ahora, simplemente sumamos a la cantidad existente
                    # existing_venta_producto.cantidad += pp_item.cantidad
                    pass # O define una lógica más clara para ventas repetidas del mismo producto
                else: 
                    # Si no existe, créala
                    venta_producto = VentaProducto(
                        producto_id=pp_item.producto_id,
                        cantidad=pp_item.cantidad,
                        precio_unitario=pp_item.precio
                    )
                    db.session.add(venta_producto)
        
        if new_status == 'cancelado' and order.estado != 'cancelado':
                 for item in PedidoProducto.query.filter_by(pedido_id=order.id).all():
                    producto = Producto.query.get(item.producto_id)
                    if producto:
                        producto.stock += item.cantidad
        
        order.estado = new_status
        db.session.commit()
        flash(f'Estado del pedido {order.id} actualizado a "{new_status}".', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar el estado del pedido: {e}', 'danger')
    
    return redirect(url_for('orders_bp.view_order', order_id=order.id))