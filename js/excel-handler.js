/**
 * Excel Handler - Simple Product Data Display for Sujata Fashion
 * ============================================================
 * 
 * This module provides immediate product data display without API calls.
 * All data is hardcoded and displays instantly when the page loads.
 * Matches the DOM structure expected by index.html
 */

console.log('Excel Handler loading...');

// Hardcoded product data that displays immediately
const shopProducts = [
  {
    id: 1,
    name: 'Designer Silk Saree Collection',
    price: 2899,
    image: 'https://images.unsplash.com/photo-1583391733956-6c78276477e2?w=400',
    category: 'sarees',
    description: 'Beautiful hand-woven silk saree with intricate golden border'
  },
  {
    id: 2,
    name: 'Premium Lehenga Set',
    price: 4599,
    image: 'https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=400',
    category: 'lehengas',
    description: 'Stunning bridal lehenga with heavy embroidery work'
  },
  {
    id: 3,
    name: 'Elegant Anarkali Suit',
    price: 3299,
    image: 'https://images.unsplash.com/photo-1583391733981-24c11ad0c90b?w=400',
    category: 'suits',
    description: 'Comfortable cotton anarkali with dupatta and intricate work'
  },
  {
    id: 4,
    name: 'Embroidered Kurti Collection',
    price: 1599,
    image: 'https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=400',
    category: 'kurtis',
    description: 'Stylish embroidered kurti perfect for casual and office wear'
  },
  {
    id: 5,
    name: 'Traditional Sharara Set',
    price: 3899,
    image: 'https://images.unsplash.com/photo-1583391733956-6c78276477e2?w=400',
    category: 'sharara',
    description: 'Traditional sharara set with beautiful mirror work and embroidery'
  },
  {
    id: 6,
    name: 'Cotton Salwar Kameez',
    price: 1899,
    image: 'https://images.unsplash.com/photo-1583391733981-24c11ad0c90b?w=400',
    category: 'salwar',
    description: 'Comfortable daily wear cotton salwar kameez in vibrant colors'
  }
];

const rentProducts = [
  {
    id: 7,
    name: 'Bridal Lehenga Premium',
    price: 8500,
    rentPrice: 1200,
    image: 'https://images.unsplash.com/photo-1583391733956-6c78276477e2?w=400',
    category: 'bridal',
    description: 'Heavy bridal lehenga with gold embroidery, perfect for weddings'
  },
  {
    id: 8,
    name: 'Party Wear Designer Saree',
    price: 5200,
    rentPrice: 800,
    image: 'https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=400',
    category: 'party',
    description: 'Elegant party wear saree with sequins and beadwork'
  },
  {
    id: 9,
    name: 'Reception Gown',
    price: 6800,
    rentPrice: 1000,
    image: 'https://images.unsplash.com/photo-1583391733981-24c11ad0c90b?w=400',
    category: 'gowns',
    description: 'Stunning floor-length gown perfect for receptions and parties'
  },
  {
    id: 10,
    name: 'Wedding Guest Outfit',
    price: 4200,
    rentPrice: 650,
    image: 'https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=400',
    category: 'wedding',
    description: 'Perfect outfit for wedding ceremonies and functions'
  },
  {
    id: 11,
    name: 'Sangeet Special Lehenga',
    price: 7500,
    rentPrice: 1100,
    image: 'https://images.unsplash.com/photo-1583391733956-6c78276477e2?w=400',
    category: 'sangeet',
    description: 'Vibrant lehenga perfect for sangeet and dance performances'
  },
  {
    id: 12,
    name: 'Cocktail Party Dress',
    price: 3800,
    rentPrice: 580,
    image: 'https://images.unsplash.com/photo-1583391733981-24c11ad0c90b?w=400',
    category: 'cocktail',
    description: 'Chic cocktail dress for evening parties and celebrations'
  }
];

// Function to create product card HTML (matches index.html structure)
function createProductCard(product, isRental = false) {
  console.log('Creating product card for:', product.name);
  return `
    <div class="product-card">
      <img src="${product.image}" alt="${product.name}" class="product-image" 
           onerror="this.src='https://via.placeholder.com/400x300?text=${encodeURIComponent(product.name)}'">
      <div class="product-info">
        <h3 class="product-title">${product.name}</h3>
        <div class="product-price">
          ₹${product.price}
          ${product.rentPrice ? `<span class="rent-price">Rent: ₹${product.rentPrice}</span>` : ''}
        </div>
        <div class="product-actions">
          ${isRental ? 
            `<button class="btn btn-rent" onclick="rentProduct(${product.id})">Rent Now</button>
             <button class="btn btn-buy" onclick="buyProduct(${product.id})">Buy</button>` :
            `<button class="btn btn-buy" onclick="buyProduct(${product.id})">Buy Now</button>`
          }
        </div>
      </div>
    </div>
  `;
}

// Function to display products in containers (matches index.html)
function displayProducts(products, containerId, isRental = false) {
  console.log(`Displaying ${products.length} products in ${containerId}`);
  const container = document.getElementById(containerId);
  if (!container) {
    console.error(`Container ${containerId} not found!`);
    return;
  }
  
  if (products.length === 0) {
    container.innerHTML = '<div class="error">No products available at the moment.</div>';
    return;
  }
  
  const productsHtml = products.map(product => createProductCard(product, isRental)).join('');
  container.innerHTML = productsHtml;
  console.log(`Successfully displayed products in ${containerId}`);
}

// Product interaction functions
function buyProduct(productId) {
  console.log('Buy product:', productId);
  alert(`Product ${productId} added to cart! (This is a demo)`);
}

function rentProduct(productId) {
  console.log('Rent product:', productId);
  alert(`Product ${productId} added to rental cart! (This is a demo)`);
}

// Initialize function to load and display products immediately
function initializeExcelHandler() {
  console.log('Excel Handler initializing with immediate data display');
  console.log('DOM ready state:', document.readyState);
  
  // Verify containers exist
  const shopContainer = document.getElementById('shop-products');
  const rentContainer = document.getElementById('rent-products');
  
  console.log('Shop container found:', !!shopContainer);
  console.log('Rent container found:', !!rentContainer);
  
  if (shopContainer && rentContainer) {
    // Display products immediately with hardcoded data
    displayProducts(shopProducts, 'shop-products', false);
    displayProducts(rentProducts, 'rent-products', true);
    console.log('Excel Handler initialized successfully with immediate display!');
  } else {
    console.error('Required containers not found!');
    // Retry after a short delay in case DOM is still loading
    setTimeout(initializeExcelHandler, 100);
  }
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  console.log('DOM still loading, waiting for DOMContentLoaded...');
  document.addEventListener('DOMContentLoaded', initializeExcelHandler);
} else {
  console.log('DOM already loaded, initializing immediately...');
  initializeExcelHandler();
}

// Export for global access
window.excelHandler = {
  shopProducts,
  rentProducts,
  displayProducts,
  initializeExcelHandler,
  buyProduct,
  rentProduct
};

console.log('Excel Handler loaded successfully!');
