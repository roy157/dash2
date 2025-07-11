// static/js/clients.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('clients.js cargado y ejecutándose'); // ¡Verifica esto en la consola del navegador!

    // Referencias a los elementos del DOM
    const viewClientModal = document.getElementById('view-client-modal');
    const addClientModal = document.getElementById('add-client-modal');
    const editClientModal = document.getElementById('edit-client-modal');
    const deleteConfirmModal = document.getElementById('delete-confirm-modal');

    const addClientBtn = document.getElementById('add-client-btn');
    const clientsTable = document.getElementById('clients-table');
    const allCloseButtons = document.querySelectorAll('.modal .close-modal');

    // Formularios
    const addClientForm = document.getElementById('add-client-form');
    const editClientForm = document.getElementById('edit-client-form');
    let clientIdToDelete = null; // Variable para guardar el ID del cliente a eliminar

    // --- Funciones de Utilidad ---

    // Función para mostrar mensajes de "flash" (simulados para respuestas AJAX)
    function showFlashMessage(message, category) {
        const flashContainer = document.querySelector('.main-content'); // O donde quieras mostrar el mensaje
        if (!flashContainer) {
            console.warn('Contenedor para mensajes flash (.main-content) no encontrado.');
            return;
        }

        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${category}`; // Asume clases CSS como 'alert-success', 'alert-danger'
        alertDiv.textContent = message;
        flashContainer.prepend(alertDiv); // Añade al principio del contenido principal

        setTimeout(() => {
            alertDiv.remove();
        }, 5000); // Elimina el mensaje después de 5 segundos
    }

    // Función para abrir un modal
    function openModal(modalElement) {
        if (modalElement) {
            modalElement.style.display = 'flex'; // Usamos flex para centrar el contenido del modal
            modalElement.setAttribute('aria-hidden', 'false'); // Para accesibilidad
        } else {
            console.error('Se intentó abrir un elemento modal nulo.');
        }
    }

    // Función para cerrar un modal
    function closeModal(modalElement) {
        if (modalElement) {
            modalElement.style.display = 'none';
            modalElement.setAttribute('aria-hidden', 'true'); // Para accesibilidad
            // Limpiar formularios al cerrar
            if (modalElement === addClientModal) addClientForm.reset();
            if (modalElement === editClientModal) editClientForm.reset();
        } else {
            console.error('Se intentó cerrar un elemento modal nulo.');
        }
    }

    // Función para recargar la tabla de clientes (después de una operación CUD)
    async function refreshClientTable() {
        try {
            const response = await fetch('/clientes/api/all'); // Obtiene todos los clientes de la API
            if (!response.ok) throw new Error('Error al obtener clientes desde la API.');
            const clientes = await response.json();

            const tbody = clientsTable.querySelector('tbody');
            if (!tbody) {
                console.error('Cuerpo de la tabla de clientes (tbody) no encontrado para recargar.');
                return;
            }
            tbody.innerHTML = ''; // Limpiar la tabla actual

            if (clientes.length === 0) {
                const noResultsRow = document.createElement('tr');
                noResultsRow.innerHTML = `<td colspan="6" class="no-results-message">No hay clientes registrados.</td>`;
                tbody.appendChild(noResultsRow);
                return;
            }

            clientes.forEach(client => {
                const row = document.createElement('tr');
                row.dataset.clientId = client.id;
                row.innerHTML = `
                    <td>${client.id}</td>
                    <td>${client.nombre}</td>
                    <td>${client.email}</td>
                    <td>${client.telefono || 'N/A'}</td>
                    <td>${new Date(client.fecha_registro).toLocaleDateString('es-ES', { year: 'numeric', month: '2-digit', day: '2-digit' })}</td>
                    <td class="actions-cell">
                        <button class="btn btn-primary view-client-btn" data-client-id="${client.id}" title="Ver Detalle"><i class="fas fa-eye"></i></button>
                        <button class="btn btn-secondary edit-client-btn" data-client-id="${client.id}" title="Editar"><i class="fas fa-edit"></i></button>
                        <button class="btn btn-danger delete-client-btn" data-client-id="${client.id}" title="Eliminar"><i class="fas fa-trash-alt"></i></button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } catch (error) {
            console.error('Error al recargar la tabla de clientes:', error);
            showFlashMessage('Error al recargar la lista de clientes.', 'danger');
        }
    }

    // --- Event Listeners para Abrir Modales ---

    // Abrir modal "Añadir Cliente"
    if (addClientBtn) {
        addClientBtn.addEventListener('click', () => {
            addClientForm.reset(); // Limpia el formulario antes de abrir el modal
            openModal(addClientModal);
        });
    } else {
        console.error('El botón "Añadir Cliente" (#add-client-btn) no fue encontrado.');
    }

    // Delegación de eventos para los botones de acción en la tabla (Ver, Editar, Eliminar)
    if (clientsTable) {
        clientsTable.addEventListener('click', async function(event) {
            const target = event.target.closest('button'); // Encuentra el botón más cercano
            if (!target) return; // Si no se hizo clic en un botón, salir

            const clientId = target.dataset.clientId;
            if (!clientId) return; // Si el botón no tiene un ID de cliente, salir

            // Ver Detalle del Cliente
            if (target.classList.contains('view-client-btn')) {
                try {
                    const response = await fetch(`/clientes/api/${clientId}`);
                    if (!response.ok) throw new Error(`Error HTTP! Estado: ${response.status}`);
                    const client = await response.json();

                    document.getElementById('modal-client-id-display').textContent = client.id;
                    document.getElementById('modal-client-name').textContent = client.nombre;
                    document.getElementById('modal-client-email').textContent = client.email;
                    document.getElementById('modal-client-phone').textContent = client.telefono || 'N/A';
                    document.getElementById('modal-client-address').textContent = client.direccion || 'N/A';
                    const regDate = client.fecha_registro ? new Date(client.fecha_registro) : null;
                    document.getElementById('modal-client-registration-date').textContent = regDate ? regDate.toLocaleDateString('es-ES', { year: 'numeric', month: '2-digit', day: '2-digit' }) : 'N/A';
                    
                    openModal(viewClientModal);
                } catch (error) {
                    console.error('Error al obtener detalles del cliente:', error);
                    showFlashMessage('No se pudieron cargar los detalles del cliente.', 'danger');
                }
            }
            // Editar Cliente
            else if (target.classList.contains('edit-client-btn')) {
                try {
                    const response = await fetch(`/clientes/api/${clientId}`);
                    if (!response.ok) throw new Error(`Error HTTP! Estado: ${response.status}`);
                    const client = await response.json();

                    document.getElementById('edit-client-id').value = client.id;
                    document.getElementById('edit-modal-client-id-display').textContent = client.id;
                    document.getElementById('edit-nombre').value = client.nombre;
                    document.getElementById('edit-email').value = client.email;
                    document.getElementById('edit-telefono').value = client.telefono || '';
                    document.getElementById('edit-direccion').value = client.direccion || '';
                    
                    openModal(editClientModal);
                } catch (error) {
                    console.error('Error al obtener datos para editar:', error);
                    showFlashMessage('No se pudieron cargar los datos del cliente para editar.', 'danger');
                }
            }
            // Eliminar Cliente (abrir modal de confirmación)
            else if (target.classList.contains('delete-client-btn')) {
                clientIdToDelete = clientId; // Guarda el ID para la confirmación
                const row = target.closest('tr');
                const clientName = row.querySelector('td:nth-child(2)').textContent; // Asume que el nombre está en la segunda celda
                
                document.getElementById('delete-modal-client-id-display').textContent = clientId;
                document.getElementById('delete-modal-client-name').textContent = clientName;
                openModal(deleteConfirmModal);
            }
        });
    } else {
        console.error('La tabla de clientes (#clients-table) no fue encontrada. Los botones de acción no funcionarán.');
    }

    // --- Event Listeners para Cerrar Modales ---

    // Cerrar cualquier modal al hacer clic en el botón con clase 'close-modal'
    allCloseButtons.forEach(button => {
        button.addEventListener('click', function() {
            closeModal(button.closest('.modal')); // Encuentra el modal padre y lo cierra
        });
    });

    // Cerrar cualquier modal al hacer clic fuera del contenido del modal
    window.addEventListener('click', function(event) {
        if (event.target === viewClientModal) closeModal(viewClientModal);
        if (event.target === addClientModal) closeModal(addClientModal);
        if (event.target === editClientModal) closeModal(editClientModal);
        if (event.target === deleteConfirmModal) closeModal(deleteConfirmModal);
    });

    // --- Manejo de Formularios (AJAX) ---

    // Formulario "Añadir Cliente"
    if (addClientForm) {
        addClientForm.addEventListener('submit', async function(event) {
            event.preventDefault(); // Evita el envío tradicional del formulario
            const formData = new FormData(this);
            const clientData = Object.fromEntries(formData.entries()); // Convierte FormData a un objeto JSON

            try {
                const response = await fetch('/clientes/nuevo', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json', // Importante para enviar JSON
                    },
                    body: JSON.stringify(clientData), // Envía los datos como JSON
                });
                const result = await response.json(); // Parsea la respuesta JSON del servidor

                if (response.ok) { // Si la respuesta HTTP es 2xx (éxito)
                    showFlashMessage(result.message, 'success');
                    closeModal(addClientModal);
                    await refreshClientTable(); // Recarga la tabla para mostrar el nuevo cliente
                } else {
                    showFlashMessage(result.error || 'Error al añadir cliente.', 'danger');
                }
            } catch (error) {
                console.error('Error en la petición al añadir cliente:', error);
                showFlashMessage('Error de conexión al añadir cliente.', 'danger');
            }
        });
    }

    // Formulario "Editar Cliente"
    if (editClientForm) {
        editClientForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            const clientId = document.getElementById('edit-client-id').value;
            const formData = new FormData(this);
            const clientData = Object.fromEntries(formData.entries());

            try {
                const response = await fetch(`/clientes/editar/${clientId}`, {
                    method: 'PUT', // Usar PUT para actualizar recursos
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(clientData),
                });
                const result = await response.json();

                if (response.ok) {
                    showFlashMessage(result.message, 'success');
                    closeModal(editClientModal);
                    await refreshClientTable(); // Recarga la tabla para reflejar los cambios
                } else {
                    showFlashMessage(result.error || 'Error al actualizar cliente.', 'danger');
                }
            } catch (error) {
                console.error('Error en la petición al actualizar cliente:', error);
                showFlashMessage('Error de conexión al actualizar cliente.', 'danger');
            }
        });
    }

    // Botón "Confirmar Eliminación"
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', async function() {
            if (!clientIdToDelete) return; // Asegúrate de tener un ID de cliente para eliminar

            try {
                const response = await fetch(`/clientes/eliminar/${clientIdToDelete}`, {
                    method: 'DELETE', // Usar DELETE para eliminar recursos
                    headers: {
                        'Content-Type': 'application/json', // Buena práctica aunque no envíes cuerpo
                    },
                });
                const result = await response.json();

                if (response.ok) {
                    showFlashMessage(result.message, 'success');
                    closeModal(deleteConfirmModal);
                    await refreshClientTable(); // Recarga la tabla después de eliminar
                } else {
                    showFlashMessage(result.error || 'Error al eliminar cliente.', 'danger');
                }
            } catch (error) {
                console.error('Error en la petición al eliminar cliente:', error);
                showFlashMessage('Error de conexión al eliminar cliente.', 'danger');
            } finally {
                clientIdToDelete = null; // Limpia el ID guardado
            }
        });
    }
});