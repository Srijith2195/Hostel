// Sidebar toggle functionality
document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    
    // Toggle sidebar
    sidebarCollapse.addEventListener('click', function () {
        sidebar.classList.toggle('active');
        
        // Adjust content width
        if (sidebar.classList.contains('active')) {
            content.style.width = '100%';
        } else {
            content.style.width = 'calc(100% - 250px)';
        }
    });
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function (event) {
        const isClickInsideSidebar = sidebar.contains(event.target);
        const isClickInsideToggle = sidebarCollapse.contains(event.target);
        
        if (!isClickInsideSidebar && !isClickInsideToggle && 
            window.innerWidth < 768 && !sidebar.classList.contains('active')) {
            sidebar.classList.add('active');
            content.style.width = '100%';
        }
    });
    
    // Handle dropdown toggles
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    dropdownToggles.forEach(function (toggle) {
        toggle.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(toggle.getAttribute('href'));
            target.classList.toggle('show');
        });
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        let isValid = true;
        
        // Check required fields
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(function (field) {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    }
    return true;
}

// Confirmation dialog for delete actions
function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Search functionality
function initSearch(searchInputId, tableId) {
    const searchInput = document.getElementById(searchInputId);
    const table = document.getElementById(tableId);
    
    if (searchInput && table) {
        searchInput.addEventListener('keyup', function () {
            const searchTerm = searchInput.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(function (row) {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    }
}