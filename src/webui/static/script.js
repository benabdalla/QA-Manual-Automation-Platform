// ============ Dark Mode & Theme Toggle ============
function setupThemeToggle() {
    // Initialize dark mode from localStorage
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
    }

    // Create and add dark mode toggle button if not exists
    if (!document.querySelector('.theme-toggle')) {
        const themeToggle = document.createElement('button');
        themeToggle.className = 'theme-toggle';
        themeToggle.innerHTML = isDarkMode ? '🌙' : '☀️';
        themeToggle.title = isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode';
        
        themeToggle.addEventListener('click', function(e) {
            e.preventDefault();
            const isCurrentlyDark = document.body.classList.contains('dark-mode');
            
            if (isCurrentlyDark) {
                document.body.classList.remove('dark-mode');
                themeToggle.innerHTML = '☀️';
                themeToggle.title = 'Switch to Dark Mode';
                localStorage.setItem('darkMode', 'false');
            } else {
                document.body.classList.add('dark-mode');
                themeToggle.innerHTML = '🌙';
                themeToggle.title = 'Switch to Light Mode';
                localStorage.setItem('darkMode', 'true');
            }
        });
        
        document.body.appendChild(themeToggle);
    }
}

// ============ Smooth Entrance Animations ============
function setupAnimations() {
    const elements = document.querySelectorAll('.group, .tabs, .auth-container, .header-text');
    elements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        setTimeout(() => {
            el.style.transition = 'opacity 0.6s cubic-bezier(0.4, 0, 0.2, 1), transform 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 80);
    });
}

// ============ Button Hover Ripple Effect ============
function setupButtonEffects() {
    document.querySelectorAll('button').forEach(button => {
        if (button.classList.contains('theme-toggle')) return;
        
        button.addEventListener('mouseenter', function() {
            this.style.filter = 'brightness(1.05)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.filter = 'brightness(1)';
        });
    });
}

// ============ Focus Management ============
function setupFocusManagement() {
    document.querySelectorAll('input, select, textarea, button').forEach(element => {
        element.addEventListener('focus', function() {
            this.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
        });
        
        element.addEventListener('blur', function() {
            this.style.boxShadow = '';
        });
    });
}

// ============ Initialize Everything on Page Load ============
function refresh() {
    // Set light theme as default
    const url = new URL(window.location);
    if (url.searchParams.get('__theme') !== 'light') {
        url.searchParams.set('__theme', 'light');
        window.location.href = url.href;
    }
}

// ============ Main Initialization ============
document.addEventListener('DOMContentLoaded', function() {
    setupThemeToggle();
    setupAnimations();
    setupButtonEffects();
    setupFocusManagement();
});

// Also run on dynamic content updates
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.addedNodes.length) {
            setupButtonEffects();
            setupFocusManagement();
        }
    });
});

observer.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: false
});
