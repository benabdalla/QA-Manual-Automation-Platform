/**
 * Main JavaScript file for Ines QA Platform
 */

// Utility Functions
const utils = {
    /**
     * Make API call
     */
    async apiCall(endpoint, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        const mergedOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(endpoint, mergedOptions);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'API request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            showNotification(error.message, 'error');
            throw error;
        }
    },
    
    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        const alertClass = type === 'error' ? 'danger' : type;
        const icon = type === 'error' ? 'exclamation-circle' : type === 'success' ? 'check-circle' : 'info-circle';
        
        const alertHtml = `
            <div class="alert alert-${alertClass} alert-dismissible fade show" role="alert">
                <i class="fas fa-${icon}"></i> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const alertContainer = document.querySelector('.container');
        if (alertContainer) {
            const alertDiv = document.createElement('div');
            alertDiv.innerHTML = alertHtml;
            alertContainer.insertBefore(alertDiv.firstElementChild, alertContainer.firstChild);
        }
    },
    
    /**
     * Format date
     */
    formatDate(date, format = 'short') {
        const options = format === 'short' 
            ? { year: 'numeric', month: 'short', day: 'numeric' }
            : { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
        
        return new Date(date).toLocaleDateString('en-US', options);
    }
};

// Configuration Management
const configs = {
    /**
     * Get all configurations
     */
    async getConfigs(type = 'agent') {
        return utils.apiCall(`/api/configs?type=${type}`);
    },
    
    /**
     * Save configuration
     */
    async saveConfig(name, type, configData, description = '') {
        return utils.apiCall('/api/configs', {
            method: 'POST',
            body: JSON.stringify({
                name,
                type,
                config_data: configData,
                description
            })
        });
    },
    
    /**
     * Update configuration
     */
    async updateConfig(configId, updates) {
        return utils.apiCall(`/api/configs/${configId}`, {
            method: 'PUT',
            body: JSON.stringify(updates)
        });
    },
    
    /**
     * Delete configuration
     */
    async deleteConfig(configId) {
        return utils.apiCall(`/api/configs/${configId}`, {
            method: 'DELETE'
        });
    }
};

// Agent Management
const agents = {
    /**
     * Run agent
     */
    async runAgent(configId) {
        return utils.apiCall('/api/run-agent', {
            method: 'POST',
            body: JSON.stringify({ config_id: configId })
        });
    },
    
    /**
     * Get agent status
     */
    async getStatus(agentId) {
        return utils.apiCall(`/api/agent-status/${agentId}`);
    }
};

// API Key Management
const apiKeys = {
    /**
     * Get all API keys
     */
    async getKeys() {
        return utils.apiCall('/api/api-keys');
    },
    
    /**
     * Create new API key
     */
    async createKey(name, value, type = 'api_key') {
        return utils.apiCall('/api/api-keys', {
            method: 'POST',
            body: JSON.stringify({
                name,
                key_value: value,
                key_type: type
            })
        });
    },
    
    /**
     * Delete API key
     */
    async deleteKey(keyId) {
        return utils.apiCall(`/api/api-keys/${keyId}`, {
            method: 'DELETE'
        });
    }
};

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize popovers
    initializePopovers();
    
    // Add animation to cards
    animateElements();
    
    // Setup event listeners
    setupEventListeners();
}

function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function initializePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

function animateElements() {
    const elements = document.querySelectorAll('.card, .btn, .alert');
    elements.forEach((el, index) => {
        el.style.animation = `slideIn 0.5s ease-out ${index * 0.1}s both`;
    });
}

function setupEventListeners() {
    // Auto-hide alerts after 5 seconds
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Export for use in other scripts
window.utils = utils;
window.configs = configs;
window.agents = agents;
window.apiKeys = apiKeys;

// Notification shortcuts
const showNotification = utils.showNotification;
const apiCall = utils.apiCall;
