# TIENDA/routes/clients.py

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user # Asegúrate de tener Flask-Login configurado
from models import Cliente, db # Asegúrate de que tu modelo Cliente y tu instancia db están correctamente definidos en models.py
from datetime import datetime 

# Crea un Blueprint para las rutas de clientes
clients_bp = Blueprint('clients_bp', __name__, url_prefix='/clientes')

# Ruta para listar clientes y renderizar la plantilla HTML
@clients_bp.route('/')
@login_required # Requiere que el usuario esté logueado
def list_clients():
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes, current_user=current_user)

# API: Ruta para crear un nuevo cliente (recibe JSON del frontend)
@clients_bp.route('/nuevo', methods=['POST'])
@login_required
def create_client():
    if not request.is_json:
        return jsonify({'error': 'La solicitud debe ser JSON.'}), 400

    data = request.get_json()
    nombre = data.get('nombre')
    email = data.get('email')
    direccion = data.get('direccion')
    telefono = data.get('telefono')
    
    if not nombre or not email:
        return jsonify({'error': 'Nombre y Email son campos requeridos.'}), 400

    try:
        nuevo_cliente = Cliente(
            nombre=nombre,
            email=email,
            direccion=direccion,
            telefono=telefono,
            fecha_registro=datetime.now() # O usa db.Column(db.DateTime, default=datetime.utcnow) en tu modelo
        )
        db.session.add(nuevo_cliente)
        db.session.commit()
        return jsonify({'message': 'Cliente creado exitosamente!', 'client_id': nuevo_cliente.id}), 201
    except Exception as e:
        db.session.rollback()
        error_message = f'Error al crear el cliente: {str(e)}'
        print(f"Error de base de datos: {error_message}") # Para depuración en el servidor
        return jsonify({'error': error_message}), 500

# API: Ruta para obtener los detalles de un cliente específico (para los modales Ver/Editar)
@clients_bp.route('/api/<int:client_id>', methods=['GET'])
@login_required
def get_client_json(client_id):
    cliente = Cliente.query.get(client_id)
    if not cliente:
        return jsonify({'error': 'Cliente no encontrado.'}), 404
    
    # Formatea la fecha para JavaScript
    fecha_registro_iso = cliente.fecha_registro.isoformat() if cliente.fecha_registro else None

    client_data = {
        'id': cliente.id,
        'nombre': cliente.nombre,
        'email': cliente.email,
        'telefono': cliente.telefono,
        'direccion': cliente.direccion,
        'fecha_registro': fecha_registro_iso
    }
    return jsonify(client_data)

# API: Ruta para obtener todos los clientes (para recargar la tabla)
@clients_bp.route('/api/all', methods=['GET'])
@login_required
def get_all_clients_json():
    clientes = Cliente.query.all()
    clients_data = []
    for cliente in clientes:
        clients_data.append({
            'id': cliente.id,
            'nombre': cliente.nombre,
            'email': cliente.email,
            'telefono': cliente.telefono,
            'direccion': cliente.direccion,
            'fecha_registro': cliente.fecha_registro.isoformat() # Asegura formato ISO para JS
        })
    return jsonify(clients_data)

# API: Ruta para editar un cliente existente (recibe JSON del frontend)
@clients_bp.route('/editar/<int:client_id>', methods=['PUT'])
@login_required
def edit_client(client_id):
    cliente = Cliente.query.get(client_id)
    if not cliente:
        return jsonify({'error': 'Cliente no encontrado.'}), 404

    if not request.is_json:
        return jsonify({'error': 'La solicitud debe ser JSON.'}), 400

    data = request.get_json()
    nombre = data.get('nombre')
    email = data.get('email')
    direccion = data.get('direccion')
    telefono = data.get('telefono')

    if not nombre or not email:
        return jsonify({'error': 'Nombre y Email son campos requeridos.'}), 400

    try:
        cliente.nombre = nombre
        cliente.email = email
        cliente.direccion = direccion
        cliente.telefono = telefono

        db.session.commit()
        return jsonify({'message': 'Cliente actualizado exitosamente!'}), 200
    except Exception as e:
        db.session.rollback()
        error_message = f'Error al actualizar el cliente: {str(e)}'
        print(f"Error de base de datos: {error_message}") # Para depuración
        return jsonify({'error': error_message}), 500

# API: Ruta para eliminar un cliente (recibe solicitud DELETE del frontend)
@clients_bp.route('/eliminar/<int:client_id>', methods=['DELETE'])
@login_required
def delete_client(client_id):
    cliente = Cliente.query.get(client_id)
    if not cliente:
        return jsonify({'error': 'Cliente no encontrado.'}), 404
    
    try:
        db.session.delete(cliente)
        db.session.commit()
        return jsonify({'message': 'Cliente eliminado exitosamente!'}), 200
    except Exception as e:
        db.session.rollback()
        error_message = f'Error al eliminar el cliente: {str(e)}'
        print(f"Error de base de datos: {error_message}") # Para depuración
        return jsonify({'error': error_message}), 500