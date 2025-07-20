const API_BASE = ''; // Относительные пути (проксируются через Nginx)

// Улучшенный вывод ошибок
function displayResponse(data, statusCode = null) {
    const responseElement = document.getElementById('response');
    if (!responseElement) {
        console.error('Element #response not found');
        return;
    }
    
    const output = {
        timestamp: new Date().toISOString(),
        status: statusCode,
        data: data
    };
    responseElement.textContent = JSON.stringify(output, null, 2);
}

// Универсальный запрос с улучшенной обработкой ошибок
async function makeRequest(method, endpoint, body = null) {
    try {
        // Валидация endpoint
        if (!endpoint.startsWith('/')) {
            throw new Error('Endpoint must start with /');
        }

        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include' // Для куков, если используются
        };

        // Добавляем токен, если есть
        const token = localStorage.getItem('token');
        if (token) {
            options.headers.Authorization = `Bearer ${token}`;
        }

        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(endpoint, options);
        
        // Обработка пустого ответа (204 No Content)
        if (response.status === 204) {
            displayResponse({ message: 'No content' }, 204);
            return;
        }

        const data = await response.json().catch(() => null);

        if (!response.ok) {
            throw new Error(
                data?.detail || 
                data?.message || 
                `HTTP error! status: ${response.status}`
            );
        }

        displayResponse(data, response.status);
        return data;
    } catch (error) {
        console.error(`Request to ${endpoint} failed:`, error);
        displayResponse({ 
            error: error.message,
            endpoint: endpoint,
            method: method
        }, 500);
        throw error; // Пробрасываем для дальнейшей обработки
    }
}

// ==================== Auth Functions ====================
async function login() {
    const username = prompt('Enter username');
    const password = prompt('Enter password');
    
    if (!username || !password) {
        displayResponse({ error: 'Username and password are required' });
        return;
    }

    try {
        const data = await makeRequest('POST', '/auth/token', {
            username,
            password
        });
        
        if (data?.access_token) {
            localStorage.setItem('token', data.access_token);
            displayResponse({ message: 'Login successful' });
        }
    } catch (error) {
        localStorage.removeItem('token');
    }
}

async function register() {
    const user = {
        username: prompt('Enter username'),
        password: prompt('Enter password'),
        email: prompt('Enter email')
    };

    if (!user.username || !user.password) {
        displayResponse({ error: 'Username and password are required' });
        return;
    }

    await makeRequest('POST', '/auth/register', user);
}

// ==================== User Functions ====================
async function getCurrentUser() {
    try {
        const user = await makeRequest('GET', '/api/users/me');
        if (!user) {
            localStorage.removeItem('token');
        }
        return user;
    } catch (error) {
        localStorage.removeItem('token');
        throw error;
    }
}

// ==================== Admin Functions ====================
function getUserById() {
    const userId = document.getElementById('userId')?.value;
    if (!userId) {
        displayResponse({ error: 'User ID is required' });
        return;
    }
    makeRequest('GET', `/api/admin/users/${userId}`);
}

// ==================== Feedback Functions ====================
async function createFeedback() {
    const content = prompt('Enter feedback content');
    if (!content?.trim()) {
        displayResponse({ error: 'Content cannot be empty' });
        return;
    }
    await makeRequest('POST', '/api/feedback/', { content });
}

// Инициализация (если нужно)
document.addEventListener('DOMContentLoaded', () => {
    // Проверяем авторизацию при загрузке
    const token = localStorage.getItem('token');
    if (token) {
        getCurrentUser().catch(() => {});
    }
});