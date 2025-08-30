function checkAuthStatus() {
    const token = localStorage.getItem('oncoai_token');
    const authLink = document.getElementById('auth-link');
    const logoutLink = document.getElementById('logout-link');
    const modelsContainer = document.getElementById('models-container');
    const authPrompt = document.getElementById('auth-prompt');
    const modelsDescription = document.getElementById('models-description');

    if (token) {
        // Usuario autenticado
        authLink.style.display = 'none';
        logoutLink.style.display = 'block';
        modelsContainer.style.display = 'block';
        authPrompt.style.display = 'none';
        modelsDescription.textContent = 'We offer predictive models to help in oncology. Click on a model to make predictions.';
    } else {
        // Usuario no autenticado
        authLink.style.display = 'block';
        logoutLink.style.display = 'none';
        modelsContainer.style.display = 'none';
        authPrompt.style.display = 'block';
        modelsDescription.textContent = 'We offer predictive models to help in oncology. Please authenticate to access our models.';
    }
}

function logout() {
    localStorage.removeItem('oncoai_token');
    localStorage.removeItem('oncoai_user');
    checkAuthStatus();
}

// Verificar estado de autenticación al cargar la página
document.addEventListener('DOMContentLoaded', checkAuthStatus);
