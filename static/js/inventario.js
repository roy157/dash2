document.addEventListener('DOMContentLoaded', () => {

    // --- Lógica general para abrir y cerrar cualquier modal ---
    function openModal(modal) {
        if (modal) modal.classList.add('is-active');
    }

    function closeModal(modal) {
        if (modal) modal.classList.remove('is-active');
    }

    // Abrir modales al hacer clic en los botones
    document.querySelectorAll('[data-modal-target]').forEach(button => {
        button.addEventListener('click', () => {
            const modal = document.querySelector(button.dataset.modalTarget);
            openModal(modal);
        });
    });

    // Cerrar modales con el botón de 'x' o el de 'Cancelar'
    document.querySelectorAll('[data-close-button]').forEach(button => {
        button.addEventListener('click', () => {
            const modal = button.closest('.modal');
            closeModal(modal);
        });
    });

    // --- Lógica para enviar los formularios de los modales ---
    const handleFormSubmit = (formId, modalId) => {
        const form = document.getElementById(formId);
        if (!form) return;

        form.addEventListener('submit', function(e) {
            e.preventDefault(); // Evita que la página se recargue

            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message); // Muestra el mensaje del servidor
                if (data.success) {
                    closeModal(document.getElementById(modalId));
                    window.location.reload(); // Recarga la página para ver los cambios
                }
            })
            .catch(error => console.error('Error:', error));
        });
    };

    // Aplicar la lógica a ambos formularios
    handleFormSubmit('entry-form', 'entry-modal');
    handleFormSubmit('exit-form', 'exit-modal');
});