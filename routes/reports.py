# TIENDA/routes/reports.py

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, Pedido, Producto, Cliente, VentaProducto, Categoria # Importa los modelos necesarios
from sqlalchemy import func, extract
from datetime import datetime, date, timedelta

reports_bp = Blueprint('reports_bp', __name__, url_prefix='/reportes')

# Ruta principal para generar reportes
@reports_bp.route('/')
@login_required
def generate_report(): # <--- Asegúrate de que esta función se llame 'generate_report'
    # Lógica para obtener datos para los reportes
    # Puedes pasar datos iniciales o permitir que el JS los cargue dinámicamente

    # Ejemplo: Ventas por mes (últimos 6 meses)
    monthly_sales = []
    today = date.today()
    for i in range(6):
        month_ago = today - timedelta(days=30 * i) # Aproximación de un mes
        start_of_month = date(month_ago.year, month_ago.month, 1)
        end_of_month = (start_of_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        total_sales_month = db.session.query(func.sum(Pedido.total)).filter(
            Pedido.fecha_pedido >= start_of_month,
            Pedido.fecha_pedido <= end_of_month,
            (Pedido.estado == 'enviado') | (Pedido.estado == 'entregado')
        ).scalar()
        
        monthly_sales.append({
            'month': start_of_month.strftime('%Y-%m'),
            'total': float(total_sales_month) if total_sales_month is not None else 0.00
        })
    monthly_sales.reverse() # Para que el mes más antiguo esté primero

    # Ejemplo: Productos más vendidos (puedes ajustar la lógica si VentaProducto no tiene fecha_venta)
    top_products_query = db.session.query(
        Producto.nombre,
        func.sum(VentaProducto.cantidad).label('total_vendido')
    ).join(VentaProducto, Producto.id == VentaProducto.producto_id)\
     .group_by(Producto.nombre)\
     .order_by(func.sum(VentaProducto.cantidad).desc())\
     .limit(5).all()

    top_products = []
    for p_name, total_sold in top_products_query:
        top_products.append({
            'nombre': p_name,
            'total_vendido': int(total_sold) if total_sold is not None else 0
        })

    return render_template('reports/reports.html',
                           monthly_sales=monthly_sales,
                           top_products=top_products)

# --- Rutas API para datos de reportes (si necesitas cargar dinámicamente con JS) ---

@reports_bp.route('/api/sales_by_month', methods=['GET'])
@login_required
def api_sales_by_month():
    # Esta ruta podría tomar parámetros de fecha si quieres un rango específico
    monthly_sales = []
    today = date.today()
    for i in range(6): # Últimos 6 meses
        month_ago = today - timedelta(days=30 * i)
        start_of_month = date(month_ago.year, month_ago.month, 1)
        end_of_month = (start_of_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        total_sales_month = db.session.query(func.sum(Pedido.total)).filter(
            Pedido.fecha_pedido >= start_of_month,
            Pedido.fecha_pedido <= end_of_month,
            (Pedido.estado == 'enviado') | (Pedido.estado == 'entregado')
        ).scalar()
        
        monthly_sales.append({
            'month': start_of_month.strftime('%Y-%m'),
            'total': float(total_sales_month) if total_sales_month is not None else 0.00
        })
    monthly_sales.reverse()
    return jsonify(monthly_sales)

@reports_bp.route('/api/top_products', methods=['GET'])
@login_required
def api_top_products():
    top_products_query = db.session.query(
        Producto.nombre,
        func.sum(VentaProducto.cantidad).label('total_vendido')
    ).join(VentaProducto, Producto.id == VentaProducto.producto_id)\
     .group_by(Producto.nombre)\
     .order_by(func.sum(VentaProducto.cantidad).desc())\
     .limit(5).all()

    top_products = []
    for p_name, total_sold in top_products_query:
        top_products.append({
            'nombre': p_name,
            'total_vendido': int(total_sold) if total_sold is not None else 0
        })
    return jsonify(top_products)

