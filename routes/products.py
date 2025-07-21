# dash2/routes/products.py

from flask import Blueprint, render_template, abort, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import Producto, Categoria, db, ImagenProducto
import cloudinary.uploader
import cloudinary # Importar también para el método destroy

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
            # Usamos 'imagenes' para poder mostrar la miniatura en la tabla
            productos = Producto.query.options(db.joinedload(Producto.imagenes)).filter_by(categoria_id=categoria_id).all()
        except ValueError:
            productos = Producto.query.options(db.joinedload(Producto.imagenes)).all()
    else:
        # Usamos 'imagenes' para poder mostrar la miniatura en la tabla
        productos = Producto.query.options(db.joinedload(Producto.imagenes)).all()
    
    categorias = Categoria.query.all()

    return render_template('products.html',
                           productos=productos,
                           categorias=categorias,
                           selected_category_value=selected_category_value)

# Ruta API para obtener datos de un producto (MODIFICADA)
@products_bp.route('/api/<int:product_id>', methods=['GET'])
@login_required
def get_product_json(product_id):
    producto = Producto.query.options(db.joinedload(Producto.imagenes)).get(product_id) # Cargar también las imágenes
    if producto is None:
        return jsonify({'message': 'Producto no encontrado'}), 404
    
    # Devuelve los datos del producto como JSON, incluyendo ID y URL de cada imagen
    return jsonify({
        'id': producto.id,
        'nombre': producto.nombre,
        'descripcion': producto.descripcion,
        'precio': float(producto.precio),
        'stock': producto.stock,
        'categoria_id': producto.categoria_id,
        'categoria_nombre': producto.categoria.nombre if producto.categoria else 'N/A',
        # MODIFICADO: Incluye el ID, URL y public_id de la imagen
        'imagenes': [{'id': imagen.id, 'url': imagen.url, 'public_id': imagen.public_id} for imagen in producto.imagenes]
    })

# NUEVA RUTA: Para eliminar una imagen específica de un producto
@products_bp.route('/api/delete-image/<int:image_id>', methods=['DELETE'])
@login_required
def delete_product_image(image_id):
    imagen = ImagenProducto.query.get(image_id)
    if not imagen:
        return jsonify({'message': 'Imagen no encontrada'}), 404

    try:
        # Usa el public_id almacenado directamente
        if imagen.public_id:
            cloudinary.uploader.destroy(imagen.public_id)
        
        db.session.delete(imagen)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Imagen eliminada exitosamente.'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar imagen de Cloudinary/DB: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al eliminar la imagen: {str(e)}'}), 500


# Ruta para ver el detalle de un producto
@products_bp.route('/detalle/<int:product_id>')
@login_required
def view_product(product_id):
    producto = Producto.query.get_or_404(product_id)
    return render_template('products/detail.html', product=producto)


# Ruta para crear un producto (MODIFICADA para guardar public_id)
@products_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def create_product():
    if request.method == 'POST':
        try:
            nuevo_producto = Producto(
                nombre=request.form['nombre'],
                descripcion=request.form['descripcion'],
                precio=float(request.form['precio']),
                stock=int(request.form['stock']),
                categoria_id=request.form['categoria_id']
            )
            db.session.add(nuevo_producto)
            db.session.flush()

            imagenes = request.files.getlist('imagenes')
            for imagen in imagenes:
                if imagen and imagen.filename:
                    upload_result = cloudinary.uploader.upload(imagen)
                    
                    nueva_imagen = ImagenProducto(
                        url=upload_result['secure_url'],
                        public_id=upload_result['public_id'], # AÑADIDO
                        producto_id=nuevo_producto.id
                    )
                    db.session.add(nueva_imagen)

            db.session.commit()
            return jsonify({'success': True, 'message': '¡Producto creado exitosamente!'}), 200
        except ValueError:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'Datos de entrada inválidos (ej. precio o stock no numéricos)'}), 400
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear el producto: {str(e)}")
            return jsonify({'success': False, 'message': f'Error al crear el producto: {str(e)}'}), 500
    
    categorias = Categoria.query.all()
    return render_template('products/create.html', categorias=categorias)

# Ruta para editar un producto (MODIFICADA para guardar public_id)
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
            
            imagenes = request.files.getlist('imagenes')
            for imagen in imagenes:
                if imagen and imagen.filename:
                    upload_result = cloudinary.uploader.upload(imagen)
                    
                    nueva_imagen = ImagenProducto(
                        url=upload_result['secure_url'],
                        public_id=upload_result['public_id'], # AÑADIDO
                        producto_id=product.id
                    )
                    db.session.add(nueva_imagen)
            
            db.session.commit()
            return jsonify({'success': True, 'message': '¡Producto actualizado exitosamente!'}), 200
            
        except ValueError:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'Datos de entrada inválidos (ej. precio o stock no numéricos)'}), 400
        except Exception as e:
            db.session.rollback()
            print(f"Error al actualizar el producto: {str(e)}")
            return jsonify({'success': False, 'message': f'Error al actualizar el producto: {str(e)}'}), 500
    
    categorias = Categoria.query.all()
    return render_template('products/edit.html', product=product, categorias=categorias)

# Ruta para eliminar un producto
@products_bp.route('/eliminar/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Producto.query.get_or_404(product_id)
    try:
        # Eliminar imágenes asociadas de Cloudinary antes de borrar el producto
        for imagen in product.imagenes:
            try:
                if imagen.public_id:
                    cloudinary.uploader.destroy(imagen.public_id)
            except Exception as e:
                print(f"Advertencia: No se pudo eliminar la imagen de Cloudinary {imagen.url}: {e}")

        db.session.delete(product)
        db.session.commit()
        flash('¡Producto eliminado exitosamente!', 'success')
        return redirect(url_for('products_bp.list_products'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el producto: {str(e)}', 'danger')
        return redirect(url_for('products_bp.list_products'))