const apiBaseUrl = "http://127.0.0.1:8000";

function getToken() {
    return localStorage.getItem("oncoai_token");
}

function setToken(token) {
    localStorage.setItem("oncoai_token", token);
}

function removeToken() {
    localStorage.removeItem("oncoai_token");
}

function showSections(show) {
    const manualSection = document.getElementById("manual-section");
    if (manualSection) manualSection.style.display = show ? "block" : "none";

    const batchSection = document.getElementById("batch-section");
    if (batchSection) batchSection.style.display = show ? "block" : "none";

    const loginSection = document.getElementById("login-section");
    if (loginSection) loginSection.style.display = show ? "none" : "block";

    const logoutSection = document.getElementById("logout-section");
    if (logoutSection) logoutSection.style.display = show ? "block" : "none";
}


function showAuthForm(formName) {
    document.querySelectorAll('.auth-form').forEach(form => {
        form.style.display = 'none';
    });
    document.getElementById(`${formName}-form`).style.display = 'block';
}

function setLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.innerHTML = '<span class="loading"></span> Procesando...';
    } else {
        button.disabled = false;
        button.innerHTML = button.getAttribute('data-original-text');
    }
}

function showResult(elementId, message, type = 'info') {
    const element = document.getElementById(elementId);
    element.innerHTML = message;
    element.className = `result ${type}`;
    element.style.display = 'block';
}

function clearResult(elementId) {
    const element = document.getElementById(elementId);
    element.innerHTML = '';
    element.style.display = 'none';
    element.className = 'result';
}

function showRegistrationForm(show) {
    showAuthForm(show ? 'register' : 'password');
}

async function registerUser() {
    if (this.id === 'register-btn') {
        showRegistrationForm(true);
        clearResult('loginResult');
        return;
    }

    const username = document.querySelector('#reg-username').value.trim();
    const email = document.querySelector('#reg-email').value.trim();
    const fullName = document.querySelector('#reg-fullname').value.trim();
    const password = document.querySelector('#reg-password').value.trim();

    if (!username || !email || !fullName || !password) {
        showResult('loginResult', 'Por favor, completa todos los campos', 'error');
        return;
    }

    if (password.length < 6) {
        showResult('loginResult', 'La contraseña debe tener al menos 6 caracteres', 'error');
        return;
    }

    const button = document.querySelector('#submit-register');
    button.setAttribute('data-original-text', button.textContent);
    setLoading(button, true);
    clearResult('loginResult');

    try {
        const response = await fetch(`${apiBaseUrl}/auth/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username,
                password,
                full_name: fullName,
                email: email
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Error en el registro');
        }

        const data = await response.json();
        showResult('loginResult', `✅ Usuario ${data.username} registrado. Ahora puedes iniciar sesión.`, 'success');

        document.getElementById('register-form').reset();
        showRegistrationForm(false);

    } catch (error) {
        showResult('loginResult', `❌ Error: ${error.message}`, 'error');
    } finally {
        setLoading(button, false);
    }
}

async function loginWithPassword(e) {
    e.preventDefault();
    const form = e.target;
    const button = form.querySelector('button[type="submit"]');
    const username = form.querySelector('#username').value.trim();
    const password = form.querySelector('#password').value.trim();

    if (!username || !password) {
        showResult('loginResult', 'Por favor, completa todos los campos', 'error');
        return;
    }

    button.setAttribute('data-original-text', button.textContent);
    setLoading(button, true);
    clearResult('loginResult');

    try {
        console.log("Intentando login con:", username);
        const response = await fetch(`${apiBaseUrl}/token`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                'username': username,
                'password': password
            })
        });

        console.log("Respuesta del servidor:", response.status);

        if (!response.ok) {
            const errorData = await response.json().catch((e) => {
                console.error("Error al parsear respuesta:", e);
                return {};
            });
            console.error("Error data:", errorData);
            throw new Error(errorData.detail || 'Error de autenticación');
        }

        const data = await response.json();
        setToken(data.access_token);

        if (data.user) {
            localStorage.setItem("oncoai_user", JSON.stringify(data.user));
        }

        showSections(true);

        // Redirect to landing page after successful login
        window.location.href = 'oncoai-landing.html';

        const userName = data.user?.name || username;
        showResult('loginResult', `✅ Bienvenido/a, ${userName}. Sesión iniciada correctamente.`, 'success');

    } catch (error) {
        showResult('loginResult', `❌ Error: ${error.message}`, 'error');
    } finally {
        setLoading(button, false);
    }
}


function logout() {
    removeToken();
    localStorage.removeItem("oncoai_user");
    showSections(false);
    clearResult('loginResult');
    clearResult('result');
    clearResult('batchResult');

    document.getElementById('password-form').reset();
    document.getElementById('predictForm').reset();
    document.getElementById('batchForm').reset();

    createInputFields();

    showResult('loginResult', '✅ Sesión cerrada correctamente', 'success');
}

function initAuth() {
    document.querySelectorAll('button[type="submit"]').forEach(button => {
        button.setAttribute('data-original-text', button.textContent);
    });

    if (getToken()) {
        showSections(true);

        const userInfo = localStorage.getItem("oncoai_user");
        let userName = "Usuario";

        if (userInfo) {
            try {
                const user = JSON.parse(userInfo);
                userName = user.name || user.username || "Usuario";
            } catch (e) {
                console.error("Error parsing user info:", e);
            }
        }

        showResult('loginResult', `🔐 Bienvenido/a de nuevo, ${userName}. Sesión activa.`, 'success');
    }

    setupAuthEventListeners();
}

function setupAuthEventListeners() {
    document.getElementById('password-form').addEventListener('submit', loginWithPassword);

    document.getElementById('logout-btn').addEventListener('click', logout);

    document.getElementById('register-btn').addEventListener('click', registerUser);

    document.getElementById('submit-register').addEventListener('click', registerUser);

    document.getElementById('back-to-login').addEventListener('click', () => {
        showRegistrationForm(false);
        clearResult('loginResult');
    });
}

function redirectToDashboard() {
    const token = localStorage.getItem('oncoai_token');
    if (token) {
        window.location.href = 'oncoai-model-survival.html';
    } else {
        window.location.href = 'oncoai-landing.html';
    }
}

document.addEventListener('DOMContentLoaded', initAuth);
