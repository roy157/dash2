// static/js/script.js

document.addEventListener('DOMContentLoaded', function() {
    // --- Utilidades para Modales ---
    function openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.style.display = 'block';
    }

    function closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.style.display = 'none';
    }

    document.querySelectorAll('.close-modal').forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) closeModal(modal.id);
        });
    });

    window.addEventListener('click', function(event) {
        const modalIds = ['add-product-modal', 'edit-product-modal'];
        modalIds.forEach(id => {
            const modal = document.getElementById(id);
            if (modal && event.target === modal) closeModal(id);
        });
    });

    // --- Scripts de Filtro y Búsqueda ---
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

    const searchInput = document.getElementById('productSearchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const searchTerm = searchInput.value.toLowerCase();
            const productRows = document.querySelectorAll('#products-table tbody .product-row');
            let foundProducts = 0;

            productRows.forEach(row => {
                const productName = row.querySelector('.product-name').textContent.toLowerCase();
                if (productName.includes(searchTerm)) {
                    row.style.display = '';
                    foundProducts++;
                } else {
                    row.style.display = 'none';
                }
            });

            const noFilteredProductsMessage = document.getElementById('no-filtered-products');
            if (foundProducts === 0) {
                noFilteredProductsMessage.style.display = 'block';
            } else {
                noFilteredProductsMessage.style.display = 'none';
            }
        });
    }

    // =================================================================
    // --- INICIO: LÓGICA REFACTORIZADA PARA GESTIÓN DE IMÁGENES ---
    // =================================================================

    // Objeto para almacenar los archivos de los formularios 'add' y 'edit'
    const fileStore = {
        add: [], // Para nuevas imágenes en el modal de añadir
        edit: [] // Para nuevas imágenes seleccionadas en el modal de editar
    };

    // Array para almacenar las imágenes YA EXISTENTES del producto en edición
    let currentImages = [];

    /**
     * Renderiza las previsualizaciones de imágenes en un contenedor.
     * @param {string} formType - 'add', 'new-edit' (para nuevas en edición), o 'current-edit' (para existentes en edición).
     * @param {HTMLElement} previewContainer - El div donde se mostrarán las imágenes.
     * @param {Array} imagesArray - El array de archivos (File) o de objetos de imagen ({id, url}).
     */
    function renderPreviews(formType, previewContainer, imagesArray) {
        previewContainer.innerHTML = ''; // Limpia el contenedor
        
        if (!imagesArray || imagesArray.length === 0) {
            const messageDiv = document.createElement('div');
            messageDiv.style.cssText = "color: #888; font-size: 0.9em; width: 100%; text-align: center; align-self: center;";
            if (formType === 'current-edit') {
                messageDiv.textContent = "No hay imágenes actuales para este producto.";
            } else {
                messageDiv.textContent = "Aquí aparecerán las imágenes seleccionadas.";
            }
            previewContainer.appendChild(messageDiv);
            return;
        }

        imagesArray.forEach((item, index) => {
            const reader = new FileReader();
            // Determina si es un objeto File (nueva imagen) o un objeto {id, url} (imagen existente)
            const isFile = item instanceof File;
            const imageUrl = isFile ? null : item.url; // Si es existente, usa la URL directamente

            // Si es un archivo, léelo; si no, renderiza directamente.
            if (isFile) {
                reader.onload = function(e) {
                    createImagePreviewElement(previewContainer, e.target.result, formType, index, isFile ? null : item.id);
                };
                reader.readAsDataURL(item);
            } else {
                createImagePreviewElement(previewContainer, imageUrl, formType, index, item.id);
            }
        });
    }

    /**
     * Crea y añade un elemento de previsualización de imagen al contenedor.
     * @param {HTMLElement} container - El contenedor de previsualización.
     * @param {string} src - La URL o DataURL de la imagen.
     * @param {string} formType - 'add', 'new-edit', 'current-edit'.
     * @param {number} index - El índice en el array de origen (fileStore.add, fileStore.edit, currentImages).
     * @param {number|null} imageId - El ID de la imagen si es una imagen existente (de la DB).
     */
    function createImagePreviewElement(container, src, formType, index, imageId) {
        const wrapper = document.createElement('div');
        wrapper.classList.add('preview-image-wrapper');

        const img = document.createElement('img');
        img.src = src;
        img.classList.add('preview-image');

        const deleteBtn = document.createElement('span');
        deleteBtn.classList.add('delete-preview-btn');
        deleteBtn.innerHTML = '&times;'; // Símbolo 'X'
        deleteBtn.dataset.index = index;
        deleteBtn.dataset.formType = formType;
        if (imageId) {
            deleteBtn.dataset.imageId = imageId; // Guarda el ID de la imagen si es existente
        }

        wrapper.appendChild(img);
        wrapper.appendChild(deleteBtn);
        container.appendChild(wrapper);
    }

    /**
     * Maneja la selección de nuevos archivos desde el input.
     * @param {Event} e - El evento 'change' del input.
     * @param {string} formType - 'add' o 'edit'.
     * @param {HTMLElement} previewContainer - El contenedor para las previsualizaciones.
     */
    function handleFileSelect(e, formType, previewContainer) {
        const newFiles = Array.from(e.target.files);
        fileStore[formType] = fileStore[formType].concat(newFiles);
        // Renderiza solo las nuevas imágenes para el contenedor de nuevas imágenes
        renderPreviews('new-edit', previewContainer, fileStore[formType]);
        e.target.value = null; // Resetea el valor del input para permitir seleccionar los mismos archivos
    }

    // --- Configuración para el modal de AGREGAR producto ---
    const addImageInput = document.getElementById('product-images');
    const addImagePreviewContainer = document.getElementById('add-image-preview');
    if (addImageInput) {
        addImageInput.addEventListener('change', (e) => handleFileSelect(e, 'add', addImagePreviewContainer));
    }

    // --- Configuración para el modal de EDITAR producto ---
    const editImageInput = document.getElementById('edit-product-images');
    const newImagePreviewContainer = document.getElementById('new-image-preview'); // Este es el contenedor para las nuevas imágenes en edición
    const currentImagePreviewContainer = document.getElementById('current-image-preview'); // Este es el contenedor para las imágenes existentes en edición

    if (editImageInput) {
        editImageInput.addEventListener('change', (e) => handleFileSelect(e, 'edit', newImagePreviewContainer));
    }

    // --- Event listener DELEGADO para los botones de eliminar ---
    document.addEventListener('click', async function(e) {
        if (e.target.classList.contains('delete-preview-btn')) {
            const formType = e.target.dataset.formType;
            const index = parseInt(e.target.dataset.index, 10);
            const imageId = e.target.dataset.imageId; // Solo presente para imágenes existentes

            if (formType === 'add') {
                // Eliminar imagen NUEVA del modal de añadir
                fileStore.add.splice(index, 1);
                renderPreviews('add', addImagePreviewContainer, fileStore.add);
            } else if (formType === 'new-edit') {
                // Eliminar imagen NUEVA del modal de editar
                fileStore.edit.splice(index, 1);
                renderPreviews('new-edit', newImagePreviewContainer, fileStore.edit);
            } else if (formType === 'current-edit' && imageId) {
                // Eliminar imagen EXISTENTE del modal de editar (requiere llamada al servidor)
                if (confirm('¿Estás seguro de que quieres eliminar esta imagen? Esta acción es irreversible.')) {
                    try {
                        const response = await fetch(`/productos/api/delete-image/${imageId}`, {
                            method: 'DELETE',
                            headers: {
                                'Content-Type': 'application/json'
                            }
                        });
                        const data = await response.json();
                        if (!response.ok) throw new Error(data.message || 'Error al eliminar la imagen.');

                        alert('Imagen eliminada exitosamente!');
                        // Eliminar la imagen del array currentImages y del DOM
                        currentImages = currentImages.filter(img => img.id !== parseInt(imageId, 10));
                        renderPreviews('current-edit', currentImagePreviewContainer, currentImages);
                    } catch (error) {
                        console.error('Error al eliminar imagen existente:', error);
                        alert('Hubo un error al eliminar la imagen: ' + error.message);
                    }
                }
            }
        }
    });

    // --- Script para abrir el modal "Agregar Producto" (MODIFICADO) ---
    const addProductBtn = document.getElementById('addProductBtn');
    if (addProductBtn) {
        addProductBtn.addEventListener('click', function() {
            document.getElementById('add-product-form').reset();
            // Limpia el almacén de archivos y el contenedor al abrir
            fileStore.add = [];
            renderPreviews('add', addImagePreviewContainer, fileStore.add); // Pasa un array vacío al inicio
            openModal('add-product-modal');
        });
    }
    
    // --- Script para abrir el modal "Editar Producto" (MODIFICADO) ---
    document.addEventListener('click', async function(event) {
        if (event.target.closest('.edit-product-btn')) {
            const button = event.target.closest('.edit-product-btn');
            const productId = button.dataset.productId;

            // Limpia el almacén de archivos de edición para nuevas imágenes
            fileStore.edit = [];
            // Limpia el array de imágenes actuales y los contenedores de previsualización
            currentImages = [];
            renderPreviews('new-edit', newImagePreviewContainer, fileStore.edit); // Vacio
            renderPreviews('current-edit', currentImagePreviewContainer, currentImages); // Vacio

            document.getElementById('edit-product-form').reset(); // Resetea el formulario

            try {
                const response = await fetch(`/productos/api/${productId}`);
                if (!response.ok) throw new Error('No se pudo cargar la información del producto.');
                const data = await response.json();

                document.getElementById('edit-product-id').value = data.id;
                document.getElementById('edit-product-name').value = data.nombre;
                document.getElementById('edit-product-description').value = data.descripcion;
                document.getElementById('edit-product-price').value = data.precio;
                document.getElementById('edit-product-stock').value = data.stock;
                document.getElementById('edit-product-category').value = data.categoria_id;

                // Carga las imágenes existentes y las renderiza
                currentImages = data.imagenes || []; // Asegúrate de que 'imagenes' contenga objetos {id, url}
                renderPreviews('current-edit', currentImagePreviewContainer, currentImages);

                openModal('edit-product-modal');
            } catch (error) {
                alert(error.message);
                console.error("Error al cargar datos del producto para edición:", error);
            }
        }
    });

    // --- Manejo del envío del formulario de AGREGAR (SIN CAMBIOS Mayores) ---
    const addProductForm = document.getElementById('add-product-form');
    if (addProductForm) {
        addProductForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            const formData = new FormData();
            formData.append('nombre', this.nombre.value);
            formData.append('descripcion', this.descripcion.value);
            formData.append('precio', this.precio.value);
            formData.append('stock', this.stock.value);
            formData.append('categoria_id', this.categoria_id.value);
            
            fileStore.add.forEach(file => {
                formData.append('imagenes', file);
            });

            try {
                const response = await fetch(this.action, { method: 'POST', body: formData });
                const data = await response.json();
                if (!response.ok) throw new Error(data.message || 'Error en el servidor');
                
                alert('Producto agregado exitosamente!');
                closeModal('add-product-modal');
                window.location.reload();
            } catch (error) {
                console.error('Error al agregar producto:', error);
                alert('Hubo un error al agregar el producto: ' + error.message);
            }
        });
    }

    // --- Manejo del envío del formulario de EDICIÓN (MODIFICADO SIGNIFICATIVAMENTE) ---
    const editProductForm = document.getElementById('edit-product-form');
    if (editProductForm) {
        editProductForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            const productId = document.getElementById('edit-product-id').value;
            const formData = new FormData();

            formData.append('nombre', this.nombre.value);
            formData.append('descripcion', this.descripcion.value);
            formData.append('precio', this.precio.value);
            formData.append('stock', this.stock.value);
            formData.append('categoria_id', this.categoria_id.value);

            // Solo añade los NUEVOS archivos del fileStore.edit
            fileStore.edit.forEach(file => {
                formData.append('imagenes', file);
            });
            
            try {
                const response = await fetch(`/productos/editar/${productId}`, { method: 'POST', body: formData });
                const data = await response.json();
                if (!response.ok) throw new Error(data.message || 'Error en el servidor');

                alert('Producto actualizado exitosamente!');
                closeModal('edit-product-modal');
                window.location.reload();
            } catch (error) {
                console.error('Error al editar producto:', error);
                alert('Hubo un error al guardar los cambios: ' + error.message);
            }
        });
    }
});