// auth.js
const API_URL = 'https://cafe-system-7nhg.onrender.com'; // ¡Tu URL de producción!

// --- Función Guardián para Proteger Rutas ---
function protectPage() {
    const token = localStorage.getItem('accessToken');
    // Si no hay token Y no estamos en la página de login, redirigir.
    if (!token && !window.location.pathname.endsWith('login.html')) {
        window.location.href = 'login.html';
    }
}

// --- Función de Logout ---
function logout() {
    localStorage.removeItem('accessToken');
    window.location.href = 'login.html';
}


document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');

    if (loginForm) {
        // --- Lógica del Formulario de Login ---
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            errorMessage.textContent = '';

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);

            try {
                const response = await fetch(`${API_URL}/token`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: formData,
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Error al iniciar sesión.');
                }

                const data = await response.json();
                localStorage.setItem('accessToken', data.access_token);
                window.location.href = 'index.html'; // Redirigir al POS

            } catch (error) {
                errorMessage.textContent = error.message;
            }
        });
    }
});

// Ejecutar el guardián en cada carga de página
protectPage();