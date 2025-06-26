document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
});

async function loadDashboardData() {
    try {
        // Cargar estadísticas
        const statsResponse = await fetch('/api/dashboard/summary');
        const stats = await statsResponse.json();
        
        document.getElementById('total-ventas').textContent = `$${stats.total_ventas.toLocaleString()}`;
        document.getElementById('ventas-mes').textContent = `$${stats.ventas_mes.toLocaleString()}`;
        document.getElementById('total-productos').textContent = stats.total_productos;
        document.getElementById('total-clientes').textContent = stats.total_clientes;
        document.getElementById('bajo-stock').textContent = stats.productos_bajo_stock;
        
        // Cargar ventas recientes
        const salesResponse = await fetch('/api/dashboard/recent-sales');
        const sales = await salesResponse.json();
        
        const salesTable = document.getElementById('recent-sales');
        salesTable.innerHTML = sales.map(sale => `
            <tr>
                <td>#${sale.id}</td>
                <td>${sale.cliente}</td>
                <td>$${sale.total.toFixed(2)}</td>
                <td>${sale.fecha}</td>
                <td><span class="status completed">${sale.estado}</span></td>
            </tr>
        `).join('');
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}