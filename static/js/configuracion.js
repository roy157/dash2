document.addEventListener('DOMContentLoaded', function() {
    // Esta función solo se ejecutará para Admins porque el script se carga condicionalmente
    
    const userModal = document.getElementById('userModal');
    const addUserBtn = document.getElementById('addUserBtn');
    const closeModalBtns = document.querySelectorAll('.close-modal');
    const userForm = document.getElementById('userForm');

    // Si algún elemento no se encuentra, salimos para evitar errores.
    if (!userModal || !addUserBtn || !userForm) {
        return;
    }

    const modalTitle = document.getElementById('modalTitle');
    const editUserIdInput = document.getElementById('editUserId');
    const passwordInput = document.getElementById('userPassword');
    const passwordHelp = document.getElementById('passwordHelp');

    const openModal = () => userModal.style.display = 'flex';
    const closeModal = () => {
        userModal.style.display = 'none';
        userForm.reset();
        if (editUserIdInput) editUserIdInput.value = '';
    };

    addUserBtn.addEventListener('click', () => {
        userForm.reset();
        modalTitle.textContent = 'Añadir Usuario';
        if (editUserIdInput) editUserIdInput.value = '';
        passwordInput.required = true;
        passwordHelp.style.display = 'none';
        openModal();
    });

    document.querySelectorAll('.edit-user-btn').forEach(button => {
        button.addEventListener('click', async (e) => {
            const userId = e.currentTarget.dataset.userId;
            if (editUserIdInput) editUserIdInput.value = userId;
            modalTitle.textContent = 'Editar Usuario';
            passwordInput.required = false;
            passwordHelp.style.display = 'block';
            
            const response = await fetch(`/configuracion/api/usuario/${userId}`);
            if (!response.ok) { return alert('Error al cargar datos del usuario.'); }
            const data = await response.json();
            
            document.getElementById('userEmail').value = data.email;
            document.getElementById('userRole').value = data.role;
            openModal();
        });
    });

    closeModalBtns.forEach(btn => btn.addEventListener('click', closeModal));
    window.addEventListener('click', (e) => {
        if (e.target === userModal) closeModal();
    });

    userForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const editUserId = editUserIdInput ? editUserIdInput.value : null;
        const formData = {
            email: document.getElementById('userEmail').value,
            password: passwordInput.value,
            role: document.getElementById('userRole').value,
        };

        let url = '/configuracion/api/usuario';
        let method = 'POST';

        if (editUserId) {
            url = `/configuracion/api/usuario/${editUserId}`;
            method = 'PUT';
            if (!formData.password) delete formData.password;
        }

        const response = await fetch(url, {
            method: method,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(formData)
        });
        const result = await response.json();
        alert(result.message);
        if (response.ok) window.location.reload();
    });

    document.querySelectorAll('.delete-user-btn').forEach(button => {
        button.addEventListener('click', async (e) => {
            const userId = e.currentTarget.dataset.userId;
            if (!confirm(`¿Estás seguro de que deseas eliminar este usuario?`)) return;

            const response = await fetch(`/configuracion/api/usuario/${userId}`, { method: 'DELETE' });
            const result = await response.json();
            alert(result.message);
            if (response.ok) window.location.reload();
        });
    });
});