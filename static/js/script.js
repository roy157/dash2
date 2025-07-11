// static/js/script.js

document.addEventListener('DOMContentLoaded', function() {
    // --- Utilidades para Modales ---
    function openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'block';
        }
    }

    function closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
        }
    }

    document.querySelectorAll('.close-modal').forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                closeModal(modal.id);
            }
        });
    });

    window.addEventListener('click', function(event) {
        const modalIds = ['add-product-modal', 'edit-product-modal'];
        modalIds.forEach(id => {
            const modal = document.getElementById(id);
            if (modal && event.target === modal) {
                closeModal(id);
            }
        });
    });

    // --- Script para el filtro por categoría ---
    const categoryFilter = document.getElementById('productCategoryFilter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            const selectedCategoryValue = this.value;
            let newUrl = '/productos/';
            if (selectedCategoryValue) {
                newUrl += `?categoria=${selectedCategoryValue}`;
            }
            window.location.href = newUrl;
        });
    }

    // --- Script para la búsqueda en tiempo real ---
    const searchInput = document.getElementById('productSearchInput');
    const productTableBody = document.querySelector('#products-table tbody');
    let productRows = productTableBody ? productTableBody.querySelectorAll('.product-row') : [];
    const noProductsMessage = document.getElementById('no-products-message'); 
    const noFilteredProductsMessage = document.getElementById('no-filtered-products');

    if (searchInput && productTableBody) {
        searchInput.addEventListener('keyup', function() {
            const searchTerm = searchInput.value.toLowerCase();
            let foundMatch = false; 

            if (noProductsMessage) { 
                noProductsMessage.style.display = 'none';
            }
            
            productRows = productTableBody.querySelectorAll('.product-row');

            productRows.forEach(row => {
                const productNameElement = row.querySelector('.product-name');
                if (productNameElement) {
                    const productName = productNameElement.textContent.toLowerCase();

                    if (productName.includes(searchTerm)) {
                        row.style.display = ''; 
                        foundMatch = true;
                    } else {
                        row.style.display = 'none'; 
                    }
                }
            });

            if (foundMatch) {
                noFilteredProductsMessage.style.display = 'none';
            } else {
                noFilteredProductsMessage.style.display = 'block';
            }
        });
    }

    // --- Script para abrir el modal "Agregar Producto" ---
    const addProductBtn = document.getElementById('addProductBtn');
    if (addProductBtn) {
        addProductBtn.addEventListener('click', function() {
            document.getElementById('add-product-form').reset();
            openModal('add-product-modal');
        });
    }

    // --- Script para el modal "Editar Producto" ---
    document.addEventListener('click', async function(event) {
        if (event.target.closest('.edit-product-btn')) {
            const button = event.target.closest('.edit-product-btn');
            const productId = button.dataset.productId; 
            console.log(`Edit button clicked for product ID: ${productId}`);

            try {
                // Usar la nueva ruta API para obtener los detalles del producto
                const response = await fetch(`/productos/api/${productId}`); 
                if (!response.ok) {
                    const errorText = await response.text();
                    console.error('Server response not OK:', response.status, errorText);
                    throw new Error('Network response was not ok: ' + response.status + ' ' + errorText);
                }
                const data = await response.json();

                // Rellena los campos del formulario de edición con los datos recibidos
                document.getElementById('edit-product-id').value = data.id;
                document.getElementById('edit-product-name').value = data.nombre;
                document.getElementById('edit-product-description').value = data.descripcion;
                document.getElementById('edit-product-price').value = data.precio;
                document.getElementById('edit-product-stock').value = data.stock;
                
                const categorySelect = document.getElementById('edit-product-category');
                categorySelect.value = data.categoria_id;

                openModal('edit-product-modal');
            } catch (error) {
                console.error('Error al cargar datos para edición:', error);
                alert('No se pudieron cargar los datos del producto para editar. Error: ' + error.message);
            }
        }
    });

    // --- Manejo del envío del formulario de edición (con AJAX) ---
    const editProductForm = document.getElementById('edit-product-form');
    if (editProductForm) {
        editProductForm.addEventListener('submit', async function(event) {
            event.preventDefault();

            const formData = new FormData(this);
            const productId = document.getElementById('edit-product-id').value;

            try {
                const response = await fetch(`/productos/editar/${productId}`, { 
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const errorJson = await response.json();
                    throw new Error(errorJson.message || 'Error al actualizar el producto.');
                }

                const data = await response.json();
                
                if (data.success) {
                    alert('Producto actualizado exitosamente!');
                    closeModal('edit-product-modal');
                    window.location.reload();
                } else {
                    alert('Error: ' + (data.message || 'No se pudo actualizar el producto.'));
                }
            } catch (error) {
                console.error('Error al enviar el formulario de edición:', error);
                alert('Hubo un error al guardar los cambios: ' + error.message);
            }
        });
    }

    // --- Manejo del envío del formulario de agregar producto (con AJAX) ---
    const addProductForm = document.getElementById('add-product-form');
    if (addProductForm) {
        addProductForm.addEventListener('submit', async function(event) {
            event.preventDefault();

            const formData = new FormData(this);

            try {
                const response = await fetch(this.action, {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const errorJson = await response.json();
                    throw new Error(errorJson.message || 'Error al agregar el producto.');
                }

                const data = await response.json();
                
                if (data.success) {
                    alert('Producto agregado exitosamente!');
                    closeModal('add-product-modal');
                    window.location.reload();
                } else {
                    alert('Error: ' + (data.message || 'No se pudo agregar el producto.'));
                }
            } catch (error) {
                console.error('Error al enviar el formulario de agregar:', error);
                alert('Hubo un error al agregar el producto: ' + error.message);
            }
        });
    }
});
