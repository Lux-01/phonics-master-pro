/**
 * Bean & Bloom Coffee Roasters
 * Main JavaScript File
 */

// Cart State
let cart = JSON.parse(localStorage.getItem('beanBloomCart')) || [];

// Stripe Configuration (TEST MODE - Replace with your own keys)
const STRIPE_PUBLIC_KEY = 'pk_test_51Hxxxxxxxxxxxxxxxxxxxxxxxxxx'; // Replace with your Stripe test key

// Product Database
const products = {
    'ethiopian-yirgacheffe': { name: 'Ethiopian Yirgacheffe', price: 2400 },
    'kenyan-aa': { name: 'Kenyan AA', price: 2600 },
    'colombian-supremo': { name: 'Colombian Supremo', price: 2200 },
    'guatemalan-antigua': { name: 'Guatemalan Antigua', price: 2300 },
    'sumatra-mandheling': { name: 'Sumatra Mandheling', price: 2600 },
    'french-roast': { name: 'French Roast', price: 2000 },
    'house-blend': { name: 'House Blend', price: 2100 },
    'espresso-blend': { name: 'Espresso Blend', price: 2300 },
    'ethiopian-hero': { name: 'Ethiopian Yirgacheffe', price: 2400 },
    'colombian-hero': { name: 'Colombian Supremo', price: 2200 },
    'sumatra-hero': { name: 'Sumatra Mandheling', price: 2600 }
};

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Cart UI
    updateCartUI();
    
    // Mobile Navigation
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    
    if (hamburger) {
        hamburger.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            hamburger.classList.toggle('active');
        });
    }
    
    // Cart Toggle
    const cartIcon = document.querySelector('.cart-icon');
    const cartDrawer = document.querySelector('.cart-drawer');
    const cartOverlay = document.querySelector('.cart-overlay');
    const closeCart = document.querySelector('.close-cart');
    
    function openCart() {
        cartDrawer.classList.add('open');
        cartOverlay.classList.add('open');
        document.body.style.overflow = 'hidden';
    }
    
    function closeCartFn() {
        cartDrawer.classList.remove('open');
        cartOverlay.classList.remove('open');
        document.body.style.overflow = '';
    }
    
    if (cartIcon) cartIcon.addEventListener('click', openCart);
    if (closeCart) closeCart.addEventListener('click', closeCartFn);
    if (cartOverlay) cartOverlay.addEventListener('click', closeCartFn);
    
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // Add to Cart button functionality
    document.querySelectorAll('.btn-add').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const productCard = this.closest('.product-card');
            const productId = productCard.dataset.productId;
            
            if (productId && products[productId]) {
                addToCart(productId);
                
                // Visual feedback
                const originalText = this.textContent;
                this.textContent = '✓ Added';
                this.style.background = '#2D6A4F';
                this.style.color = 'white';
                
                setTimeout(() => {
                    this.textContent = originalText;
                    this.style.background = '';
                    this.style.color = '';
                }, 1500);
            }
        });
    });
    
    // Checkout button
    const checkoutBtn = document.getElementById('checkout-btn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', initiateCheckout);
    }}
    
    // Newsletter form
    const newsletterForm = document.querySelector('.newsletter-form');
    
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const emailInput = this.querySelector('input[type="email"]');
            const submitBtn = this.querySelector('button');
            
            if (emailInput.value) {
                submitBtn.textContent = 'Subscribed!';
                submitBtn.style.background = '#2D6A4F';
                emailInput.value = '';
                
                setTimeout(() => {
                    submitBtn.textContent = 'Subscribe';
                    submitBtn.style.background = '';
                }, 3000);
            }
        });
    }
});

// Cart Functions
function addToCart(productId) {
    const existingItem = cart.find(item => item.id === productId);
    
    if (existingItem) {
        existingItem.qty += 1;
    } else {
        cart.push({
            id: productId,
            name: products[productId].name,
            price: products[productId].price,
            qty: 1
        });
    }
    
    saveCart();
    updateCartUI();
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    saveCart();
    updateCartUI();
}

function updateQuantity(productId, change) {
    const item = cart.find(item => item.id === productId);
    if (item) {
        item.qty += change;
        if (item.qty <= 0) {
            removeFromCart(productId);
        } else {
            saveCart();
            updateCartUI();
        }
    }
}

function saveCart() {
    localStorage.setItem('beanBloomCart', JSON.stringify(cart));
}

function updateCartUI() {
    const cartCount = document.querySelector('.cart-count');
    const cartItems = document.querySelector('.cart-items');
    const cartTotal = document.querySelector('.cart-total-amount');
    const emptyCart = document.querySelector('.empty-cart');
    const checkoutBtn = document.getElementById('checkout-btn');
    
    // Update cart count
    const totalItems = cart.reduce((sum, item) => sum + item.qty, 0);
    if (cartCount) {
        cartCount.textContent = totalItems;
        cartCount.style.display = totalItems > 0 ? 'flex' : 'none';
    }
    
    // Update cart drawer items
    if (cartItems) {
        if (cart.length === 0) {
            cartItems.innerHTML = '';
            if (emptyCart) emptyCart.style.display = 'block';
            if (checkoutBtn) checkoutBtn.disabled = true;
        } else {
            if (emptyCart) emptyCart.style.display = 'none';
            if (checkoutBtn) checkoutBtn.disabled = false;
            
            cartItems.innerHTML = cart.map(item => `
                <div class="cart-item">
                    <div class="cart-item-info">
                        <h4>${item.name}</h4>
                        <p class="cart-item-price">$${(item.price / 100).toFixed(2)}</p>
                    </div>
                    <div class="cart-item-actions">
                        <div class="quantity-controls">
                            <button onclick="updateQuantity('${item.id}', -1)" class="qty-btn">−</button>
                            <span class="qty-display">${item.qty}</span>
                            <button onclick="updateQuantity('${item.id}', 1)" class="qty-btn">+</button>
                        </div>
                        <button onclick="removeFromCart('${item.id}')" class="remove-btn">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `).join('');
        }
    }
    
    // Update total
    const total = cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
    if (cartTotal) {
        cartTotal.textContent = `$${(total / 100).toFixed(2)}`;
    }
}

// Stripe Checkout
async function initiateCheckout() {
    if (cart.length === 0) return;
    
    const checkoutBtn = document.getElementById('checkout-btn');
    checkoutBtn.disabled = true;
    checkoutBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    
    // For demo purposes, we'll show what the checkout would look like
    // In production, this would call your backend to create a Stripe session
    
    /*
    // Real Stripe integration would look like:
    const response = await fetch('/create-checkout-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            items: cart.map(item => ({
                name: item.name,
                amount: item.price,
                quantity: item.qty
            })),
            success_url: window.location.origin + '/success.html',
            cancel_url: window.location.origin + '/menu.html'
        })
    });
    
    const { sessionId } = await response.json();
    const stripe = Stripe(STRIPE_PUBLIC_KEY);
    await stripe.redirectToCheckout({ sessionId });
    */
    
    // Demo: Show checkout modal
    setTimeout(() => {
        alert(`Demo Checkout\n\nItems:\n${cart.map(i => `${i.name} x${i.qty} - $${((i.price * i.qty) / 100).toFixed(2)}`).join('\n')}\n\nTotal: $${(cart.reduce((s, i) => s + (i.price * i.qty), 0) / 100).toFixed(2)}\n\nIn production, this would redirect to Stripe Checkout`);
        
        checkoutBtn.disabled = false;
        checkoutBtn.innerHTML = 'Checkout <i class="fas fa-arrow-right"></i>';
    }, 500);
}

// Example Stripe backend (for reference - would go in a server file)
/*
// Node.js/Express backend example:
const stripe = require('stripe')('sk_test_your_secret_key');

app.post('/create-checkout-session', async (req, res) => {
    const session = await stripe.checkout.sessions.create({
        payment_method_types: ['card'],
        line_items: req.body.items.map(item => ({
            price_data: {
                currency: 'usd',
                product_data: { name: item.name },
                unit_amount: item.amount,
            },
            quantity: item.quantity,
        })),
        mode: 'payment',
        success_url: req.body.success_url,
        cancel_url: req.body.cancel_url,
    });
    
    res.json({ sessionId: session.id });
});
*/
    
    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.feature-card, .product-card, .testimonial-card').forEach(el => {
        observer.observe(el);
    });
});

// CSS Animation class
const style = document.createElement('style');
style.textContent = `
    .fade-in-up {
        animation: fadeInUp 0.8s ease forwards;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);
