/*
   UI Interactions and Accessibility
   Handles alerts, hamburger menu, keyboard navigation, and micro-interactions
*/

(function() {
    'use strict';

    // Initialize hamburger menu
    initializeHamburgerMenu();
    
    // Initialize alert close buttons
    initializeAlerts();

    function initializeHamburgerMenu() {
        const hamburger = document.getElementById('hamburgerBtn');
        const navMenu = document.getElementById('navMenu');

        if (!hamburger || !navMenu) return;

        hamburger.addEventListener('click', () => {
            const isExpanded = hamburger.getAttribute('aria-expanded') === 'true';
            hamburger.setAttribute('aria-expanded', !isExpanded);
            navMenu.classList.toggle('mobile-open');
        });

        // Close menu when a link is clicked
        navMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                hamburger.setAttribute('aria-expanded', 'false');
                navMenu.classList.remove('mobile-open');
            });
        });

        // Close menu on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                hamburger.setAttribute('aria-expanded', 'false');
                navMenu.classList.remove('mobile-open');
            }
        });
    }

    function initializeAlerts() {
        const alerts = document.querySelectorAll('.alert');

        alerts.forEach(alert => {
            const closeBtn = alert.querySelector('.alert-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    alert.style.display = 'none';
                });
            }

            // Auto-dismiss error alerts after 5 seconds if user hasn't interacted
            if (alert.classList.contains('alert-error')) {
                setTimeout(() => {
                    if (alert.style.display !== 'none' && !alert.dataset.userInteracted) {
                        alert.style.display = 'none';
                    }
                }, 5000);

                // Track user interaction
                alert.addEventListener('mouseenter', () => {
                    alert.dataset.userInteracted = 'true';
                });
            }
        });

        // Close alerts with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const visibleAlerts = document.querySelectorAll('.alert[style*="display: block"]');
                visibleAlerts.forEach(alert => {
                    alert.style.display = 'none';
                });
            }
        });
    }

    // Button active state feedback
    document.addEventListener('click', (e) => {
        if (e.target.tagName === 'BUTTON') {
            e.target.style.transform = 'scale(0.98)';
            setTimeout(() => {
                e.target.style.transform = 'scale(1)';
            }, 100);
        }
    });

    // Keyboard navigation for forms
    const formInputs = document.querySelectorAll('input, select, textarea, button');
    formInputs.forEach((input, index) => {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                // Tab moves to next element (browser default)
                return;
            }
            if (e.shiftKey && e.key === 'Tab') {
                // Shift+Tab moves to previous element (browser default)
                return;
            }
        });
    });

    // Skip to main content link (for accessibility)
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.style.position = 'absolute';
    skipLink.style.top = '-40px';
    skipLink.style.left = '0';
    skipLink.style.background = '#000';
    skipLink.style.color = '#fff';
    skipLink.style.padding = '8px 12px';
    skipLink.style.zIndex = '9999';
    skipLink.addEventListener('focus', () => {
        skipLink.style.top = '0';
    });
    skipLink.addEventListener('blur', () => {
        skipLink.style.top = '-40px';
    });

    // Accessibility: Focus management
    document.addEventListener('keydown', (e) => {
        // Handle Enter key on form submission
        if (e.key === 'Enter' && e.target.tagName === 'BUTTON' && e.target.type === 'submit') {
            e.target.form.dispatchEvent(new Event('submit'));
        }

        // Handle Space key on buttons
        if (e.key === ' ' && e.target.tagName === 'BUTTON') {
            e.preventDefault();
            e.target.click();
        }
    });

})();
