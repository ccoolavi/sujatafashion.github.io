/**
 * Excel Handler - Simple Product Data Display for Sujata Fashion
 * ============================================================
 * 
 * This module provides immediate product data display without API calls.
 * All data is hardcoded and displays instantly when the page loads.
 */
class ExcelHandler {
  constructor() {
    // Hardcoded product data - displays immediately
    this.productData = {
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
        },
        {
          id: 'SF004',
          name: 'Embroidered Kurti',
          price: '₹1,299',
          category: 'Kurtis',
          image: 'images/products/kurti1.jpg',
          description: 'Stylish embroidered kurti for casual wear',
          availability: 'In Stock',
          sizes: 'S, M, L, XL, XXL',
          colors: 'Blue, Yellow, Pink'
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
          colors: 'Red, Gold, Maroon'
        },
        {
          id: 'SR002',
          name: 'Party Wear Saree Rental',
          price: '₹599/day',
          category: 'Party Wear',
          image: 'images/products/rental2.jpg',
          description: 'Elegant party wear saree for special occasions',
          availability: 'Available',
          sizes: 'Free Size',
          colors: 'Black, Navy, Purple'
        },
        {
          id: 'SR003',
          name: 'Wedding Guest Outfit',
          price: '₹799/day',
          category: 'Wedding Wear',
          image: 'images/products/rental3.jpg',
          description: 'Perfect outfit for wedding ceremonies',
          availability: 'Available',
          sizes: 'S, M, L, XL',
          colors: 'Green, Pink, Orange'
        }
      ]
    };
  }

  // Get shop products - returns data immediately
  getShopProducts() {
    return this.productData.shop;
  }

  // Get rental products - returns data immediately
  getRentProducts() {
    return this.productData.rent;
  }

  // Get all products - returns data immediately
  getAllProducts() {
    return {
      shop: this.productData.shop,
      rent: this.productData.rent
    };
  }

  // Get product by ID - returns data immediately
  getProductById(id) {
    const allProducts = [...this.productData.shop, ...this.productData.rent];
    return allProducts.find(product => product.id === id) || null;
  }

  // Get products by category - returns data immediately
  getProductsByCategory(category) {
    const allProducts = [...this.productData.shop, ...this.productData.rent];
    return allProducts.filter(product => 
      product.category.toLowerCase() === category.toLowerCase()
    );
  }

  // Search products - returns data immediately
  searchProducts(query) {
    const allProducts = [...this.productData.shop, ...this.productData.rent];
    const searchTerm = query.toLowerCase();
    return allProducts.filter(product => 
      product.name.toLowerCase().includes(searchTerm) ||
      product.description.toLowerCase().includes(searchTerm) ||
      product.category.toLowerCase().includes(searchTerm)
    );
  }

  // Initialize and display products immediately
  init() {
    console.log('Excel Handler initialized with immediate data display');
    this.displayProducts();
  }

  // Display products on page load
  displayProducts() {
    // Display shop products
    const shopContainer = document.getElementById('shop-products');
    if (shopContainer) {
      this.renderProducts(this.getShopProducts(), shopContainer);
    }

    // Display rental products
    const rentContainer = document.getElementById('rent-products');
    if (rentContainer) {
      this.renderProducts(this.getRentProducts(), rentContainer);
    }

    // Display featured products if container exists
    const featuredContainer = document.getElementById('featured-products');
    if (featuredContainer) {
      const featured = [...this.productData.shop.slice(0, 2), ...this.productData.rent.slice(0, 1)];
      this.renderProducts(featured, featuredContainer);
    }
  }

  // Render products to container
  renderProducts(products, container) {
    if (!container || !products) return;

    container.innerHTML = products.map(product => `
      <div class="product-card" data-id="${product.id}">
        <img src="${product.image}" alt="${product.name}" class="product-image">
        <div class="product-info">
          <h3 class="product-name">${product.name}</h3>
          <p class="product-price">${product.price}</p>
          <p class="product-category">${product.category}</p>
          <p class="product-description">${product.description}</p>
          <p class="product-availability">${product.availability}</p>
          <p class="product-sizes">Sizes: ${product.sizes}</p>
          <p class="product-colors">Colors: ${product.colors}</p>
        </div>
      </div>
    `).join('');
  }
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.excelHandler = new ExcelHandler();
    window.excelHandler.init();
  });
} else {
  // DOM already loaded
  window.excelHandler = new ExcelHandler();
  window.excelHandler.init();
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ExcelHandler;
}
