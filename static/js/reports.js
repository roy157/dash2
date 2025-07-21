// static/js/reports.js

document.addEventListener('DOMContentLoaded', function() {
    const reportTypeSelect = document.getElementById('report-type');
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    const sortBySelect = document.getElementById('sort-by');
    const filterBtn = document.getElementById('filter-btn');
    const downloadBtn = document.getElementById('download-btn');
    const reportTableHead = document.getElementById('report-table-head');
    const reportTableBody = document.getElementById('report-table-body');
    const loadingSpinner = document.getElementById('loading-spinner');
    const noDataMessage = document.getElementById('no-data-message');
    const granularityFilterDiv = document.getElementById('granularity-filter');
    const periodGranularitySelect = document.getElementById('period-granularity');


    // Función para actualizar las opciones del selector de "Ordenar por"
    function updateSortByOptions(reportType) {
        let optionsHtml = '';
        if (reportType === 'pedidos_detallado') {
            optionsHtml = `
                <option value="recientes" selected>Más Recientes</option>
                <option value="cantidad">Mayor Cantidad (Producto)</option>
                <option value="total">Mayor Total (Producto)</option>
            `;
        } else if (reportType === 'productos_ventas') {
             optionsHtml = `
                <option value="nombre" selected>Nombre (A-Z)</option>
                <option value="unidades_vendidas">Unidades Vendidas</option>
                <option value="ingresos">Ingresos Generados</option>
                <option value="stock">Stock Actual</option>
            `;
        } else if (reportType === 'ventas_por_categoria') {
            optionsHtml = `
                <option value="total_ingresos" selected>Mayor Ingresos</option>
                <option value="total_unidades">Mayor Unidades Vendidas</option>
                <option value="nombre_categoria">Categoría (A-Z)</option>
            `;
        } else if (reportType === 'ventas_resumen') {
            optionsHtml = `
                <option value="recientes" selected>Más Recientes (Periodo)</option>
                <option value="total">Mayor Venta (Periodo)</option>
                <option value="cantidad">Mayor Cantidad de Ventas (Periodo)</option>
            `;
        }
        sortBySelect.innerHTML = optionsHtml;
    }

    // Función para mostrar/ocultar filtros de granularidad
    function toggleGranularityFilter() {
        const selectedType = reportTypeSelect.value;
        if (selectedType === 'ventas_resumen') {
            granularityFilterDiv.style.display = 'flex'; // Usar flex para mantener el layout
        } else {
            granularityFilterDiv.style.display = 'none';
        }
    }

    // Función para obtener y mostrar los datos del reporte
    async function fetchAndRenderReport() {
        loadingSpinner.style.display = 'block';
        noDataMessage.style.display = 'none';
        reportTableBody.innerHTML = ''; // Limpiar cuerpo de la tabla
        reportTableHead.innerHTML = ''; // Limpiar encabezado de la tabla

        const reportType = reportTypeSelect.value;
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        const sortBy = sortBySelect.value;
        const periodGranularity = periodGranularitySelect.value; // Obtener granularidad

        // Construir la URL de la API para obtener datos
        let apiUrl = `/reportes/api/reports/data?type=${reportType}&start_date=${startDate}&end_date=${endDate}&sort_by=${sortBy}`;
        if (reportType === 'ventas_resumen') {
            apiUrl += `&granularity=${periodGranularity}`; // Añadir granularidad si es un reporte de resumen
        }

        try {
            const response = await fetch(apiUrl);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Error al cargar los reportes.');
            }
            const data = await response.json();

            loadingSpinner.style.display = 'none';

            if (data.headers && data.rows && data.rows.length > 0) {
                renderTable(data.headers, data.rows);
                noDataMessage.style.display = 'none';
            } else {
                noDataMessage.textContent = 'No se encontraron datos para los filtros seleccionados.';
                noDataMessage.style.display = 'block';
            }

        } catch (error) {
            loadingSpinner.style.display = 'none';
            noDataMessage.textContent = `Error al cargar reportes: ${error.message}`;
            noDataMessage.style.display = 'block';
            console.error('Error fetching report data:', error);
        }
    }

    // Función para renderizar la tabla dinámicamente
    function renderTable(headers, rows) {
        // Renderizar encabezados
        const headerRow = document.createElement('tr');
        headers.forEach(headerText => {
            const th = document.createElement('th');
            th.textContent = headerText;
            headerRow.appendChild(th);
        });
        reportTableHead.appendChild(headerRow);

        // Renderizar filas
        rows.forEach(rowData => {
            const row = document.createElement('tr');
            rowData.forEach(cellData => {
                const td = document.createElement('td');
                td.textContent = cellData;
                row.appendChild(td);
            });
            reportTableBody.appendChild(row);
        });
    }

    // Función para manejar la descarga del CSV
    function downloadCSV() {
        const reportType = reportTypeSelect.value;
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        const sortBy = sortBySelect.value;
        const periodGranularity = periodGranularitySelect.value; // Obtener granularidad

        // Construir la URL de la API para descargar CSV
        let downloadUrl = `/reportes/api/reports/download?type=${reportType}&start_date=${startDate}&end_date=${endDate}&sort_by=${sortBy}`;
        if (reportType === 'ventas_resumen') {
            downloadUrl += `&granularity=${periodGranularity}`; // Añadir granularidad si es un reporte de resumen
        }
        
        window.location.href = downloadUrl; // Esto iniciará la descarga
    }

    // Event Listeners
    filterBtn.addEventListener('click', fetchAndRenderReport);
    downloadBtn.addEventListener('click', downloadCSV);

    // Cuando cambia el tipo de reporte: actualiza opciones de ordenar, muestra/oculta granularidad y recarga el reporte
    reportTypeSelect.addEventListener('change', function() {
        updateSortByOptions(this.value);
        toggleGranularityFilter();
        fetchAndRenderReport();
    });

    // Cuando cambia la granularidad, recarga el reporte (solo relevante para ventas_resumen)
    periodGranularitySelect.addEventListener('change', fetchAndRenderReport);

    // Cargar reporte al inicio de la página
    // Inicializar las opciones de ordenar y visibilidad del filtro de granularidad
    updateSortByOptions(reportTypeSelect.value);
    toggleGranularityFilter();
    fetchAndRenderReport();
});