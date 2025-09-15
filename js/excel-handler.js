/**
 * Excel Handler - CSV Data Integration for Sujata Fashion
 * ====================================================
 * 
 * This module fetches product data from Google Sheets via CSV export
 * and dynamically creates product cards for the shop interface.
 */
class ExcelHandler {
  constructor() {
    this.shopSheetUrl = 'https://docs.google.com/spreadsheets/d/1JT5j6xifWkRcaeZIDzQjhB1RArzFEyqxSLQxnAObfms/export?format=csv&gid=1717675571';
    this.rentSheetUrl = 'https://docs.google.com/spreadsheets/d/1JT5j6xifWkRcaeZIDzQjhB1RArzFEyqxSLQxnAObfms/export?format=csv&gid=1815405474';
    this.cache = new Map();
    this.cacheExpiry = 5 * 60 * 1000; // 5 minutes
  }

  /**
   * Initialize the excel handler and load products
   */
  async init(containerSelector = '.products-grid', type = 'shop') {
    const container = document.querySelector(containerSelector);
    if (!container) {
      console.error('Products container not found:', containerSelector);
      return;
    }

    this.showLoadingState(container);

    try {
      const products = await this.fetchProducts(type);
      this.renderProducts(products, container);
    } catch (error) {
      console.error('Failed to load products:', error);
      this.showErrorState(container, error.message);
    }
  }

  /**
   * Fetch products from Google Sheets CSV export
   */
  async fetchProducts(type = 'shop') {
    const cacheKey = `products_${type}`;
    const cached = this.cache.get(cacheKey);
    
    if (cached && (Date.now() - cached.timestamp) < this.cacheExpiry) {
      return cached.data;
    }

    const url = type === 'rent' ? this.rentSheetUrl : this.shopSheetUrl;
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'text/csv'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const csvText = await response.text();
      const products = this.parseCSV(csvText);
      
      // Cache the results
      this.cache.set(cacheKey, {
        data: products,
        timestamp: Date.now()
      });

      return products;
    } catch (error) {
      console.error('Error fetching CSV data:', error);
      throw new Error('Failed to fetch product data. Please check your internet connection.');
    }
  }

  /**
   * Parse CSV data into product objects
   */
  parseCSV(csvText) {
    const lines = csvText.split('\n').filter(line => line.trim());
    if (lines.length < 2) {
      throw new Error('Invalid CSV data - no products found');
    }

    const headers = this.parseCSVLine(lines[0]).map(h => h.toLowerCase().trim());
    const products = [];

    for (let i = 1; i < lines.length; i++) {
      const values = this.parseCSVLine(lines[i]);
      if (values.length === 0 || values.every(v => !v.trim())) continue;

      const product = {};
      headers.forEach((header, index) => {
        product[header] = values[index] ? values[index].trim() : '';
      });

      // Validate required fields
      if (product.id && product.name && product.price) {
        // Clean and format the product data
        product.id = product.id.toString();
        product.price = this.formatPrice(product.price);
        product.image = this.formatImageUrl(product.image || product.imageurl);
        product.category = product.category || 'Uncategorized';
        product.description = product.description || '';
        product.stock = parseInt(product.stock) || 0;
        
        products.push(product);
      }
    }

    if (products.length === 0) {
      throw new Error('No valid products found in the data');
    }

    return products;
  }

  /**
   * Parse a single CSV line, handling commas within quotes
   */
  parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      
      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        result.push(current);
        current = '';
      } else {
        current += char;
      }
    }
    
    result.push(current);
    return result;
  }

  /**
   * Format price to display currency
   */
  formatPrice(price) {
    const numPrice = parseFloat(price.toString().replace(/[^\d.]/g, ''));
    return isNaN(numPrice) ? 'Price on request' : `₹${numPrice.toLocaleString('en-IN')}`;
  }

  /**
   * Format and validate image URL
   */
  formatImageUrl(imageUrl) {
    if (!imageUrl) return 'images/placeholder.jpg';
    
    // If it's already a full URL, return as is
    if (imageUrl.startsWith('http')) return imageUrl;
    
    // If it's a relative path, make it absolute
    return imageUrl.startsWith('/') ? imageUrl : `images/${imageUrl}`;
  }

  /**
   * Render products in the container
   */
  renderProducts(products, container) {
    container.innerHTML = '';
    
    if (products.length === 0) {
      container.innerHTML = '<p class="no-products">No products available at the moment.</p>';
      return;
    }

    const fragment = document.createDocumentFragment();
    
    products.forEach(product => {
      const productCard = this.createProductCard(product);
      fragment.appendChild(productCard);
    });
    
    container.appendChild(fragment);
  }

  /**
   * Create a product card element
   */
  createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    card.setAttribute('data-product-id', product.id);
    card.setAttribute('data-category', product.category);
    
    const stockClass = product.stock > 0 ? 'in-stock' : 'out-of-stock';
    const stockText = product.stock > 0 ? 'In Stock' : 'Out of Stock';
    
    card.innerHTML = `
      <div class="product-image-container">
        <img src="${product.image}" alt="${product.name}" class="product-image" loading="lazy" onerror="this.src='images/placeholder.jpg'">
        <div class="product-overlay">
          <button class="quick-view-btn" onclick="window.excelHandler.viewProduct('${product.id}')">
            Quick View
          </button>
        </div>
        <span class="stock-badge ${stockClass}">${stockText}</span>
      </div>
      <div class="product-info">
        <h3 class="product-name">${this.escapeHtml(product.name)}</h3>
        <p class="product-category">${this.escapeHtml(product.category)}</p>
        <p class="product-description">${this.escapeHtml(this.truncateText(product.description, 100))}</p>
        <div class="product-footer">
          <span class="product-price">${product.price}</span>
          <button class="view-details-btn" onclick="window.excelHandler.viewProduct('${product.id}')">
            View Details
          </button>
        </div>
      </div>
    `;
    
    return card;
  }

  /**
   * View product details - redirect to product.html
   */
  viewProduct(productId) {
    if (!productId) {
      console.error('Product ID is required');
      return;
    }
    
    // Store product ID in session storage for product.html to use
    sessionStorage.setItem('selectedProductId', productId);
    
    // Navigate to product details page
    window.location.href = `product.html?id=${encodeURIComponent(productId)}`;
  }

  /**
   * Get a specific product by ID
   */
  async getProductById(productId, type = 'shop') {
    try {
      const products = await this.fetchProducts(type);
      return products.find(p => p.id === productId.toString());
    } catch (error) {
      console.error('Error fetching product:', error);
      return null;
    }
  }

  /**
   * Filter products by category
   */
  filterProducts(category, containerSelector = '.products-grid') {
    const container = document.querySelector(containerSelector);
    if (!container) return;
    
    const productCards = container.querySelectorAll('.product-card');
    
    productCards.forEach(card => {
      const productCategory = card.getAttribute('data-category');
      const shouldShow = !category || category === 'all' || productCategory === category;
      card.style.display = shouldShow ? 'block' : 'none';
    });
  }

  /**
   * Search products by name or description
   */
  searchProducts(query, containerSelector = '.products-grid') {
    const container = document.querySelector(containerSelector);
    if (!container) return;
    
    const productCards = container.querySelectorAll('.product-card');
    const searchTerm = query.toLowerCase().trim();
    
    productCards.forEach(card => {
      const name = card.querySelector('.product-name').textContent.toLowerCase();
      const description = card.querySelector('.product-description').textContent.toLowerCase();
      const shouldShow = !searchTerm || name.includes(searchTerm) || description.includes(searchTerm);
      card.style.display = shouldShow ? 'block' : 'none';
    });
  }

  /**
   * Show loading state
   */
  showLoadingState(container) {
    container.innerHTML = `
      <div class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading products...</p>
      </div>
    `;
  }

  /**
   * Show error state
   */
  showErrorState(container, message) {
    container.innerHTML = `
      <div class="error-state">
        <div class="error-icon">⚠️</div>
        <p>Unable to load products</p>
        <p class="error-message">${this.escapeHtml(message)}</p>
        <button class="retry-btn" onclick="window.location.reload()">Try Again</button>
      </div>
    `;
  }

  /**
   * Utility: Escape HTML to prevent XSS
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Utility: Truncate text to specified length
   */
  truncateText(text, maxLength) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength).trim() + '...';
  }

  /**
   * Clear cache
   */
  clearCache() {
    this.cache.clear();
  }

  /**
   * Refresh products
   */
  async refresh(containerSelector = '.products-grid', type = 'shop') {
    this.clearCache();
    await this.init(containerSelector, type);
  }
}

// Initialize global instance
window.excelHandler = new ExcelHandler();

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  // Check if we're on a page that should load products
  const productsContainer = document.querySelector('.products-grid');
  if (productsContainer) {
    // Determine type from page URL or data attribute
    const isRentPage = window.location.pathname.includes('rent') || 
                      document.body.classList.contains('rent-page');
    const type = isRentPage ? 'rent' : 'shop';
    
    window.excelHandler.init('.products-grid', type);
  }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ExcelHandler;
}
