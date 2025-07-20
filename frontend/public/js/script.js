// Глобальные переменные
let currentUser = null;

// ==================== Функции отображения ====================
function showLoading(show = true) {
    document.getElementById('loading-indicator').style.display = show ? 'inline' : 'none';
}

function displayResponse(data, status = null) {
    console.log('[displayResponse] Received data:', data);
    
    const responseElement = document.getElementById('response');
    if (!responseElement) {
        console.error('Error: Could not find response element');
        return;
    }

    try {
        let output;
        if (typeof data === 'string') {
            try {
                output = JSON.parse(data);
                responseElement.textContent = JSON.stringify({
                    timestamp: new Date().toISOString(),
                    status: status,
                    data: output
                }, null, 2);
                return;
            } catch (e) {
                output = data;
            }
        } else {
            output = data;
        }

        const result = {
            timestamp: new Date().toISOString(),
            status: status,
            data: output
        };

        responseElement.textContent = JSON.stringify(result, null, 2);
    } catch (error) {
        console.error('[displayResponse] Error:', error);
        responseElement.textContent = `Ошибка отображения данных: ${error.message}\nНеобработанные данные: ${JSON.stringify(data)}`;
    } finally {
        showLoading(false);
    }
}

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
    }
}

function clearError(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = '';
    }
}

function updateAuthStatus() {
    const authElement = document.getElementById('auth-status');
    const roleBadge = document.getElementById('role-badge');
    
    if (currentUser) {
        authElement.textContent = `Авторизован как: ${currentUser.username}`;
        authElement.className = 'auth-status authenticated';
        
        if (currentUser.role === 'admin') {
            document.getElementById('admin-section').style.display = 'block';
            document.getElementById('moderator-section').style.display = 'block';
            roleBadge.textContent = 'ADMIN';
            roleBadge.className = 'role-badge admin';
        } else if (currentUser.role === 'moderator') {
            document.getElementById('moderator-section').style.display = 'block';
            roleBadge.textContent = 'MODERATOR';
            roleBadge.className = 'role-badge moderator';
        } else {
            roleBadge.textContent = 'USER';
            roleBadge.className = 'role-badge user';
        }
    } else {
        authElement.textContent = 'Не авторизован';
        authElement.className = 'auth-status not-authenticated';
        document.getElementById('admin-section').style.display = 'none';
        document.getElementById('moderator-section').style.display = 'none';
        roleBadge.textContent = '';
    }
}

// ==================== API функции ====================
async function makeRequest(method, endpoint, body = null) {
    showLoading(true);
    console.log(`[makeRequest] Sending ${method} request to ${endpoint}`, body);
    
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        const token = localStorage.getItem('token');
        if (token) {
            options.headers['Authorization'] = `Bearer ${token}`;
        }

        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(endpoint, options);
        console.log('[makeRequest] Received response:', response);

        if (response.status === 204) {
            displayResponse({ message: 'Нет содержимого' }, 204);
            return null;
        }

        let data;
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = await response.text();
        }

        if (!response.ok) {
            const errorMsg = data.detail || data.message || `HTTP ошибка! статус: ${response.status}`;
            throw new Error(errorMsg);
        }

        displayResponse(data, response.status);
        return data;
    } catch (error) {
        console.error('[makeRequest] Error:', error);
        displayResponse({ 
            error: error.message,
            endpoint: endpoint,
            method: method
        }, error.status || 500);
        throw error;
    } finally {
        showLoading(false);
    }
}

// ==================== Функции аутентификации ====================
async function login() {
    const username = prompt('Введите имя пользователя');
    const password = prompt('Введите пароль');
    
    if (!username || !password) {
        displayResponse({ error: 'Требуется имя пользователя и пароль' });
        return;
    }

    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        formData.append('grant_type', 'password');

        const response = await fetch('/auth/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Ошибка входа');
        }

        localStorage.setItem('token', data.access_token);
        await getCurrentUser();
        displayResponse({ message: 'Вход выполнен успешно' });
    } catch (error) {
        console.error('[login] Error:', error);
        localStorage.removeItem('token');
        currentUser = null;
        updateAuthStatus();
        displayResponse({ error: error.message });
    }
}

async function register() {
    const username = prompt('Введите имя пользователя');
    const email = prompt('Введите email');
    const password = prompt('Введите пароль');
    
    if (!username || !password || !email) {
        displayResponse({ error: 'Все поля обязательны для заполнения' });
        return;
    }

    try {
        const data = await makeRequest('POST', '/auth/register', {
            username,
            email,
            password,
            role: 'user'
        });
        displayResponse({ message: 'Регистрация прошла успешно', user: data });
    } catch (error) {
        console.error('[register] Error:', error);
        displayResponse({ error: error.message });
    }
}

async function getCurrentUser() {
    try {
        const user = await makeRequest('GET', '/api/users/me');
        currentUser = user;
        updateAuthStatus();
        return user;
    } catch (error) {
        console.error('[getCurrentUser] Error:', error);
        localStorage.removeItem('token');
        currentUser = null;
        updateAuthStatus();
        throw error;
    }
}

function logout() {
    localStorage.removeItem('token');
    currentUser = null;
    updateAuthStatus();
    displayResponse({ message: 'Выход выполнен успешно' });
}

// ==================== Функции пользователя ====================
async function updateCurrentUser() {
    const email = prompt('Введите новый email');
    const password = prompt('Введите новый пароль');
    
    if (!email && !password) {
        displayResponse({ error: 'Необходимо обновить хотя бы одно поле' });
        return;
    }

    const updates = {};
    if (email) updates.email = email;
    if (password) updates.password = password;

    try {
        const data = await makeRequest('PUT', '/api/users/me', updates);
        currentUser = data;
        updateAuthStatus();
        displayResponse({ message: 'Профиль успешно обновлен', user: data });
    } catch (error) {
        console.error('[updateCurrentUser] Error:', error);
        displayResponse({ error: error.message });
    }
}

// ==================== Админские функции ====================
async function getAllUsers() {
    try {
        const users = await makeRequest('GET', '/api/admin/users');
        displayResponse(users);
    } catch (error) {
        console.error('[getAllUsers] Error:', error);
        displayResponse({ error: error.message });
    }
}

async function getUser() {
    const userId = document.getElementById('userId').value;
    if (!userId) {
        showError('user-id-error', 'Требуется ID пользователя');
        return;
    }
    clearError('user-id-error');

    try {
        const user = await makeRequest('GET', `/api/admin/users/${userId}`);
        displayResponse(user);
    } catch (error) {
        console.error('[getUser] Error:', error);
        displayResponse({ error: error.message });
    }
}

async function updateUser() {
    const userId = document.getElementById('userId').value;
    if (!userId) {
        showError('user-id-error', 'Требуется ID пользователя');
        return;
    }
    clearError('user-id-error');

    const username = prompt('Введите новое имя пользователя (оставьте пустым, чтобы пропустить)');
    const email = prompt('Введите новый email (оставьте пустым, чтобы пропустить)');
    const password = prompt('Введите новый пароль (оставьте пустым, чтобы пропустить)');
    const role = prompt('Введите новую роль (admin/moderator/user, оставьте пустым, чтобы пропустить)');

    const updates = {};
    if (username) updates.username = username;
    if (email) updates.email = email;
    if (password) updates.password = password;
    if (role) updates.role = role;

    if (Object.keys(updates).length === 0) {
        displayResponse({ error: 'Не указаны данные для обновления' });
        return;
    }

    try {
        const data = await makeRequest('PUT', `/api/admin/users/${userId}`, updates);
        displayResponse({ message: 'Пользователь успешно обновлен', user: data });
    } catch (error) {
        console.error('[updateUser] Error:', error);
        displayResponse({ error: error.message });
    }
}

async function deleteUser() {
    const userId = document.getElementById('userId').value;
    if (!userId) {
        showError('user-id-error', 'Требуется ID пользователя');
        return;
    }
    clearError('user-id-error');

    if (!confirm(`Вы уверены, что хотите удалить пользователя ${userId}?`)) {
        return;
    }

    try {
        const result = await makeRequest('DELETE', `/api/admin/users/${userId}`);
        displayResponse({ message: 'Пользователь успешно удален', result });
    } catch (error) {
        console.error('[deleteUser] Error:', error);
        displayResponse({ error: error.message });
    }
}

// ==================== Функции отзывов ====================
async function createFeedback() {
    const name = document.getElementById('feedbackName').value;
    const email = document.getElementById('feedbackEmail').value;
    const phone = document.getElementById('feedbackPhone').value;
    const message = document.getElementById('feedbackMessage').value;

    if (!name || !email || !message) {
        displayResponse({ error: 'Имя, email и сообщение обязательны для заполнения' });
        return;
    }

    try {
        const feedback = await makeRequest('POST', '/api/feedback/', {
            name,
            email,
            phone: phone || '',
            message
        });
        displayResponse({ message: 'Отзыв успешно создан', feedback });
        
        // Очищаем форму
        document.getElementById('feedbackName').value = '';
        document.getElementById('feedbackEmail').value = '';
        document.getElementById('feedbackPhone').value = '';
        document.getElementById('feedbackMessage').value = '';
    } catch (error) {
        console.error('[createFeedback] Error:', error);
        displayResponse({ error: error.message });
    }
}

async function getMyFeedbacks() {
    try {
        const feedbacks = await makeRequest('GET', '/api/feedback/');
        displayResponse(feedbacks);
    } catch (error) {
        console.error('[getMyFeedbacks] Error:', error);
        displayResponse({ error: error.message });
    }
}

async function getAllFeedbacks() {
    try {
        const feedbacks = await makeRequest('GET', '/api/moderator/feedbacks');
        displayResponse(feedbacks);
    } catch (error) {
        console.error('[getAllFeedbacks] Error:', error);
        displayResponse({ error: error.message });
    }
}

async function deleteFeedback() {
    const feedbackId = document.getElementById('feedbackId').value;
    if (!feedbackId) {
        showError('feedback-id-error', 'Требуется ID отзыва');
        return;
    }
    clearError('feedback-id-error');

    if (!confirm(`Вы уверены, что хотите удалить отзыв ${feedbackId}?`)) {
        return;
    }

    try {
        const result = await makeRequest('DELETE', `/api/feedback/${feedbackId}`);
        displayResponse({ message: 'Отзыв успешно удален', result });
    } catch (error) {
        console.error('[deleteFeedback] Error:', error);
        displayResponse({ error: error.message });
    }
}

// ==================== Системные функции ====================
async function healthCheck() {
    try {
        const status = await makeRequest('GET', '/api/health');
        displayResponse(status);
    } catch (error) {
        console.error('[healthCheck] Error:', error);
        displayResponse({ error: error.message });
    }
}

// ==================== Инициализация ====================
document.addEventListener('DOMContentLoaded', async () => {
    console.log('[init] Page loaded');
    
    if (localStorage.getItem('token')) {
        console.log('[init] Found token in localStorage, fetching current user');
        try {
            await getCurrentUser();
        } catch (error) {
            console.log('[init] Not authenticated');
        }
    }
    
    displayResponse({ 
        message: 'Система готова', 
        instructions: 'Используйте кнопки выше для взаимодействия с API',
        testData: {
            users: [
                {id: 1, name: "Тестовый пользователь 1"},
                {id: 2, name: "Тестовый пользователь 2"}
            ],
            timestamp: new Date().toISOString()
        }
    });
});