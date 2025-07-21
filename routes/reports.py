from flask import Blueprint, render_template, request, jsonify, make_response, abort
from flask_login import login_required
from models import db, Pedido, Producto, Cliente, PedidoProducto, Categoria 
from sqlalchemy import func, desc, asc, cast, Date, String 
from datetime import datetime, date, timedelta
import io
import csv

reports_bp = Blueprint('reports_bp', __name__, url_prefix='/reportes')

@reports_bp.route('/')
@login_required
def view_detailed_reports():
    return render_template('reportes.html')

# --- Función auxiliar para obtener datos de reportes ---
def _get_report_data_query(report_type, start_date_str, end_date_str, sort_by, granularity=None):
    """
    Construye y ejecuta la consulta SQLAlchemy basada en el tipo de reporte y filtros.
    Retorna (headers, resultados_de_consulta).
    Lanza excepción si las fechas son inválidas o el tipo de reporte no es reconocido.
    """
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59) if end_date_str else None
    except (ValueError, TypeError):
        raise ValueError("Formato de fecha inválido.")

    headers = []
    query_results = []

    if report_type == 'pedidos_detallado':
        headers = ["ID Pedido", "Fecha", "Cliente", "Producto", "Cantidad", "Precio Unit.", "Total"]
        
        query = db.session.query(
            Pedido.id.label('pedido_id'),
            Pedido.fecha_pedido.label('pedido_fecha'),
            Cliente.nombre.label('cliente_nombre'),
            Producto.nombre.label('producto_nombre'),
            PedidoProducto.cantidad.label('item_cantidad'),
            PedidoProducto.precio.label('item_precio')
        ).join(Pedido.cliente).join(Pedido.productos_en_pedido).join(Producto)

        if start_date:
            query = query.filter(Pedido.fecha_pedido >= start_date)
        if end_date:
            query = query.filter(Pedido.fecha_pedido <= end_date)

        if sort_by == 'cantidad':
            query = query.order_by(desc(PedidoProducto.cantidad))
        elif sort_by == 'total':
            query = query.order_by(desc(PedidoProducto.cantidad * PedidoProducto.precio))
        else: # 'recientes' o por defecto
            query = query.order_by(desc(Pedido.fecha_pedido))
        
        query_results = query.all()

    elif report_type == 'productos_ventas':
        headers = ["ID Producto", "Nombre", "Categoría", "Precio Actual", "Stock Actual", "Unidades Vendidas (Periodo)", "Ingresos Generados (Periodo)", "Última Venta (Periodo)"]
        
        sales_subquery = db.session.query(
            PedidoProducto.producto_id,
            func.sum(PedidoProducto.cantidad).label('total_unidades_vendidas'),
            func.sum(PedidoProducto.cantidad * PedidoProducto.precio).label('total_ingresos_generados'),
            func.max(Pedido.fecha_pedido).label('ultima_venta_periodo')
        ).join(PedidoProducto.pedido) 
        
        if start_date:
            sales_subquery = sales_subquery.filter(Pedido.fecha_pedido >= start_date)
        if end_date:
            sales_subquery = sales_subquery.filter(Pedido.fecha_pedido <= end_date)
            
        sales_subquery = sales_subquery.group_by(PedidoProducto.producto_id).subquery()


        query = db.session.query(
            Producto.id,
            Producto.nombre,
            Categoria.nombre.label('categoria_nombre'), 
            Producto.precio,
            Producto.stock,
            func.coalesce(sales_subquery.c.total_unidades_vendidas, 0).label('unidades_vendidas'),
            func.coalesce(sales_subquery.c.total_ingresos_generados, 0.0).label('ingresos_generados'),
            sales_subquery.c.ultima_venta_periodo
        ).outerjoin(Categoria, Producto.categoria_id == Categoria.id) \
         .outerjoin(sales_subquery, Producto.id == sales_subquery.c.producto_id)
        
        if sort_by == 'unidades_vendidas':
            query = query.order_by(desc('unidades_vendidas'))
        elif sort_by == 'ingresos':
            query = query.order_by(desc('ingresos_generados'))
        elif sort_by == 'stock':
            query = query.order_by(asc(Producto.stock)) 
        else: # 'nombre' por defecto
            query = query.order_by(asc(Producto.nombre))

        query_results = query.all()
    
    elif report_type == 'ventas_por_categoria':
        headers = ["Categoría", "Unidades Vendidas", "Ingresos Generados"]

        query = db.session.query(
            Categoria.nombre.label('categoria_nombre'),
            func.sum(PedidoProducto.cantidad).label('total_unidades'),
            func.sum(PedidoProducto.cantidad * PedidoProducto.precio).label('total_ingresos')
        ).join(Producto, Producto.categoria_id == Categoria.id) \
         .join(PedidoProducto, PedidoProducto.producto_id == Producto.id) \
         .join(Pedido, PedidoProducto.pedido_id == Pedido.id)
        
        if start_date:
            query = query.filter(Pedido.fecha_pedido >= start_date)
        if end_date:
            query = query.filter(Pedido.fecha_pedido <= end_date)

        query = query.group_by(Categoria.nombre)

        if sort_by == 'total_ingresos':
            query = query.order_by(desc('total_ingresos'))
        elif sort_by == 'total_unidades':
            query = query.order_by(desc('total_unidades'))
        else: # 'nombre_categoria' por defecto
            query = query.order_by(asc(Categoria.nombre))

        query_results = query.all()

    elif report_type == 'ventas_resumen':
        headers = []
        group_by_col = None
        
        # Subconsulta para obtener las categorías distintas por cada pedido dentro del rango
        # y luego agruparlas para el periodo principal
        # NOTA: GROUP_CONCAT es específico de MySQL. Para PostgreSQL usar STRING_AGG, para SQLite GROUP_CONCAT
        # Si usas otro DB, necesitarás adaptar esta línea.
        categories_subquery = db.session.query(
            PedidoProducto.pedido_id,
            func.group_concat(func.distinct(Categoria.nombre)).label('categorias_vendidas_en_pedido')
        ).join(Producto, PedidoProducto.producto_id == Producto.id) \
         .join(Categoria, Producto.categoria_id == Categoria.id) \
         .group_by(PedidoProducto.pedido_id).subquery()


        if granularity == 'day':
            headers = ["Fecha", "Ventas del Día", "Número de Productos Vendidos", "Categorías Vendidas"]
            group_by_col = func.date(Pedido.fecha_pedido) 
        elif granularity == 'week':
            headers = ["Año-Semana", "Ventas de la Semana", "Número de Productos Vendidos", "Categorías Vendidas"]
            group_by_col = func.concat(func.year(Pedido.fecha_pedido), '-', func.lpad(func.week(Pedido.fecha_pedido, 3), 2, '0')) 
        elif granularity == 'month':
            headers = ["Año-Mes", "Ventas del Mes", "Número de Productos Vendidos", "Categorías Vendidas"]
            group_by_col = func.date_format(Pedido.fecha_pedido, '%Y-%m')
        elif granularity == 'year':
            headers = ["Año", "Ventas del Año", "Número de Productos Vendidos", "Categorías Vendidas"]
            group_by_col = func.year(Pedido.fecha_pedido)
        else:
            raise ValueError("Granularidad de reporte de ventas no válida.")

        query = db.session.query(
            group_by_col.label('period_label'),
            func.sum(Pedido.total).label('total_ventas_periodo'),
            func.sum(PedidoProducto.cantidad).label('total_productos_vendidos'), # Suma de cantidad de productos vendidos
            # Concatena todas las categorías distintas vendidas en ese período
            func.group_concat(func.distinct(Categoria.nombre)).label('categorias_periodo')
        ).join(Pedido.productos_en_pedido).join(Producto).join(Categoria) # Uniones necesarias para acceder a PedidoProducto y Categoria

        if start_date:
            query = query.filter(Pedido.fecha_pedido >= start_date)
        if end_date:
            query = query.filter(Pedido.fecha_pedido <= end_date)

        query = query.group_by(group_by_col) # Agrupar por el período

        if sort_by == 'recientes':
            query = query.order_by(desc('period_label')) 
        elif sort_by == 'total':
            query = query.order_by(desc('total_ventas_periodo'))
        elif sort_by == 'cantidad': # Ahora representa "Número de Productos Vendidos"
            query = query.order_by(desc('total_productos_vendidos')) 
        else: # Por defecto, ordenar por el período (ascendente)
            query = query.order_by(asc('period_label')) 

        query_results = query.all()
    
    else:
        abort(400, description="Tipo de reporte no válido")
    
    return headers, query_results

# --- Ruta API para obtener los datos de los reportes (JSON) ---
@reports_bp.route('/api/reports/data', methods=['GET'])
@login_required
def get_report_data():
    report_type = request.args.get('type', 'pedidos_detallado')
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    sort_by = request.args.get('sort_by', 'recientes')
    granularity = request.args.get('granularity', 'day') # Obtener granularidad para ventas_resumen

    try:
        headers, raw_data = _get_report_data_query(report_type, start_date_str, end_date_str, sort_by, granularity)
    except ValueError as ve:
        return jsonify({'message': f'Error en el formato de fecha: {str(ve)}'}), 400
    except Exception as e:
        print(f"Error al construir la consulta del reporte: {e}") 
        return jsonify({'message': f'Ocurrió un error en el servidor al cargar los reportes: {str(e)}'}), 500

    formatted_rows = []
    
    if report_type == 'pedidos_detallado':
        for item in raw_data:
            formatted_rows.append([
                item.pedido_id,
                item.pedido_fecha.strftime('%Y-%m-%d %H:%M'),
                item.cliente_nombre,
                item.producto_nombre,
                item.item_cantidad,
                f"S/ {float(item.item_precio):.2f}",
                f"S/ {float(item.item_cantidad * item.item_precio):.2f}"
            ])
    elif report_type == 'productos_ventas':
        for product in raw_data:
            formatted_rows.append([
                product.id,
                product.nombre,
                product.categoria_nombre if product.categoria_nombre else 'N/A',
                f"S/ {float(product.precio):.2f}",
                product.stock,
                product.unidades_vendidas,
                f"S/ {float(product.ingresos_generados):.2f}",
                product.ultima_venta_periodo.strftime('%Y-%m-%d %H:%M') if product.ultima_venta_periodo else 'N/A'
            ])
    elif report_type == 'ventas_por_categoria':
        for category_summary in raw_data:
            formatted_rows.append([
                category_summary.categoria_nombre if category_summary.categoria_nombre else 'Sin Categoría',
                category_summary.total_unidades,
                f"S/ {float(category_summary.total_ingresos):.2f}"
            ])
    elif report_type == 'ventas_resumen':
        for period_summary in raw_data:
            period_label = str(period_summary.period_label)
            
            formatted_rows.append([
                period_label,
                f"S/ {float(period_summary.total_ventas_periodo):.2f}",
                period_summary.total_productos_vendidos, # Ahora es el total de productos vendidos
                period_summary.categorias_periodo if period_summary.categorias_periodo else 'N/A' # Lista de categorías
            ])
    
    return jsonify({'headers': headers, 'rows': formatted_rows})

# --- Ruta API para descargar el reporte como CSV ---
@reports_bp.route('/api/reports/download', methods=['GET'])
@login_required
def download_report_csv():
    report_type = request.args.get('type', 'pedidos_detallado')
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    sort_by = request.args.get('sort_by', 'recientes')
    granularity = request.args.get('granularity', 'day')

    try:
        headers, raw_data = _get_report_data_query(report_type, start_date_str, end_date_str, sort_by, granularity)
    except ValueError as ve:
        return f"Error en el formato de fecha: {str(ve)}", 400
    except Exception as e:
        print(f"Error al construir la consulta del reporte para descarga: {e}")
        return "Error al generar el reporte CSV.", 500

    si = io.StringIO()
    cw = csv.writer(si)
    
    cw.writerow(headers) # Escribir encabezados

    # Formatear filas para CSV
    if report_type == 'pedidos_detallado':
        for item in raw_data:
            total = float(item.item_cantidad * item.item_precio)
            cw.writerow([
                item.pedido_id,
                item.pedido_fecha.strftime('%Y-%m-%d %H:%M'),
                item.cliente_nombre,
                item.producto_nombre,
                item.item_cantidad,
                f"{float(item.item_precio):.2f}".replace('.', ','), 
                f"{total:.2f}".replace('.', ',')
            ])
    elif report_type == 'productos_ventas':
        for product in raw_data:
            cw.writerow([
                product.id,
                product.nombre,
                product.categoria_nombre if product.categoria_nombre else 'N/A',
                f"{float(product.precio):.2f}".replace('.', ','),
                product.stock,
                product.unidades_vendidas,
                f"{float(product.ingresos_generados):.2f}".replace('.', ','),
                product.ultima_venta_periodo.strftime('%Y-%m-%d %H:%M') if product.ultima_venta_periodo else 'N/A'
            ])
    elif report_type == 'ventas_por_categoria':
        for category_summary in raw_data:
            cw.writerow([
                category_summary.categoria_nombre if category_summary.categoria_nombre else 'Sin Categoría',
                category_summary.total_unidades,
                f"{float(category_summary.total_ingresos):.2f}".replace('.', ',')
            ])
    elif report_type == 'ventas_resumen':
        for period_summary in raw_data:
            period_label = str(period_summary.period_label)
            
            cw.writerow([
                period_label,
                f"{float(period_summary.total_ventas_periodo):.2f}".replace('.', ','),
                period_summary.total_productos_vendidos, # Ahora es el total de productos vendidos
                period_summary.categorias_periodo if period_summary.categorias_periodo else 'N/A' # Lista de categorías
            ])
    
    output = si.getvalue()
    
    response = make_response(output)
    response.headers["Content-Disposition"] = f"attachment; filename=reporte_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response.headers["Content-type"] = "text/csv; charset=utf-8"
    
    return response