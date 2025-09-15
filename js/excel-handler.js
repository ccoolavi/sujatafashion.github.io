/**
 * Excel Handler - JSON Data Integration for Sujata Fashion
 * ====================================================
 * 
 * This module fetches product data from Google Sheets via JSON API
 * with CORS-free fallback to hardcoded sample data.
 */
class ExcelHandler {
  constructor() {
    // Using Google Sheets JSON API endpoint (CORS-free)
    this.shopSheetUrl = 'https://sheets.googleapis.com/v4/spreadsheets/1JT5j6xifWkRcaeZIDzQjhB1RArzFEyqxSLQxnAObfms/values/Shop!A:J?key=AIzaSyD-9tSrke72PouQMnMX-a7UARF8ZHocBMw';
    this.rentSheetUrl = 'https://sheets.googleapis.com/v4/spreadsheets/1JT5j6xifWkRcaeZIDzQjhB1RArzFEyqxSLQxnAObfms/values/Rent!A:J?key=AIzaSyD-9tSrke72PouQMnMX-a7UARF8ZHocBMw';
    this.cache = new Map();
    this.cacheExpiry = 5 * 60 * 1000; // 5 minutes
    
    // Fallback sample data matching Google Sheets structure
    this.fallbackData = {
      shop: [
        {
          id: 'SF001',
          name: 'Elegant Silk Saree',
          price: '₹2,999',
          category: 'Sarees',
          image: 'images/products/saree1.jpg',
          description: 'Beautiful hand-woven silk saree with intricate golden border',
          availability: 'In Stock',
          sizes: 'Free Size',
          colors: 'Red, Blue, Green'
        },
        {
          id: 'SF002',
          name: 'Designer Lehenga',
          price: '₹4,999',
          category: 'Lehengas',
          image: 'images/products/lehenga1.jpg',
          description: 'Stunning bridal lehenga with heavy embroidery work',
          availability: 'In Stock',
          sizes: 'S, M, L, XL',
          colors: 'Pink, Maroon, Gold'
        },
        {
          id: 'SF003',
          name: 'Anarkali Suit Set',
          price: '₹1,899',
          category: 'Suits',
          image: 'images/products/anarkali1.jpg',
          description: 'Comfortable cotton anarkali with dupatta',
          availability: 'In Stock',
          sizes: 'S, M, L, XL',
          colors: 'White, Black, Navy'
        }
      ],
      rent: [
        {
          id: 'SR001',
          name: 'Bridal Lehenga Rental',
          price: '₹999/day',
          category: 'Bridal Wear',
          image: 'images/products/rental1.jpg',
          description: 'Premium bridal lehenga available for rent',
          availability: 'Available',
          sizes: 'S, M, L, XL',
          colors: 'Red, Pink, Gold'
        },
        {
          id: 'SR002',
          name: 'Party Wear Saree Rental',
          price: '₹299/day',
          category: 'Party Wear',
          image: 'images/products/rental2.jpg',
          description: 'Elegant party wear saree for special occasions',
          availability: 'Available',
          sizes: 'Free Size',
          colors: 'Black, Navy, Wine'
        }
      ]
    };
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
   * Fetch products from Google Sheets JSON API with fallback
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
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const jsonData = await response.json();
      const products = this.parseGoogleSheetsJSON(jsonData);
      
      // Cache the successful response
      this.cache.set(cacheKey, {
        data: products,
        timestamp: Date.now()
      });
      
      return products;
    } catch (error) {
      console.warn('Google Sheets API failed, using fallback data:', error);
      // Return fallback data immediately
      const fallbackProducts = this.fallbackData[type] || this.fallbackData.shop;
      
      // Cache fallback data for shorter duration
      this.cache.set(cacheKey, {
        data: fallbackProducts,
        timestamp: Date.now()
      });
      
      return fallbackProducts;
    }
  }

  /**
   * Parse Google Sheets JSON API response
   */
  parseGoogleSheetsJSON(jsonData) {
    if (!jsonData.values || jsonData.values.length < 2) {
      throw new Error('Invalid Google Sheets data format');
    }

    const [headers, ...rows] = jsonData.values;
    const products = [];

    rows.forEach((row, index) => {
      if (row.length < headers.length) {
        console.warn(`Row ${index + 2} has missing data, skipping`);
        return;
      }

      const product = {};
      headers.forEach((header, i) => {
        const key = header.toLowerCase().replace(/\s+/g, '_');
        product[key] = row[i] || '';
      });

      // Skip empty rows
      if (product.name && product.name.trim()) {
        products.push(product);
      }
    });

    return products;
  }

  /**
   * Render products in the container
   */
  renderProducts(products, container) {
    if (!products || products.length === 0) {
      container.innerHTML = '<div class="no-products">No products available at the moment.</div>';
      return;
    }

    const productsHTML = products.map(product => this.createProductCard(product)).join('');
    container.innerHTML = productsHTML;

    // Add click handlers for product cards
    this.attachProductHandlers(container);
  }

  /**
   * Create individual product card HTML
   */
  createProductCard(product) {
    const name = product.name || 'Unnamed Product';
    const price = product.price || 'Price not available';
    const image = product.image || 'images/placeholder.jpg';
    const description = product.description || 'No description available';
    const category = product.category || 'Uncategorized';
    const availability = product.availability || 'Unknown';

    return `
      <div class="product-card" data-product-id="${product.id || ''}">
        <div class="product-image">
          <img src="${image}" alt="${name}" loading="lazy" onerror="this.src='images/placeholder.jpg'">
          <div class="product-overlay">
            <button class="quick-view-btn" data-product-id="${product.id || ''}">
              Quick View
            </button>
          </div>
        </div>
        <div class="product-info">
          <span class="product-category">${category}</span>
          <h3 class="product-name">${name}</h3>
          <p class="product-description">${description}</p>
          <div class="product-meta">
            <span class="product-price">${price}</span>
            <span class="product-availability ${availability.toLowerCase().replace(/\s+/g, '-')}">
              ${availability}
            </span>
          </div>
          <div class="product-actions">
            <button class="btn btn-primary add-to-cart" data-product-id="${product.id || ''}">
              Add to Cart
            </button>
          </div>
        </div>
      </div>
    `;
  }

  /**
   * Attach event handlers to product cards
   */
  attachProductHandlers(container) {
    // Quick view buttons
    container.querySelectorAll('.quick-view-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const productId = btn.dataset.productId;
        this.openQuickView(productId);
      });
    });

    // Add to cart buttons
    container.querySelectorAll('.add-to-cart').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const productId = btn.dataset.productId;
        this.addToCart(productId);
      });
    });

    // Product card clicks
    container.querySelectorAll('.product-card').forEach(card => {
      card.addEventListener('click', (e) => {
        if (!e.target.closest('button')) {
          const productId = card.dataset.productId;
          this.viewProductDetails(productId);
        }
      });
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
        <p class="error-message">Failed to load products: ${message}</p>
        <button class="btn btn-secondary retry-btn" onclick="window.location.reload()">
          Retry
        </button>
      </div>
    `;
  }

  /**
   * Open quick view modal
   */
  openQuickView(productId) {
    console.log('Opening quick view for product:', productId);
    // Implement quick view modal logic
  }

  /**
   * Add product to cart
   */
  addToCart(productId) {
    console.log('Adding to cart:', productId);
    // Implement add to cart logic
  }

  /**
   * View product details page
   */
  viewProductDetails(productId) {
    console.log('Viewing product details:', productId);
    // Implement navigation to product details page
  }

  /**
   * Clear cache (useful for development)
   */
  clearCache() {
    this.cache.clear();
    console.log('Cache cleared');
  }

  /**
   * Get cached data for debugging
   */
  getCacheStatus() {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
      expiry: this.cacheExpiry
    };
  }
}

// Auto-initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  // Initialize for shop page
  if (document.querySelector('.products-grid.shop')) {
    const shopHandler = new ExcelHandler();
    shopHandler.init('.products-grid.shop', 'shop');
  }

  // Initialize for rent page
  if (document.querySelector('.products-grid.rent')) {
    const rentHandler = new ExcelHandler();
    rentHandler.init('.products-grid.rent', 'rent');
  }
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ExcelHandler;
}
if (typeof window !== 'undefined') {
  window.ExcelHandler = ExcelHandler;
}
