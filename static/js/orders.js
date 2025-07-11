// TIENDA/static/js/orders.js

document.addEventListener('DOMContentLoaded', function() {

    // --- Funciones para Modales (reutilizables) ---
    function openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex'; // Usar flex para centrar
        }
    }

    function closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
        }
    }

    // Cerrar modales al hacer clic en la 'x'
    document.querySelectorAll('.close-modal').forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                closeModal(modal.id);
            }
        });
    });

    // Cerrar modales al hacer clic fuera del contenido del modal
    window.addEventListener('click', function(event) {
        const viewModal = document.getElementById('view-order-modal');
        const editModal = document.getElementById('edit-order-modal');

        if (viewModal && event.target === viewModal) {
            closeModal('view-order-modal');
        }
        if (editModal && event.target === editModal) {
            closeModal('edit-order-modal');
        }
    });

    // --- Lógica para "Ver Detalle" del Pedido (Modal) ---
    document.querySelectorAll('.view-order-btn').forEach(button => {
        button.addEventListener('click', async function() {
            const orderId = this.dataset.orderId;
            console.log(`Ver detalle del pedido ID: ${orderId}`);

            try {
                const response = await fetch(`/pedidos/${orderId}/json`);
                if (!response.ok) {
                    throw new Error(`Error al cargar los detalles del pedido: ${response.statusText}`);
                }
                const data = await response.json();

                // Rellenar el modal de ver detalle
                document.getElementById('modal-order-id').textContent = data.order.id;
                document.getElementById('modal-client-name').textContent = data.client.nombre;
                document.getElementById('modal-client-email').textContent = data.client.email;
                document.getElementById('modal-client-phone').textContent = data.client.telefono;
                document.getElementById('modal-order-date').textContent = new Date(data.order.fecha_pedido).toLocaleString();
                document.getElementById('modal-shipping-address').textContent = data.order.direccion_envio;
                document.getElementById('modal-order-total').textContent = parseFloat(data.order.total).toFixed(2);
                
                const statusBadge = document.getElementById('modal-order-status');
                statusBadge.textContent = data.order.estado;
                statusBadge.className = `status-badge status-${data.order.estado.toLowerCase()}`; // Actualiza la clase CSS

                // Llenar la tabla de productos del pedido
                const productsListBody = document.getElementById('modal-products-list');
                productsListBody.innerHTML = ''; // Limpiar contenido previo
                data.products.forEach(product => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${product.name}</td>
                        <td>${product.quantity}</td>
                        <td>$${parseFloat(product.unit_price).toFixed(2)}</td>
                        <td>$${parseFloat(product.subtotal).toFixed(2)}</td>
                    `;
                    productsListBody.appendChild(row);
                });

                openModal('view-order-modal');

            } catch (error) {
                console.error('Error al obtener detalles del pedido:', error);
                alert('No se pudieron cargar los detalles del pedido. Inténtalo de nuevo.');
            }
        });
    });

    // --- Lógica para "Editar Pedido" (Modal) ---
    document.querySelectorAll('.edit-order-btn').forEach(button => {
        button.addEventListener('click', async function() {
            const orderId = this.dataset.orderId;
            console.log(`Editar pedido ID: ${orderId}`);

            try {
                const response = await fetch(`/pedidos/${orderId}/json`);
                if (!response.ok) {
                    throw new Error(`Error al cargar los datos del pedido para editar: ${response.statusText}`);
                }
                const data = await response.json();

                // Rellenar el modal de edición
                document.getElementById('edit-modal-order-id').textContent = data.order.id;
                document.getElementById('edit-order-hidden-id').value = data.order.id;
                document.getElementById('edit-order-original-status').value = data.order.estado; // Guardar estado original

                // Cargar clientes en el select
                const clientSelect = document.getElementById('edit-client-select');
                clientSelect.innerHTML = ''; // Limpiar opciones previas
                // Aquí deberías hacer una llamada AJAX para obtener todos los clientes
                // O si ya los tienes disponibles en una variable global (menos ideal)
                // Por simplicidad, vamos a asumir que tienes una forma de obtenerlos o los pasas desde el backend
                // Por ahora, solo añadiremos el cliente actual. Idealmente, cargarías todos los clientes.
                
                // Ejemplo de cómo cargar todos los clientes (requiere una ruta API de clientes)
                const clientsResponse = await fetch('/clientes/api/all'); // Asume esta ruta existe
                if (clientsResponse.ok) {
                    const clientsData = await clientsResponse.json();
                    clientsData.forEach(client => {
                        const option = document.createElement('option');
                        option.value = client.id;
                        option.textContent = client.nombre;
                        clientSelect.appendChild(option);
                    });
                } else {
                    console.warn('No se pudieron cargar todos los clientes para el select de edición.');
                    // Si no se pueden cargar todos, al menos añade el cliente actual
                    const option = document.createElement('option');
                    option.value = data.client.id;
                    option.textContent = data.client.nombre;
                    clientSelect.appendChild(option);
                }
                clientSelect.value = data.order.cliente_id; // Seleccionar el cliente del pedido

                document.getElementById('edit-shipping-address').value = data.order.direccion_envio;
                document.getElementById('edit-order-status').value = data.order.estado;

                openModal('edit-order-modal');

            } catch (error) {
                console.error('Error al obtener datos para edición:', error);
                alert('No se pudieron cargar los datos del pedido para editar. Inténtalo de nuevo.');
            }
        });
    });

    // --- Manejo del envío del formulario de edición (con AJAX) ---
    const editOrderForm = document.getElementById('edit-order-form');
    if (editOrderForm) {
        editOrderForm.addEventListener('submit', async function(event) {
            event.preventDefault();

            const orderId = document.getElementById('edit-order-hidden-id').value;
            const formData = new FormData(this);

            try {
                const response = await fetch(`/pedidos/editar/${orderId}`, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest' // Indicar que es una petición AJAX
                    }
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || 'Error desconocido al actualizar.');
                }

                const data = await response.json();
                if (data.success) {
                    alert('Pedido actualizado exitosamente!');
                    closeModal('edit-order-modal');
                    window.location.reload(); // Recargar la página para ver los cambios
                } else {
                    alert('Error: ' + (data.message || 'No se pudo actualizar el pedido.'));
                }
            } catch (error) {
                console.error('Error al enviar el formulario de edición:', error);
                alert('Hubo un error al guardar los cambios: ' + error.message);
            }
        });
    }

    // --- Lógica para búsqueda y filtrado de la tabla ---
    const orderSearchInput = document.getElementById('orderSearchInput');
    const orderStatusFilter = document.getElementById('orderStatusFilter');
    const orderDateFilter = document.getElementById('orderDateFilter');
    const ordersTableBody = document.querySelector('#orders-table tbody');
    const noOrdersMessage = document.getElementById('no-orders-message');
    const noFilteredOrdersMessage = document.getElementById('no-filtered-orders');

    function filterOrders() {
        if (!ordersTableBody) return;

        const searchTerm = orderSearchInput.value.toLowerCase();
        const selectedStatus = orderStatusFilter.value.toLowerCase();
        const selectedDate = orderDateFilter.value; // Formato YYYY-MM-DD

        let anyRowVisible = false;
        const allRows = ordersTableBody.querySelectorAll('.order-row');

        allRows.forEach(row => {
            const orderId = row.cells[0].textContent.toLowerCase();
            const clientName = row.cells[1].textContent.toLowerCase();
            const orderStatus = row.dataset.status.toLowerCase(); // Usar data-status
            const orderDate = row.dataset.date; // Usar data-date

            const matchesSearch = orderId.includes(searchTerm) || clientName.includes(searchTerm);
            const matchesStatus = selectedStatus === '' || orderStatus === selectedStatus;
            const matchesDate = selectedDate === '' || orderDate === selectedDate;

            if (matchesSearch && matchesStatus && matchesDate) {
                row.style.display = '';
                anyRowVisible = true;
            } else {
                row.style.display = 'none';
            }
        });

        if (noOrdersMessage) {
            noOrdersMessage.style.display = allRows.length === 0 ? 'block' : 'none';
        }
        if (noFilteredOrdersMessage) {
            noFilteredOrdersMessage.style.display = anyRowVisible ? 'none' : 'block';
        }
    }

    // Asignar listeners a los elementos de filtro
    if (orderSearchInput) orderSearchInput.addEventListener('keyup', filterOrders);
    if (orderStatusFilter) orderStatusFilter.addEventListener('change', filterOrders);
    if (orderDateFilter) orderDateFilter.addEventListener('change', filterOrders);

    // Ejecutar el filtro inicial al cargar la página
    filterOrders();

    // --- Lógica para el botón de exportar (ejemplo básico) ---
    const exportBtn = document.querySelector('.export-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            alert('Funcionalidad de exportar aún no implementada. Puedes implementarla para exportar a CSV/Excel.');
            // Aquí podrías añadir lógica para generar un CSV o PDF
            // Por ejemplo, hacer una llamada AJAX a una ruta Flask que genere el archivo
            // window.location.href = '/pedidos/exportar?status=' + orderStatusFilter.value + '&search=' + orderSearchInput.value;
        });
    }
});
