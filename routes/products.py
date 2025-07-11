# dash2/routes/products.py

from flask import Blueprint, render_template, abort, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import Producto, Categoria, db

# Definimos el Blueprint con su nombre y el prefijo de URL
products_bp = Blueprint('products_bp', __name__, url_prefix='/productos')

# Ruta para listar productos
@products_bp.route('/')
@login_required
def list_products():
    selected_category_value = request.args.get('categoria', '')

    if selected_category_value:
        try:
            categoria_id = int(selected_category_value)
            productos = Producto.query.filter_by(categoria_id=categoria_id).all()
        except ValueError:
            productos = Producto.query.all()
    else:
        productos = Producto.query.all()
    
    categorias = Categoria.query.all()

    return render_template('products.html',
                           productos=productos,
                           categorias=categorias,
                           selected_category_value=selected_category_value)

# ¡NUEVA RUTA API para obtener detalles de producto como JSON!
@products_bp.route('/api/<int:product_id>', methods=['GET'])
@login_required
def get_product_json(product_id):
    producto = Producto.query.get(product_id)
    if producto is None:
        return jsonify({'message': 'Producto no encontrado'}), 404
    
    # Devuelve los datos del producto como JSON
    return jsonify({
        'id': producto.id,
        'nombre': producto.nombre,
        'descripcion': producto.descripcion,
        'precio': float(producto.precio), # Asegura que sea un float para JSON
        'stock': producto.stock,
        'categoria_id': producto.categoria_id,
        'categoria_nombre': producto.categoria.nombre if producto.categoria else 'N/A'
    })

# Ruta para ver el detalle de un producto específico (no API, renderiza HTML)
# Esta ruta es la que se llama desde index.html para "Ver Producto"
@products_bp.route('/detalle/<int:product_id>') # Cambiado a /detalle/ para evitar conflicto con /api/
@login_required
def view_product(product_id):
    producto = Producto.query.get_or_404(product_id)
    return render_template('products/detail.html', product=producto)


# Ruta para agregar un nuevo producto (modificado para respuesta JSON)
@products_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def create_product():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            precio = float(request.form['precio'])
            stock = int(request.form['stock'])
            categoria_id = request.form['categoria_id']
            
            nuevo_producto = Producto(nombre=nombre, descripcion=descripcion, precio=precio, stock=stock, categoria_id=categoria_id)
            db.session.add(nuevo_producto)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Producto creado exitosamente!', 'product_id': nuevo_producto.id}), 200
        except ValueError:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'Datos de entrada inválidos (ej. precio o stock no numéricos)'}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error al crear el producto: {str(e)}'}), 500
    
    categorias = Categoria.query.all()
    return render_template('products/create.html', categorias=categorias)

# Ruta para editar un producto existente (modificado para respuesta JSON en POST)
@products_bp.route('/editar/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Producto.query.get_or_404(product_id)

    if request.method == 'POST':
        try:
            product.nombre = request.form['nombre']
            product.descripcion = request.form['descripcion']
            product.precio = float(request.form['precio'])
            product.stock = int(request.form['stock'])
            product.categoria_id = request.form['categoria_id']
            
            db.session.commit()
            return jsonify({'success': True, 'message': 'Producto actualizado exitosamente!'}), 200
        except ValueError:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'Datos de entrada inválidos (ej. precio o stock no numéricos)'}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error al actualizar el producto: {str(e)}'}), 500
    
    categorias = Categoria.query.all()
    return render_template('products/edit.html', product=product, categorias=categorias)

# Ruta para eliminar un producto
@products_bp.route('/eliminar/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Producto.query.get_or_404(product_id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Producto eliminado exitosamente!', 'success')
        return redirect(url_for('products_bp.list_products'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el producto: {str(e)}', 'danger')
        return redirect(url_for('products_bp.list_products'))
