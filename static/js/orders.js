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
                
                // Fetch all clients for the dropdown
                const clientsResponse = await fetch('/clientes/api/all'); // Assumes this route exists and returns all clients
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
                    // Fallback: if clients cannot be loaded, at least add the current client
                    const option = document.createElement('option');
                    option.value = data.client.id;
                    option.textContent = data.client.nombre;
                    clientSelect.appendChild(option);
                }
                clientSelect.value = data.order.cliente_id; // Select the order's client

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

    // --- Lógica para búsqueda y filtrado de la tabla (MODIFIED) ---
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
        const selectedDate = orderDateFilter.value; // Format YYYY-MM-DD

        let anyRowVisible = false;
        const allRows = ordersTableBody.querySelectorAll('.order-row');

        allRows.forEach(row => {
            // Get all relevant text content from the row for searching
            const orderId = row.cells[0].textContent.toLowerCase();
            const clientName = row.cells[1].textContent.toLowerCase();
            const shippingAddress = row.cells[2].textContent.toLowerCase();
            const total = row.cells[3].textContent.toLowerCase(); // Includes "S/"
            const orderDateDisplay = row.cells[4].textContent.toLowerCase(); // Displayed date and time
            const orderStatus = row.dataset.status.toLowerCase(); // Use data-status

            // Construct a single string with all searchable content for the row
            const rowContent = `${orderId} ${clientName} ${shippingAddress} ${total} ${orderDateDisplay} ${orderStatus}`;

            const matchesSearch = searchTerm === '' || rowContent.includes(searchTerm);
            const matchesStatus = selectedStatus === '' || orderStatus === selectedStatus;
            const matchesDate = selectedDate === '' || row.dataset.date === selectedDate; // Use data-date for exact date filter

            if (matchesSearch && matchesStatus && matchesDate) {
                row.style.display = '';
                anyRowVisible = true;
            } else {
                row.style.display = 'none';
            }
        });

        if (noOrdersMessage) {
            // If there are no orders at all (table body is empty or only header)
            noOrdersMessage.style.display = allRows.length === 0 ? 'block' : 'none';
        }
        if (noFilteredOrdersMessage) {
            // If there are orders, but none match the current filters
            noFilteredOrdersMessage.style.display = anyRowVisible ? 'none' : 'block';
        }
    }

    // Assign listeners to filter elements
    if (orderSearchInput) orderSearchInput.addEventListener('keyup', filterOrders);
    if (orderStatusFilter) orderStatusFilter.addEventListener('change', filterOrders);
    if (orderDateFilter) orderDateFilter.addEventListener('change', filterOrders);

    // Execute initial filter on page load
    filterOrders();

    // --- Lógica para el botón de exportar (ejemplo básico) ---
    const exportBtn = document.querySelector('.export-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            alert('Funcionalidad de exportar aún no implementada. Puedes implementarla para exportar a CSV/Excel.');
            // Here you could add logic to generate a CSV or PDF
            // For example, make an AJAX call to a Flask route that generates the file
            // window.location.href = '/pedidos/exportar?status=' + orderStatusFilter.value + '&search=' + orderSearchInput.value;
        });
    }
});