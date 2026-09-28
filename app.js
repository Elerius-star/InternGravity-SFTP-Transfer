// ============================================
// AKWA IBOM STATE E-COMMERCE PLATFORM
// Main JavaScript File
// ============================================

// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';
let authToken = localStorage.getItem('access_token');

// ============================================
// LOADING OVERLAY MANAGEMENT WITH SAFETY TIMEOUT
// ============================================

// Safety timeout to force hide loading overlay (prevents infinite spinning)
const LOADING_TIMEOUT = 8000; // 8 seconds max

let loadingTimer = null;

function clearLoadingTimer() {
    if (loadingTimer) {
        clearTimeout(loadingTimer);
        loadingTimer = null;
    }
}

function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'flex';
        
        // Clear any existing timer
        clearLoadingTimer();
        
        // Set safety timeout to force hide loading
        loadingTimer = setTimeout(() => {
            console.warn('⚠️ Loading timeout reached - forcing hide');
            hideLoading();
            showNotification('Connection timeout - please refresh', 'warning');
        }, LOADING_TIMEOUT);
    }
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
        clearLoadingTimer();
    }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function showNotification(message, type = 'info') {
    // Remove any existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(n => n.remove());
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.zIndex = '10000';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

function formatCurrency(amount) {
    if (amount === undefined || amount === null) return '₦0.00';
    return '₦' + Number(amount).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}

function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
    };
}

// Safe fetch with timeout and error handling
async function safeFetch(url, options = {}, timeout = 10000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        return response;
    } catch (error) {
        clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
            throw new Error('Request timeout - server not responding');
        }
        throw error;
    }
}

// ============================================
// HERO IMAGE CHECK FUNCTION - INTEGRATED
// ============================================
function checkHeroImage() {
    const heroSection = document.querySelector('.hero');
    if (!heroSection) return;
    
    const img = new Image();
    img.src = 'images/hero-bg.jpg';
    
    img.onload = function() {
        console.log('✅ Hero image loaded successfully from: images/hero-bg.jpg');
        heroSection.classList.remove('image-failed');
        
        // Ensure the background is set correctly
        heroSection.style.background = `linear-gradient(135deg, rgba(128, 0, 128, 0.8), rgba(139, 0, 0, 0.8)), url('images/hero-bg.jpg')`;
        heroSection.style.backgroundSize = 'cover';
        heroSection.style.backgroundPosition = 'center';
    };
    
    img.onerror = function() {
        console.warn('⚠️ Hero image failed to load from: images/hero-bg.jpg');
        console.warn('📁 Expected path: C:\\Users\\USER-PC\\.vscode\\Frontendfull3\\images\\hero-bg.jpg');
        
        // Add fallback class to show gradient only
        heroSection.classList.add('image-failed');
        
        // Try alternative paths
        tryAlternativeHeroPaths();
    };
}

// Try alternative paths for hero image
function tryAlternativeHeroPaths() {
    const heroSection = document.querySelector('.hero');
    if (!heroSection) return;
    
    const alternativePaths = [
        'images/here-bg.jpg',
        './images/hero-bg.jpg',
        '/images/hero-bg.jpg',
        '../images/hero-bg.jpg',
        'images/hero-bg.png',
        'images/hero.jpg'
    ];
    
    let foundPath = false;
    
    alternativePaths.forEach(path => {
        const img = new Image();
        img.src = path;
        
        img.onload = function() {
            if (!foundPath) {
                foundPath = true;
                console.log(`✅ Hero image found at alternative path: ${path}`);
                // Update the background with the working path
                heroSection.style.background = `linear-gradient(135deg, rgba(128, 0, 128, 0.8), rgba(139, 0, 0, 0.8)), url('${path}')`;
                heroSection.style.backgroundSize = 'cover';
                heroSection.style.backgroundPosition = 'center';
                heroSection.classList.remove('image-failed');
                
                // Show success message
                showNotification('Hero image loaded successfully!', 'success');
            }
        };
    });
    
    // If no image found after 2 seconds, just keep the gradient
    setTimeout(() => {
        if (!foundPath) {
            console.warn('⚠️ No hero image found in any location. Using gradient only.');
            heroSection.style.background = 'linear-gradient(135deg, var(--primary-purple), var(--primary-red))';
        }
    }, 2000);
}

// ============================================
// AUTHENTICATION
// ============================================

// Login function
async function login(username, password) {
    try {
        showLoading();
        
        if (!username || !password) {
            showNotification('Please enter username and password', 'warning');
            hideLoading();
            return;
        }
        
        const response = await safeFetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            showNotification('Login successful!', 'success');
            
            // Redirect based on user role
            setTimeout(() => {
                if (data.user.is_admin) {
                    window.location.href = 'dashboard.html';
                } else {
                    window.location.href = 'shop.html';
                }
            }, 500);
        } else {
            showNotification(data.error || 'Login failed', 'error');
            hideLoading();
        }
    } catch (error) {
        console.error('Login error:', error);
        let errorMsg = 'Connection error';
        if (error.message.includes('timeout')) {
            errorMsg = 'Server timeout - please try again';
        } else if (error.message.includes('Failed to fetch')) {
            errorMsg = 'Cannot connect to server - is backend running?';
        }
        showNotification(errorMsg, 'error');
        hideLoading();
    }
}

// Register function
async function register(userData) {
    try {
        showLoading();
        
        // Validate required fields
        const required = ['username', 'email', 'password', 'full_name', 'phone'];
        for (let field of required) {
            if (!userData[field]) {
                showNotification(`${field} is required`, 'warning');
                hideLoading();
                return;
            }
        }
        
        const response = await safeFetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Registration successful! Please login.', 'success');
            // Switch to login tab
            const loginTab = document.querySelector('[data-tab="login"]');
            if (loginTab) loginTab.click();
        } else {
            showNotification(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showNotification('Connection error - please try again', 'error');
    } finally {
        hideLoading();
    }
}

// Logout function
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    localStorage.removeItem('cart');
    showNotification('Logged out successfully', 'info');
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 500);
}

// Check if user is logged in
function isLoggedIn() {
    return !!localStorage.getItem('access_token');
}

// Get current user
function getCurrentUser() {
    try {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    } catch (e) {
        console.error('Error parsing user data:', e);
        return null;
    }
}

// ============================================
// PRODUCTS
// ============================================

// Fetch products with filters
async function fetchProducts(filters = {}) {
    try {
        showLoading();
        
        // Build query string
        const queryParams = new URLSearchParams();
        Object.entries(filters).forEach(([key, value]) => {
            if (value) queryParams.append(key, value);
        });
        
        const response = await safeFetch(`${API_BASE_URL}/products?${queryParams}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching products:', error);
        showNotification('Error loading products - please refresh', 'error');
        return { products: [], total: 0, pages: 0 };
    } finally {
        hideLoading();
    }
}

// Fetch single product
async function fetchProduct(productId) {
    try {
        showLoading();
        const response = await safeFetch(`${API_BASE_URL}/products/${productId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const product = await response.json();
        return product;
    } catch (error) {
        console.error('Error fetching product:', error);
        showNotification('Error loading product details', 'error');
        return null;
    } finally {
        hideLoading();
    }
}

// Get image URL with fallback
function getImageUrl(url) {
    if (!url || url === 'null' || url === 'undefined') {
        return 'images/placeholder.jpg';
    }
    // Remove leading slash if present
    return url.startsWith('/') ? url.substring(1) : url;
}

// Render products grid
function renderProducts(products, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (!products || products.length === 0) {
        container.innerHTML = '<p class="no-products">No products found.</p>';
        return;
    }
    
    container.innerHTML = products.map(product => {
        const imageUrl = getImageUrl(product.image_url);
        return `
        <div class="product-card">
            ${product.is_new ? '<span class="product-badge badge-new">New</span>' : ''}
            ${product.discounted_price ? '<span class="product-badge badge-sale">Sale</span>' : ''}
            <div class="product-image">
                <img src="${imageUrl}" alt="${product.name || 'Product'}" 
                     onerror="this.onerror=null; this.src='images/placeholder.jpg'; this.classList.add('error');">
                <div class="product-actions">
                    <button class="product-action-btn" onclick="addToCart(${product.id}, 1)" title="Add to Cart">
                        <i class="fas fa-shopping-cart"></i>
                    </button>
                    <button class="product-action-btn" onclick="viewProduct(${product.id})" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="product-action-btn" onclick="addToWishlist(${product.id})" title="Add to Wishlist">
                        <i class="fas fa-heart"></i>
                    </button>
                </div>
            </div>
            <div class="product-info">
                <span class="product-category">${product.category_name || ''}</span>
                <h3 class="product-name">${product.name || 'Unnamed Product'}</h3>
                <div class="product-price">
                    <span class="current-price">${formatCurrency(product.discounted_price || product.price)}</span>
                    ${product.discounted_price ? `<span class="original-price">${formatCurrency(product.price)}</span>` : ''}
                </div>
                <div class="product-rating">
                    ${renderStars(product.rating || 0)}
                    <span>(${product.review_count || 0})</span>
                </div>
            </div>
        </div>
    `}).join('');
}

// Render star ratings
function renderStars(rating) {
    const fullStars = Math.floor(rating);
    const halfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);
    
    let stars = '';
    for (let i = 0; i < fullStars; i++) stars += '<i class="fas fa-star"></i>';
    if (halfStar) stars += '<i class="fas fa-star-half-alt"></i>';
    for (let i = 0; i < emptyStars; i++) stars += '<i class="far fa-star"></i>';
    
    return stars;
}

// ============================================
// SHOPPING CART
// ============================================

// Cart state
let cart = {
    items: [],
    total: 0,
    itemCount: 0
};

// Load cart from localStorage or API
async function loadCart() {
    if (isLoggedIn()) {
        try {
            const response = await safeFetch(`${API_BASE_URL}/cart`, {
                headers: getAuthHeaders()
            });
            
            if (response.ok) {
                cart = await response.json();
            } else {
                console.warn('Could not load cart from server');
            }
        } catch (error) {
            console.error('Error loading cart:', error);
        }
    } else {
        // Load from localStorage
        try {
            const savedCart = localStorage.getItem('cart');
            if (savedCart) {
                cart = JSON.parse(savedCart);
            }
        } catch (e) {
            console.error('Error parsing saved cart:', e);
            localStorage.removeItem('cart');
        }
    }
    updateCartUI();
}

// Save cart (localStorage for guests)
async function saveCart() {
    if (!isLoggedIn()) {
        localStorage.setItem('cart', JSON.stringify(cart));
    }
    updateCartUI();
}

// Add to cart
async function addToCart(productId, quantity = 1) {
    try {
        showLoading();
        
        if (isLoggedIn()) {
            const response = await safeFetch(`${API_BASE_URL}/cart/add`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({ product_id: productId, quantity })
            });
            
            if (response.ok) {
                showNotification('Item added to cart!', 'success');
                await loadCart();
            } else {
                const data = await response.json();
                showNotification(data.error || 'Failed to add item', 'error');
            }
        } else {
            // Guest cart
            const product = await fetchProduct(productId);
            if (product) {
                const existingItem = cart.items.find(item => item.product_id === productId);
                
                if (existingItem) {
                    existingItem.quantity += quantity;
                } else {
                    cart.items.push({
                        id: Date.now(), // Temporary ID
                        product_id: productId,
                        name: product.name,
                        price: product.discounted_price || product.price,
                        quantity: quantity,
                        image_url: product.image_url
                    });
                }
                
                cart.total = cart.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
                cart.itemCount = cart.items.reduce((sum, item) => sum + item.quantity, 0);
                
                await saveCart();
                showNotification('Item added to cart!', 'success');
                updateCartUI();
            }
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
        showNotification('Failed to add item to cart', 'error');
    } finally {
        hideLoading();
    }
}

// Update cart item quantity
async function updateCartItem(itemId, quantity) {
    try {
        if (isLoggedIn()) {
            const response = await safeFetch(`${API_BASE_URL}/cart/update/${itemId}`, {
                method: 'PUT',
                headers: getAuthHeaders(),
                body: JSON.stringify({ quantity })
            });
            
            if (response.ok) {
                await loadCart();
            }
        } else {
            const item = cart.items.find(item => item.id === itemId);
            if (item) {
                if (quantity <= 0) {
                    cart.items = cart.items.filter(i => i.id !== itemId);
                } else {
                    item.quantity = quantity;
                }
                
                cart.total = cart.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
                cart.itemCount = cart.items.reduce((sum, item) => sum + item.quantity, 0);
                
                await saveCart();
                renderCartPage();
            }
        }
    } catch (error) {
        console.error('Error updating cart:', error);
        showNotification('Failed to update cart', 'error');
    }
}

// Remove from cart
async function removeFromCart(itemId) {
    try {
        if (isLoggedIn()) {
            const response = await safeFetch(`${API_BASE_URL}/cart/remove/${itemId}`, {
                method: 'DELETE',
                headers: getAuthHeaders()
            });
            
            if (response.ok) {
                await loadCart();
                showNotification('Item removed from cart', 'info');
            }
        } else {
            cart.items = cart.items.filter(item => item.id !== itemId);
            cart.total = cart.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
            cart.itemCount = cart.items.reduce((sum, item) => sum + item.quantity, 0);
            
            await saveCart();
            renderCartPage();
        }
    } catch (error) {
        console.error('Error removing from cart:', error);
        showNotification('Failed to remove item', 'error');
    }
}

// Update cart UI (cart count badge)
function updateCartUI() {
    const cartCountElements = document.querySelectorAll('.cart-count');
    cartCountElements.forEach(el => {
        if (el) el.textContent = cart.itemCount || 0;
    });
}

// Render cart page
function renderCartPage() {
    const cartContainer = document.getElementById('cart-items');
    const summaryContainer = document.getElementById('cart-summary');
    
    if (!cartContainer || !summaryContainer) return;
    
    if (!cart.items || cart.items.length === 0) {
        cartContainer.innerHTML = '<p class="empty-cart">Your cart is empty. <a href="shop.html">Continue shopping</a></p>';
        summaryContainer.innerHTML = '';
        return;
    }
    
    cartContainer.innerHTML = cart.items.map(item => {
        const imageUrl = getImageUrl(item.image_url);
        return `
        <div class="cart-item">
            <img src="${imageUrl}" alt="${item.name}" class="cart-item-image"
                 onerror="this.onerror=null; this.src='images/placeholder.jpg';">
            <div class="cart-item-details">
                <h4>${item.name}</h4>
                <div class="cart-item-price">${formatCurrency(item.price)} each</div>
            </div>
            <div class="cart-item-actions">
                <div class="cart-item-quantity">
                    <button class="cart-quantity-btn" onclick="updateCartItem(${item.id}, ${item.quantity - 1})">-</button>
                    <input type="number" class="cart-quantity-input" value="${item.quantity}" min="1" 
                           onchange="updateCartItem(${item.id}, parseInt(this.value))">
                    <button class="cart-quantity-btn" onclick="updateCartItem(${item.id}, ${item.quantity + 1})">+</button>
                </div>
                <div class="cart-item-subtotal">${formatCurrency(item.price * item.quantity)}</div>
                <button class="cart-item-remove" onclick="removeFromCart(${item.id})">
                    <i class="fas fa-trash"></i> Remove
                </button>
            </div>
        </div>
    `}).join('');
    
    summaryContainer.innerHTML = `
        <h3>Order Summary</h3>
        <div class="summary-row">
            <span>Subtotal (${cart.itemCount} items)</span>
            <span>${formatCurrency(cart.total)}</span>
        </div>
        <div class="summary-row">
            <span>Shipping</span>
            <span>Calculated at checkout</span>
        </div>
        <div class="summary-row total">
            <span>Total</span>
            <span>${formatCurrency(cart.total)}</span>
        </div>
        <button class="btn-checkout" onclick="proceedToCheckout()">Proceed to Checkout</button>
    `;
}

// ============================================
// ORDERS
// ============================================

// Create order
async function createOrder(orderData) {
    if (!isLoggedIn()) {
        showNotification('Please login to checkout', 'warning');
        window.location.href = 'login.html';
        return;
    }
    
    try {
        showLoading();
        
        const response = await safeFetch(`${API_BASE_URL}/orders`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(orderData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Order placed successfully!', 'success');
            cart = { items: [], total: 0, itemCount: 0 };
            updateCartUI();
            setTimeout(() => {
                window.location.href = `tracking.html?order=${data.order_number}`;
            }, 1000);
        } else {
            showNotification(data.error || 'Failed to place order', 'error');
        }
    } catch (error) {
        console.error('Error creating order:', error);
        showNotification('Failed to place order - please try again', 'error');
    } finally {
        hideLoading();
    }
}

// Track order
async function trackOrder(orderNumber) {
    if (!orderNumber) {
        showNotification('Please enter an order number', 'warning');
        return;
    }
    
    try {
        showLoading();
        const response = await safeFetch(`${API_BASE_URL}/orders/track/${orderNumber}`);
        
        if (response.status === 404) {
            showNotification('Order not found', 'error');
            hideLoading();
            return;
        }
        
        const data = await response.json();
        
        if (response.ok) {
            renderTrackingInfo(data);
        } else {
            showNotification(data.error || 'Order not found', 'error');
        }
    } catch (error) {
        console.error('Error tracking order:', error);
        showNotification('Failed to track order', 'error');
    } finally {
        hideLoading();
    }
}

// Render tracking info
function renderTrackingInfo(order) {
    const resultDiv = document.getElementById('tracking-result');
    if (!resultDiv) return;
    
    const statusMap = {
        'pending': 'Order Pending',
        'processing': 'Processing',
        'shipped': 'Shipped',
        'delivered': 'Delivered',
        'cancelled': 'Cancelled'
    };
    
    resultDiv.innerHTML = `
        <h2>Order #${order.order_number}</h2>
        <div class="order-status-badge status-${order.status}">${statusMap[order.status] || order.status}</div>
        
        <div class="timeline">
            <div class="timeline-item">
                <div class="timeline-marker"></div>
                <div class="timeline-content">
                    <h4>Order Placed</h4>
                    <p>${new Date(order.order_date).toLocaleString()}</p>
                </div>
            </div>
            
            ${order.status !== 'pending' ? `
            <div class="timeline-item">
                <div class="timeline-marker"></div>
                <div class="timeline-content">
                    <h4>Processing</h4>
                    <p>Your order is being prepared</p>
                </div>
            </div>
            ` : ''}
            
            ${order.status === 'shipped' || order.status === 'delivered' ? `
            <div class="timeline-item">
                <div class="timeline-marker"></div>
                <div class="timeline-content">
                    <h4>Shipped</h4>
                    <p>Tracking Number: ${order.tracking_number || 'N/A'}</p>
                </div>
            </div>
            ` : ''}
            
            ${order.status === 'delivered' ? `
            <div class="timeline-item">
                <div class="timeline-marker"></div>
                <div class="timeline-content">
                    <h4>Delivered</h4>
                    <p>${order.estimated_delivery ? new Date(order.estimated_delivery).toLocaleDateString() : 'Completed'}</p>
                </div>
            </div>
            ` : ''}
        </div>
        
        <p><strong>Items:</strong> ${order.item_count}</p>
        ${order.estimated_delivery ? `<p><strong>Estimated Delivery:</strong> ${new Date(order.estimated_delivery).toLocaleDateString()}</p>` : ''}
    `;
    
    resultDiv.classList.add('active');
}

// ============================================
// REVIEWS
// ============================================

// Add review
async function addReview(productId, rating, comment) {
    if (!isLoggedIn()) {
        showNotification('Please login to leave a review', 'warning');
        window.location.href = 'login.html';
        return;
    }
    
    if (!comment || comment.trim() === '') {
        showNotification('Please enter a comment', 'warning');
        return;
    }
    
    try {
        showLoading();
        const response = await safeFetch(`${API_BASE_URL}/products/${productId}/reviews`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ rating, comment })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Review added! Thank you for your feedback.', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification(data.error || 'Failed to add review', 'error');
        }
    } catch (error) {
        console.error('Error adding review:', error);
        showNotification('Failed to add review', 'error');
    } finally {
        hideLoading();
    }
}

// ============================================
// PAGE SPECIFIC FUNCTIONS
// ============================================

// Initialize home page
async function initHomePage() {
    // Load featured categories
    try {
        const response = await safeFetch(`${API_BASE_URL}/categories`);
        const categories = await response.json();
        
        const categoriesGrid = document.getElementById('categories-grid');
        if (categoriesGrid && categories) {
            categoriesGrid.innerHTML = categories.slice(0, 6).map(cat => {
                const imageUrl = getImageUrl(cat.image_url);
                return `
                <div class="category-card" onclick="window.location.href='shop.html?category=${cat.id}'">
                    <div class="category-image" style="background-image: url('${imageUrl}')">
                        <div class="category-overlay">
                            <h3>${cat.name}</h3>
                            <p>${cat.product_count || 0} products</p>
                        </div>
                    </div>
                </div>
            `}).join('');
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
    
    // Load featured products
    const products = await fetchProducts({ featured: true, per_page: 8 });
    renderProducts(products.products, 'featured-products');
}

// Initialize shop page
async function initShopPage() {
    const urlParams = new URLSearchParams(window.location.search);
    const category = urlParams.get('category');
    const search = urlParams.get('search');
    
    let filters = {
        category: category,
        search: search,
        sort_by: 'newest',
        page: 1
    };
    
    // Load categories for filter
    try {
        const response = await safeFetch(`${API_BASE_URL}/categories`);
        const categories = await response.json();
        
        const categoryFilter = document.getElementById('category-filter');
        if (categoryFilter && categories) {
            categoryFilter.innerHTML = '<option value="">All Categories</option>' + 
                categories.map(cat => `<option value="${cat.id}" ${category == cat.id ? 'selected' : ''}>${cat.name}</option>`).join('');
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
    
    // Load products
    const data = await fetchProducts(filters);
    renderProducts(data.products, 'products-grid');
    
    // Render pagination
    renderPagination(data);
    
    // Setup filter listeners
    setupFilterListeners(filters);
}

// Setup filter listeners
function setupFilterListeners(filters) {
    const categoryFilter = document.getElementById('category-filter');
    const sortFilter = document.getElementById('sort-filter');
    const minPrice = document.getElementById('min-price');
    const maxPrice = document.getElementById('max-price');
    const applyFilters = document.getElementById('apply-filters');
    
    if (categoryFilter) {
        categoryFilter.addEventListener('change', () => {
            filters.category = categoryFilter.value;
            filters.page = 1;
            applyFiltersAndReload(filters);
        });
    }
    
    if (sortFilter) {
        sortFilter.addEventListener('change', () => {
            filters.sort_by = sortFilter.value;
            filters.page = 1;
            applyFiltersAndReload(filters);
        });
    }
    
    if (applyFilters && minPrice && maxPrice) {
        applyFilters.addEventListener('click', () => {
            filters.min_price = minPrice.value;
            filters.max_price = maxPrice.value;
            filters.page = 1;
            applyFiltersAndReload(filters);
        });
    }
}

// Apply filters and reload products
async function applyFiltersAndReload(filters) {
    const data = await fetchProducts(filters);
    renderProducts(data.products, 'products-grid');
    renderPagination(data);
}

// Render pagination
function renderPagination(data) {
    const pagination = document.getElementById('pagination');
    if (!pagination) return;
    
    if (!data || data.pages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '<ul class="pagination">';
    
    if (data.has_prev) {
        html += `<li class="page-item"><span class="page-link" onclick="changePage(${data.page - 1})">«</span></li>`;
    }
    
    for (let i = 1; i <= data.pages; i++) {
        if (i === data.page) {
            html += `<li class="page-item active"><span class="page-link">${i}</span></li>`;
        } else if (i === 1 || i === data.pages || (i >= data.page - 2 && i <= data.page + 2)) {
            html += `<li class="page-item"><span class="page-link" onclick="changePage(${i})">${i}</span></li>`;
        } else if (i === data.page - 3 || i === data.page + 3) {
            html += `<li class="page-item"><span class="page-link">...</span></li>`;
        }
    }
    
    if (data.has_next) {
        html += `<li class="page-item"><span class="page-link" onclick="changePage(${data.page + 1})">»</span></li>`;
    }
    
    html += '</ul>';
    pagination.innerHTML = html;
}

// Change page
function changePage(page) {
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('page', page);
    window.location.search = urlParams.toString();
}

// Initialize product detail page
async function initProductPage() {
    const urlParams = new URLSearchParams(window.location.search);
    const productId = urlParams.get('id');
    
    if (!productId) {
        window.location.href = 'shop.html';
        return;
    }
    
    const product = await fetchProduct(productId);
    if (!product) {
        showNotification('Product not found', 'error');
        setTimeout(() => window.location.href = 'shop.html', 1500);
        return;
    }
    
    // Render product details
    document.title = `${product.name} - Akwa Ibom Store`;
    
    const mainImage = document.getElementById('main-image');
    if (mainImage) {
        mainImage.src = getImageUrl(product.image_url);
        mainImage.onerror = function() { 
            this.src = 'images/placeholder.jpg'; 
            this.onerror = null;
        };
    }
    
    document.getElementById('product-name').textContent = product.name || 'Product';
    document.getElementById('product-category').textContent = product.category_name || '';
    document.getElementById('product-sku').textContent = `SKU: ${product.sku || 'N/A'}`;
    document.getElementById('product-price').innerHTML = `
        <span class="current-price">${formatCurrency(product.discounted_price || product.price)}</span>
        ${product.discounted_price ? `<span class="original-price">${formatCurrency(product.price)}</span>` : ''}
    `;
    
    const stockStatus = document.getElementById('stock-status');
    if (stockStatus) {
        if (product.stock > 10) {
            stockStatus.className = 'stock-status';
            stockStatus.textContent = 'In Stock';
        } else if (product.stock > 0) {
            stockStatus.className = 'stock-status low-stock';
            stockStatus.textContent = `Only ${product.stock} left in stock`;
        } else {
            stockStatus.className = 'stock-status out-of-stock';
            stockStatus.textContent = 'Out of Stock';
        }
    }
    
    document.getElementById('product-description').innerHTML = (product.description || '').replace(/\n/g, '<br>');
    
    // Render features
    const featuresContainer = document.getElementById('product-features');
    if (featuresContainer) {
        if (product.features && product.features.length > 0) {
            let features = product.features;
            if (typeof features === 'string') {
                try { features = JSON.parse(features); } 
                catch { features = [features]; }
            }
            featuresContainer.innerHTML = `
                <h3>Key Features</h3>
                <ul>
                    ${Array.isArray(features) ? features.map(f => `<li>${f}</li>`).join('') : ''}
                </ul>
            `;
        } else {
            featuresContainer.innerHTML = '';
        }
    }
    
    // Render reviews
    renderReviews(product.reviews || [], product.rating || 0);
    
    // Render related products
    renderProducts(product.related_products || [], 'related-products');
    
    // Setup add to cart button
    const addToCartBtn = document.getElementById('add-to-cart');
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', () => {
            const quantity = parseInt(document.getElementById('quantity')?.value || 1);
            addToCart(productId, quantity);
        });
    }
}

// Render reviews
function renderReviews(reviews, averageRating) {
    const reviewsContainer = document.getElementById('reviews-list');
    if (!reviewsContainer) return;
    
    const avgRatingEl = document.getElementById('average-rating');
    const totalReviewsEl = document.getElementById('total-reviews');
    
    if (avgRatingEl) avgRatingEl.textContent = (averageRating || 0).toFixed(1);
    if (totalReviewsEl) totalReviewsEl.textContent = `${reviews?.length || 0} reviews`;
    
    if (!reviews || reviews.length === 0) {
        reviewsContainer.innerHTML = '<p>No reviews yet. Be the first to review this product!</p>';
        return;
    }
    
    reviewsContainer.innerHTML = reviews.map(review => `
        <div class="review-card">
            <div class="review-header">
                <span class="reviewer-name">${review.user_name || 'Anonymous'}</span>
                <span class="review-rating">${renderStars(review.rating || 0)}</span>
                <span class="review-date">${review.created_at ? new Date(review.created_at).toLocaleDateString() : ''}</span>
            </div>
            <div class="review-comment">${review.comment || ''}</div>
        </div>
    `).join('');
    
    // Setup review form
    const submitReview = document.getElementById('submit-review');
    if (submitReview) {
        submitReview.onclick = () => {
            const rating = document.querySelector('.rating-select .active')?.dataset.rating || 5;
            const comment = document.getElementById('review-comment')?.value;
            if (comment?.trim()) {
                const productId = new URLSearchParams(window.location.search).get('id');
                addReview(productId, rating, comment);
            } else {
                showNotification('Please enter a comment', 'warning');
            }
        };
    }
}

// Initialize cart page
function initCartPage() {
    renderCartPage();
}

// Initialize checkout page
function initCheckoutPage() {
    if (!isLoggedIn()) {
        showNotification('Please login to checkout', 'warning');
        window.location.href = 'login.html?redirect=checkout.html';
        return;
    }
    
    // Load user data
    const user = getCurrentUser();
    if (user) {
        const nameInput = document.getElementById('full-name');
        const emailInput = document.getElementById('email');
        const phoneInput = document.getElementById('phone');
        const addressInput = document.getElementById('address');
        
        if (nameInput) nameInput.value = user.full_name || '';
        if (emailInput) emailInput.value = user.email || '';
        if (phoneInput) phoneInput.value = user.phone || '';
        if (addressInput) addressInput.value = user.address || '';
    }
    
    // Setup form submission
    const form = document.getElementById('checkout-form');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const orderData = {
                shipping_address: document.getElementById('address')?.value,
                shipping_city: document.getElementById('city')?.value,
                shipping_state: document.getElementById('state')?.value,
                shipping_phone: document.getElementById('phone')?.value,
                payment_method: document.querySelector('input[name="payment"]:checked')?.value,
                notes: document.getElementById('notes')?.value
            };
            
            createOrder(orderData);
        });
    }
    
    // Update order summary
    const subtotal = cart.total || 0;
    const deliveryFee = 1000;
    const total = subtotal + deliveryFee;
    
    const subtotalEl = document.getElementById('subtotal');
    const deliveryFeeEl = document.getElementById('delivery-fee');
    const totalEl = document.getElementById('total');
    
    if (subtotalEl) subtotalEl.textContent = formatCurrency(subtotal);
    if (deliveryFeeEl) deliveryFeeEl.textContent = formatCurrency(deliveryFee);
    if (totalEl) totalEl.textContent = formatCurrency(total);
    
    // Render order items
    const orderItemsDiv = document.getElementById('order-items');
    if (orderItemsDiv) {
        if (cart.items && cart.items.length > 0) {
            orderItemsDiv.innerHTML = cart.items.map(item => `
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; padding-bottom: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <div>
                        <span style="font-weight: 600;">${item.quantity}x</span> ${item.name}
                    </div>
                    <span>${formatCurrency(item.price * item.quantity)}</span>
                </div>
            `).join('');
        } else {
            orderItemsDiv.innerHTML = '<p style="color: var(--text-muted);">No items in cart</p>';
        }
    }
}

// Initialize tracking page
function initTrackingPage() {
    const urlParams = new URLSearchParams(window.location.search);
    const orderNumber = urlParams.get('order');
    
    const input = document.getElementById('tracking-number');
    const button = document.getElementById('track-order-btn');
    
    if (orderNumber && input) {
        input.value = orderNumber;
        trackOrder(orderNumber);
    }
    
    if (button && input) {
        button.addEventListener('click', () => {
            const orderNumber = input.value.trim();
            if (orderNumber) {
                window.location.href = `tracking.html?order=${orderNumber}`;
            } else {
                showNotification('Please enter an order number', 'warning');
            }
        });
    }
}

// Initialize dashboard
function initDashboard() {
    if (!isLoggedIn()) {
        window.location.href = 'login.html';
        return;
    }
    
    const user = getCurrentUser();
    if (user) {
        const userNameEl = document.getElementById('user-name');
        const userEmailEl = document.getElementById('user-email');
        const userInitialsEl = document.getElementById('user-initials');
        const welcomeNameEl = document.getElementById('welcome-name');
        
        if (userNameEl) userNameEl.textContent = user.full_name || '';
        if (userEmailEl) userEmailEl.textContent = user.email || '';
        if (userInitialsEl) {
            const initials = (user.full_name || 'U')
                .split(' ')
                .map(n => n[0])
                .join('')
                .toUpperCase()
                .substring(0, 2);
            userInitialsEl.textContent = initials;
        }
        if (welcomeNameEl) welcomeNameEl.textContent = user.full_name?.split(' ')[0] || 'Customer';
    }
    
    // Load user orders
    loadUserOrders();
    
    // Setup dashboard menu
    document.querySelectorAll('.dashboard-menu a').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = link.getAttribute('href').substring(1);
            
            document.querySelectorAll('.dashboard-menu a').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            document.querySelectorAll('.dashboard-section').forEach(s => s.classList.remove('active'));
            const targetSection = document.getElementById(target);
            if (targetSection) targetSection.classList.add('active');
        });
    });
}

// Load user orders
async function loadUserOrders() {
    try {
        const response = await safeFetch(`${API_BASE_URL}/orders`, {
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error('Failed to load orders');
        }
        
        const orders = await response.json();
        
        const recentOrdersEl = document.getElementById('recent-orders');
        const ordersListEl = document.getElementById('orders-list');
        
        if (recentOrdersEl) {
            if (orders && orders.length > 0) {
                const recentOrders = orders.slice(0, 3);
                recentOrdersEl.innerHTML = recentOrders.map(order => `
                    <tr>
                        <td>#${order.order_number}</td>
                        <td>${new Date(order.order_date).toLocaleDateString()}</td>
                        <td>${formatCurrency(order.total_amount)}</td>
                        <td><span class="order-status status-${order.status}">${order.status}</span></td>
                        <td><span class="order-status status-${order.payment_status}">${order.payment_status}</span></td>
                        <td><button class="btn-small" onclick="viewOrderDetails(${order.id})">View</button></td>
                    </tr>
                `).join('');
            } else {
                recentOrdersEl.innerHTML = '<tr><td colspan="6" style="text-align: center;">No recent orders</td></tr>';
            }
        }
        
        if (ordersListEl) {
            if (orders && orders.length > 0) {
                ordersListEl.innerHTML = orders.map(order => `
                    <tr>
                        <td>#${order.order_number}</td>
                        <td>${new Date(order.order_date).toLocaleDateString()}</td>
                        <td>${order.item_count || 0}</td>
                        <td>${formatCurrency(order.total_amount)}</td>
                        <td><span class="order-status status-${order.status}">${order.status}</span></td>
                        <td><span class="order-status status-${order.payment_status}">${order.payment_status}</span></td>
                        <td><button class="btn-small" onclick="viewOrderDetails(${order.id})">View</button></td>
                    </tr>
                `).join('');
            } else {
                ordersListEl.innerHTML = '<tr><td colspan="7" style="text-align: center;">No orders found</td></tr>';
            }
        }
        
        // Update dashboard stats
        if (orders) {
            const totalOrders = document.getElementById('total-orders');
            const pendingOrders = document.getElementById('pending-orders');
            const deliveredOrders = document.getElementById('delivered-orders');
            
            if (totalOrders) totalOrders.textContent = orders.length;
            if (pendingOrders) {
                const pending = orders.filter(o => o.status === 'pending' || o.status === 'processing').length;
                pendingOrders.textContent = pending;
            }
            if (deliveredOrders) {
                const delivered = orders.filter(o => o.status === 'delivered').length;
                deliveredOrders.textContent = delivered;
            }
        }
        
    } catch (error) {
        console.error('Error loading orders:', error);
        const ordersListEl = document.getElementById('orders-list');
        if (ordersListEl) {
            ordersListEl.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--danger-red);">Failed to load orders</td></tr>';
        }
    }
}

// ============================================
// PAGE INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Load cart
    loadCart();
    
    // Update cart UI
    updateCartUI();
    
    // Check hero image on every page load
    checkHeroImage();
    
    // Initialize based on current page
    const path = window.location.pathname;
    
    if (path.includes('index.html') || path === '/') {
        initHomePage();
    } else if (path.includes('shop.html')) {
        initShopPage();
    } else if (path.includes('product.html')) {
        initProductPage();
    } else if (path.includes('cart.html')) {
        initCartPage();
    } else if (path.includes('checkout.html')) {
        initCheckoutPage();
    } else if (path.includes('tracking.html')) {
        initTrackingPage();
    } else if (path.includes('dashboard.html')) {
        initDashboard();
    }
    
    // Setup auth tabs
    const authTabs = document.querySelectorAll('.auth-tab');
    authTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;
            
            authTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
            const targetForm = document.getElementById(`${target}-form`);
            if (targetForm) targetForm.classList.add('active');
        });
    });
    
    // Setup login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const username = document.getElementById('login-username')?.value;
            const password = document.getElementById('login-password')?.value;
            if (username && password) {
                login(username, password);
            } else {
                showNotification('Please enter username and password', 'warning');
            }
        });
    }
    
    // Setup register form
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const userData = {
                username: document.getElementById('reg-username')?.value,
                email: document.getElementById('reg-email')?.value,
                password: document.getElementById('reg-password')?.value,
                full_name: document.getElementById('reg-fullname')?.value,
                phone: document.getElementById('reg-phone')?.value,
                address: document.getElementById('reg-address')?.value,
                city: document.getElementById('reg-city')?.value,
                state: 'Akwa Ibom'
            };
            register(userData);
        });
    }
    
    // Setup logout button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }
    
    // Setup quantity controls
    document.querySelectorAll('.quantity-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const container = btn.closest('.quantity-controls, .cart-item-quantity');
            if (!container) return;
            
            const input = container.querySelector('.quantity-input, .cart-quantity-input');
            if (!input) return;
            
            let value = parseInt(input.value) || 1;
            
            if (btn.classList.contains('minus') || btn.textContent === '-') {
                value = Math.max(1, value - 1);
            } else {
                value = value + 1;
            }
            
            input.value = value;
            
            // Trigger change event for cart updates
            const event = new Event('change', { bubbles: true });
            input.dispatchEvent(event);
        });
    });
    
    // Setup rating stars
    const ratingStars = document.querySelectorAll('.rating-select i');
    if (ratingStars.length > 0) {
        ratingStars.forEach(star => {
            star.addEventListener('mouseover', () => {
                const rating = parseInt(star.dataset.rating) || 0;
                ratingStars.forEach((s, i) => {
                    if (i < rating) {
                        s.className = 'fas fa-star';
                    } else {
                        s.className = 'far fa-star';
                    }
                });
            });
            
            star.addEventListener('click', () => {
                const rating = parseInt(star.dataset.rating) || 0;
                ratingStars.forEach(s => s.classList.remove('active'));
                star.classList.add('active');
                
                ratingStars.forEach((s, i) => {
                    if (i < rating) {
                        s.className = 'fas fa-star active';
                    }
                });
            });
            
            star.addEventListener('mouseout', () => {
                const active = document.querySelector('.rating-select .active');
                if (active) {
                    const rating = parseInt(active.dataset.rating) || 0;
                    ratingStars.forEach((s, i) => {
                        if (i < rating) {
                            s.className = 'fas fa-star active';
                        } else {
                            s.className = 'far fa-star';
                        }
                    });
                } else {
                    ratingStars.forEach(s => s.className = 'far fa-star');
                }
            });
        });
    }
});

// ============================================
// HELPER FUNCTIONS
// ============================================

function viewProduct(productId) {
    window.location.href = `product.html?id=${productId}`;
}

function addToWishlist(productId) {
    if (!isLoggedIn()) {
        showNotification('Please login to add to wishlist', 'warning');
        window.location.href = 'login.html';
        return;
    }
    showNotification('Added to wishlist!', 'success');
}

function proceedToCheckout() {
    if (!isLoggedIn()) {
        showNotification('Please login to checkout', 'warning');
        window.location.href = 'login.html?redirect=checkout.html';
        return;
    }
    
    if (!cart.items || cart.items.length === 0) {
        showNotification('Your cart is empty', 'warning');
        return;
    }
    
    window.location.href = 'checkout.html';
}

function viewOrderDetails(orderId) {
    window.location.href = `tracking.html?order=${orderId}`;
}

// ============================================
// SAFETY INITIALIZATION
// ============================================

// Force hide loading overlay after page load (safety net)
window.addEventListener('load', () => {
    setTimeout(hideLoading, 2000);
    // Check hero image again after full load
    setTimeout(checkHeroImage, 500);
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        // Page became visible again, ensure no loading overlay is stuck
        setTimeout(hideLoading, 1000);
        // Check hero image again
        setTimeout(checkHeroImage, 500);
    }
});