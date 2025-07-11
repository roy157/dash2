# dash2/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import Usuario, db # Importa el modelo Usuario para login

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index')) # Si ya está logueado, redirige al dashboard

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password') # En una app real, aquí se verificaría el hash de la contraseña

        # Ejemplo muy simple (¡NO USAR EN PRODUCCIÓN! Usa contraseñas hasheadas y bcrypt)
        user = Usuario.query.filter_by(email=email).first()
        if user and user.password == password: # Esto es solo para pruebas
            login_user(user)
            flash('Inicio de sesión exitoso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Email o contraseña incorrectos.', 'danger')

    return render_template('auth/login.html') # Asume que tienes una plantilla en templates/auth/login.html
                                             # Si está en templates/login.html, cambia a 'login.html'

@auth_bp.route('/logout')
@login_required # Requiere que el usuario esté logueado para acceder
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('auth.login'))