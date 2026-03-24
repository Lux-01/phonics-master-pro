/**
 * RESTORED RIGHT SYDNEY - MAIN.JS
 * Mobile Navigation, Smooth Scroll, Form Validation, Interactions
 */

(function() {
    'use strict';

    // ========================================
    // DOM Elements
    // ========================================
    const navToggle = document.querySelector('.nav-toggle');
    const nav = document.querySelector('.nav');
    const navOverlay = document.querySelector('.nav-overlay');
    const header = document.querySelector('.header');
    const navLinks = document.querySelectorAll('.nav-list a');
    const forms = document.querySelectorAll('form[data-validate]');
    const lazyImages = document.querySelectorAll('img[data-src]');
    const sections = document.querySelectorAll('section[id]');

    // ========================================
    // Mobile Navigation
    // ========================================
    function toggleNav() {
        navToggle.classList.toggle('active');
        nav.classList.toggle('active');
        navOverlay.classList.toggle('active');
        document.body.style.overflow = nav.classList.contains('active') ? 'hidden' : '';
    }

    function closeNav() {
        navToggle.classList.remove('active');
        nav.classList.remove('active');
        navOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (navToggle) {
        navToggle.addEventListener('click', toggleNav);
    }

    if (navOverlay) {
        navOverlay.addEventListener('click', closeNav);
    }

    // Close nav when clicking a link
    navLinks.forEach(link => {
        link.addEventListener('click', closeNav);
    });

    // Close nav on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && nav.classList.contains('active')) {
            closeNav();
        }
    });

    // ========================================
    // Sticky Header
    // ========================================
    let lastScroll = 0;

    function updateHeader() {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }

        lastScroll = currentScroll;
    }

    // Throttled scroll handler
    let ticking = false;
    window.addEventListener('scroll', () => {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                updateHeader();
                ticking = false;
            });
            ticking = true;
        }
    }, { passive: true });

    // ========================================
    // Active Navigation Link
    // ========================================
    function updateActiveLink() {
        const scrollPos = window.scrollY + 150;

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');

            if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }

    window.addEventListener('scroll', updateActiveLink, { passive: true });

    // ========================================
    // Smooth Scroll for Anchor Links
    // ========================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                const headerOffset = 80;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // ========================================
    // Form Validation
    // ========================================
    const validators = {
        required: (value) => value.trim() !== '',
        email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
        phone: (value) => /^[\d\s\-\+\(\)]{8,}$/.test(value),
        minLength: (value, length) => value.length >= parseInt(length),
        maxLength: (value, length) => value.length <= parseInt(length)
    };

    function validateField(field) {
        const value = field.value;
        const rules = field.dataset.validate?.split('|') || [];
        let isValid = true;
        let errorMessage = '';

        // Check required
        if (field.required && !validators.required(value)) {
            isValid = false;
            errorMessage = 'This field is required';
        }

        // Check email
        if (isValid && field.type === 'email' && value && !validators.email(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address';
        }

        // Check phone
        if (isValid && field.type === 'tel' && value && !validators.phone(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid phone number';
        }

        // Check min length
        if (isValid && field.dataset.minLength && !validators.minLength(value, field.dataset.minLength)) {
            isValid = false;
            errorMessage = `Minimum ${field.dataset.minLength} characters required`;
        }

        // Update field state
        const formGroup = field.closest('.form-group');
        const errorElement = formGroup?.querySelector('.error-message');

        if (isValid) {
            field.classList.remove('error');
            if (errorElement) {
                errorElement.classList.remove('visible');
            }
        } else {
            field.classList.add('error');
            if (errorElement) {
                errorElement.textContent = errorMessage;
                errorElement.classList.add('visible');
            }
        }

        return isValid;
    }

    function validateForm(form) {
        const fields = form.querySelectorAll('[data-validate], [required]');
        let isFormValid = true;

        fields.forEach(field => {
            if (!validateField(field)) {
                isFormValid = false;
            }
        });

        return isFormValid;
    }

    // Attach validation to forms
    forms.forEach(form => {
        const fields = form.querySelectorAll('[data-validate], [required]');

        // Validate on blur
        fields.forEach(field => {
            field.addEventListener('blur', () => validateField(field));
            field.addEventListener('input', () => {
                if (field.classList.contains('error')) {
                    validateField(field);
                }
            });
        });

        // Validate on submit
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                // Focus first error
                const firstError = this.querySelector('.error');
                if (firstError) {
                    firstError.focus();
                }
            } else {
                // Show success message
                const submitBtn = this.querySelector('button[type="submit"]');
                if (submitBtn) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> Sending...';
                    submitBtn.disabled = true;

                    // For demo/simulation - re-enable after 2s
                    setTimeout(() => {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }, 2000);
                }
            }
        });
    });

    // ========================================
    // Lazy Loading Images
    // ========================================
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        img.classList.add('loaded');
                    }
                    observer.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px 0px',
            threshold: 0.01
        });

        lazyImages.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for older browsers
        lazyImages.forEach(img => {
            if (img.dataset.src) {
                img.src = img.dataset.src;
            }
        });
    }

    // ========================================
    // Emergency Button Click Handler
    // ========================================
    document.querySelectorAll('a[href^="tel:"]').forEach(link => {
        link.addEventListener('click', function(e) {
            // Track emergency call clicks (for analytics)
            if (window.gtag) {
                gtag('event', 'click', {
                    'event_category': 'Emergency',
                    'event_label': 'Phone Call'
                });
            }
        });
    });

    // ========================================
    // Form Character Counter (for textarea)
    // ========================================
    document.querySelectorAll('textarea[data-max]').forEach(textarea => {
        const max = parseInt(textarea.dataset.max);
        const counter = document.createElement('div');
        counter.className = 'char-counter';
        counter.style.cssText = 'text-align: right; font-size: 0.75rem; color: var(--text-light); margin-top: 0.25rem;';
        textarea.parentNode.appendChild(counter);

        function updateCounter() {
            const remaining = max - textarea.value.length;
            counter.textContent = `${remaining} characters remaining`;
            counter.style.color = remaining < 20 ? 'var(--accent-red)' : 'var(--text-light)';
        }

        textarea.addEventListener('input', updateCounter);
        updateCounter();
    });

    // ========================================
    // Service Card Interactions
    // ========================================
    document.querySelectorAll('.service-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });

    // ========================================
    // Gallery Lightbox (Simple Implementation)
    // ========================================
    const galleryItems = document.querySelectorAll('.gallery-item');
    
    if (galleryItems.length > 0) {
        // Create lightbox elements
        const lightbox = document.createElement('div');
        lightbox.className = 'lightbox';
        lightbox.innerHTML = `
            <div class="lightbox-content">
                <button class="lightbox-close" aria-label="Close">&times;</button>
                <img src="" alt="Gallery Image">
                <div class="lightbox-caption"></div>
            </div>
        `;
        
        // Add lightbox styles
        const lightboxStyles = document.createElement('style');
        lightboxStyles.textContent = `
            .lightbox {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.95);
                z-index: 10000;
                display: none;
                align-items: center;
                justify-content: center;
                padding: 2rem;
            }
            .lightbox.active { display: flex; }
            .lightbox-content { position: relative; max-width: 90vw; max-height: 90vh; }
            .lightbox img { max-width: 100%; max-height: 85vh; object-fit: contain; border-radius: 8px; }
            .lightbox-close {
                position: absolute;
                top: -40px;
                right: 0;
                background: none;
                border: none;
                color: white;
                font-size: 2rem;
                cursor: pointer;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .lightbox-caption {
                color: white;
                text-align: center;
                margin-top: 1rem;
                font-size: 1.125rem;
            }
        `;
        document.head.appendChild(lightboxStyles);
        document.body.appendChild(lightbox);

        const lightboxImg = lightbox.querySelector('img');
        const lightboxCaption = lightbox.querySelector('.lightbox-caption');
        const lightboxClose = lightbox.querySelector('.lightbox-close');

        galleryItems.forEach(item => {
            item.addEventListener('click', function() {
                const img = this.querySelector('img');
                const overlay = this.querySelector('.gallery-overlay');
                
                lightboxImg.src = img.src;
                lightboxCaption.textContent = overlay ? overlay.textContent.trim() : '';
                lightbox.classList.add('active');
                document.body.style.overflow = 'hidden';
            });
        });

        function closeLightbox() {
            lightbox.classList.remove('active');
            document.body.style.overflow = '';
        }

        lightboxClose.addEventListener('click', closeLightbox);
        lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox) closeLightbox();
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && lightbox.classList.contains('active')) {
                closeLightbox();
            }
        });
    }

    // ========================================
    // Scroll Reveal Animation
    // ========================================
    function revealOnScroll() {
        const reveals = document.querySelectorAll('.reveal');
        
        reveals.forEach(element => {
            const windowHeight = window.innerHeight;
            const elementTop = element.getBoundingClientRect().top;
            const elementVisible = 150;

            if (elementTop < windowHeight - elementVisible) {
                element.classList.add('revealed');
            }
        });
    }

    // Add reveal class to elements
    document.querySelectorAll('.service-card, .trust-card, .testimonial-card, .gallery-item').forEach(el => {
        el.classList.add('reveal');
    });

    // Add reveal styles
    const revealStyles = document.createElement('style');
    revealStyles.textContent = `
        .reveal {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        .reveal.revealed {
            opacity: 1;
            transform: translateY(0);
        }
    `;
    document.head.appendChild(revealStyles);

    window.addEventListener('scroll', revealOnScroll, { passive: true });
    revealOnScroll(); // Initial check

    // ========================================
    // Preload Critical Images
    // ========================================
    function preloadImage(src) {
        const img = new Image();
        img.src = src;
    }

    // Preload hero image and logo
    const heroImage = document.querySelector('.hero-bg img');
    if (heroImage) preloadImage(heroImage.src);

    const logoImage = document.querySelector('.logo img');
    if (logoImage) preloadImage(logoImage.src);

    // ========================================
    // Performance: Debounce function
    // ========================================
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Apply debounced resize handler
    const debouncedResize = debounce(() => {
        // Recalculate positions if needed
        updateActiveLink();
    }, 250);

    window.addEventListener('resize', debouncedResize);

    // ========================================
    // Service Worker Registration (PWA ready)
    // ========================================
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            // Uncomment when service worker is available
            // navigator.serviceWorker.register('/sw.js');
        });
    }

    // ========================================
    // Console Welcome Message
    // ========================================
    console.log('%c Restored Right Sydney ', 'background: #1a5276; color: white; font-size: 24px; padding: 10px; border-radius: 8px;');
    console.log('%c Emergency Flood Restoration Services - Sydney Wide ', 'color: #1a5276; font-size: 14px;');
    console.log('%c 24/7 Emergency Hotline: 0488 851 951 ', 'background: #c0392b; color: white; font-size: 16px; padding: 5px 10px; border-radius: 4px;');

})();
