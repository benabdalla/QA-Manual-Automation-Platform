// Authentication helper functions

function getAuthToken() {
    // Try to get token from localStorage first
    let token = localStorage.getItem('auth_token');
    
    // If not in localStorage, try sessionStorage
    if (!token) {
        token = sessionStorage.getItem('auth_token');
    }
    
    // If not in storage, try to get from cookie
    if (!token) {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'auth_token' || name === 'session_token') {
                token = value;
                break;
            }
        }
    }
    
    return token;
}

function isLoggedIn() {
    const token = getAuthToken();
    return token !== null && token !== '';
}

function getAuthHeaders() {
    const token = getAuthToken();
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
}

// Redirect to login if not authenticated
function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
        return false;
    }
    return true;
}

// Make authenticated API request
async function authFetch(url, options = {}) {
    const headers = getAuthHeaders();
    
    options.headers = {
        ...headers,
        ...(options.headers || {})
    };
    
    // Include credentials for cookie-based auth
    options.credentials = 'include';
    
    const response = await fetch(url, options);
    
    // If unauthorized, redirect to login
    if (response.status === 401) {
        window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
        throw new Error('Please login to continue');
    }
    
    return response;
}
