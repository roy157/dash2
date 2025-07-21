# dash2/routes/main.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

main_bp = Blueprint('main_bp', __name__)

# Elimina esta sección si tu index está en app.py, o cámbiala por otra ruta si la necesitas
# @main_bp.route('/')
# def dashboard():
#     return render_template('index.html')

# Ejemplo de otra ruta para main_bp si lo quieres usar
@main_bp.route('/acerca-de')
def about():
    return render_template('about.html')

# @main_bp.route('/configuracion')
# @login_required
# def settings_page():
#     flash('La página de configuración aún no está implementada.', 'info')
#     # Redirige al dashboard
#     return redirect(url_for('index'))
    # O podrías redirigir a una página de "Acerca de" si la tienes
    # return redirect(url_for('main_bp.about'))