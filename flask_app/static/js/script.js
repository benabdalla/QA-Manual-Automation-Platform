  // Add some interactivity
    document.getElementById('testForm').addEventListener('submit', function(e) {
        // Show loading animation (you can remove this preventDefault for actual form submission)
        // e.preventDefault();
        document.getElementById('loading').style.display = 'block';
        document.querySelector('.submit-btn').style.opacity = '0.7';
        document.querySelector('.submit-btn').disabled = true;
    });

    // Add focus animations to inputs
    const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="number"]');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.02)';
        });

        input.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    });

    // Add hover effects to checkbox items
    document.querySelectorAll('.checkbox-item').forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.borderColor = '#667eea';
        });

        item.addEventListener('mouseleave', function() {
            this.style.borderColor = 'transparent';
        });
    });