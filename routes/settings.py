from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, Usuario 

settings_bp = Blueprint('settings', __name__, url_prefix='/configuracion')

# --- RUTA PRINCIPAL (DATOS PERSONALES + PANEL DE ADMIN) ---
@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        # Actualiza el email del usuario actual
        email = request.form.get('email')
        user_exists = db.session.query(db.exists().where(db.and_(Usuario.email == email, Usuario.id != current_user.id))).scalar()

        if user_exists:
            flash('El email ya está en uso por otro usuario.', 'danger')
        else:
            current_user.email = email
            db.session.commit()
            flash('Tus datos han sido actualizados con éxito.', 'success')
        return redirect(url_for('settings.index'))
    
    # Pasamos todos los usuarios a la plantilla (el HTML decidirá si mostrarlos)
    all_users = Usuario.query.all()
    return render_template('configuracion.html', users=all_users)

@settings_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    # Cambia la contraseña del usuario actual
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')

    if not current_user.check_password(current_password):
        flash('La contraseña actual es incorrecta.', 'danger')
        return redirect(url_for('settings.index'))

    current_user.set_password(new_password)
    db.session.commit()
    flash('Tu contraseña ha sido actualizada con éxito.', 'success')
    return redirect(url_for('settings.index'))


# --- API PARA GESTIÓN DE USUARIOS (SOLO ADMIN) ---
def admin_required():
    if current_user.role != 'Administrador':
        return jsonify({'message': 'Acceso no autorizado'}), 403

@settings_bp.route('/api/usuario/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    if current_user.role != 'Administrador': return admin_required()
    user = Usuario.query.get_or_404(user_id)
    return jsonify({'email': user.email, 'role': user.role})

@settings_bp.route('/api/usuario', methods=['POST'])
@login_required
def create_user():
    if current_user.role != 'Administrador': return admin_required()
    data = request.json
    if not all(k in data for k in ['email', 'password', 'role']):
        return jsonify({'message': 'Faltan datos'}), 400
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'El email ya está registrado'}), 409
    
    new_user = Usuario(email=data['email'], role=data['role'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Usuario creado con éxito'}), 201

@settings_bp.route('/api/usuario/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    if current_user.role != 'Administrador': return admin_required()
    user = Usuario.query.get_or_404(user_id)
    data = request.json
    
    if data.get('email') != user.email and Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'El email ya está en uso'}), 409
        
    user.email = data.get('email', user.email)
    user.role = data.get('role', user.role)
    if data.get('password'):
        user.set_password(data['password'])
    db.session.commit()
    return jsonify({'message': 'Usuario actualizado con éxito'})

@settings_bp.route('/api/usuario/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if current_user.role != 'Administrador': return admin_required()
    user = Usuario.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Usuario eliminado con éxito'})