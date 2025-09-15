// Product Page JavaScript - Extract URL parameters, fetch data from Google Sheets, and handle social sharing

// Utility function to extract URL parameters
function getURLParameter(name) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(name);
}

// Configuration for Google Sheets API (adjust based on Phase 2 implementation)
const SHEETS_CONFIG = {
  spreadsheetId: 'your-google-sheets-id', // Replace with actual spreadsheet ID
  range: 'Products!A:Z', // Adjust range as needed
  apiKey: 'your-api-key' // Replace with actual API key
};

// Function to fetch product data from Google Sheets
async function fetchProductData(productId, productType) {
  try {
    const url = `https://sheets.googleapis.com/v4/spreadsheets/${SHEETS_CONFIG.spreadsheetId}/values/${SHEETS_CONFIG.range}?key=${SHEETS_CONFIG.apiKey}`;
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    const rows = data.values;
    
    if (!rows || rows.length === 0) {
      throw new Error('No data found in the spreadsheet');
    }
    
    // Assuming first row contains headers
    const headers = rows[0];
    
    // Find the product by ID and type
    for (let i = 1; i < rows.length; i++) {
      const row = rows[i];
      const product = {};
      
      // Map row data to object using headers
      headers.forEach((header, index) => {
        product[header.toLowerCase()] = row[index] || '';
      });
      
      // Check if this is the product we're looking for
      if (product.id === productId && 
          (!productType || product.type === productType)) {
        return product;
      }
    }
    
    throw new Error('Product not found');
  } catch (error) {
    console.error('Error fetching product data:', error);
    throw error;
  }
}

// Function to populate the product template with data
function populateProductTemplate(productData) {
  try {
    // Update product images
    const mainImage = document.getElementById('main-product-image');
    if (mainImage && productData.mainimage) {
      mainImage.src = productData.mainimage;
      mainImage.alt = productData.title || 'Product Image';
    }
    
    // Update thumbnail images if they exist
    const thumbnails = document.querySelectorAll('.product-thumbnail');
    thumbnails.forEach((thumb, index) => {
      const imageKey = `image${index + 1}`;
      if (productData[imageKey]) {
        thumb.src = productData[imageKey];
        thumb.alt = `${productData.title} - Image ${index + 1}`;
      }
    });
    
    // Update product title
    const titleElement = document.getElementById('product-title');
    if (titleElement && productData.title) {
      titleElement.textContent = productData.title;
    }
    
    // Update product price
    const priceElement = document.getElementById('product-price');
    if (priceElement && productData.price) {
      priceElement.textContent = `₹${productData.price}`;
    }
    
    // Update product description
    const descriptionElement = document.getElementById('product-description');
    if (descriptionElement && productData.description) {
      descriptionElement.innerHTML = productData.description;
    }
    
    // Update additional product details
    const categoryElement = document.getElementById('product-category');
    if (categoryElement && productData.category) {
      categoryElement.textContent = productData.category;
    }
    
    const availabilityElement = document.getElementById('product-availability');
    if (availabilityElement && productData.availability) {
      availabilityElement.textContent = productData.availability;
    }
    
    // Update meta tags for better SEO and social sharing
    updateMetaTags(productData);
    
  } catch (error) {
    console.error('Error populating product template:', error);
  }
}

// Function to update meta tags for SEO and social sharing
function updateMetaTags(productData) {
  // Update page title
  document.title = `${productData.title} - Sujata Fashion`;
  
  // Update meta description
  const metaDescription = document.querySelector('meta[name="description"]');
  if (metaDescription) {
    metaDescription.content = productData.description || `Shop ${productData.title} at Sujata Fashion`;
  }
  
  // Update Open Graph tags for Facebook sharing
  updateOrCreateMetaTag('property', 'og:title', productData.title);
  updateOrCreateMetaTag('property', 'og:description', productData.description);
  updateOrCreateMetaTag('property', 'og:image', productData.mainimage);
  updateOrCreateMetaTag('property', 'og:url', window.location.href);
  updateOrCreateMetaTag('property', 'og:type', 'product');
  
  // Update Twitter Card tags
  updateOrCreateMetaTag('name', 'twitter:card', 'summary_large_image');
  updateOrCreateMetaTag('name', 'twitter:title', productData.title);
  updateOrCreateMetaTag('name', 'twitter:description', productData.description);
  updateOrCreateMetaTag('name', 'twitter:image', productData.mainimage);
}

// Utility function to update or create meta tags
function updateOrCreateMetaTag(attribute, value, content) {
  let metaTag = document.querySelector(`meta[${attribute}="${value}"]`);
  if (!metaTag) {
    metaTag = document.createElement('meta');
    metaTag.setAttribute(attribute, value);
    document.head.appendChild(metaTag);
  }
  metaTag.content = content;
}

// Social sharing functions
const SocialShare = {
  // WhatsApp sharing
  shareToWhatsApp: function(productData) {
    const message = `Check out this amazing product: ${productData.title}\nPrice: ₹${productData.price}\n${window.location.href}`;
    const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(message)}`;
    window.open(whatsappUrl, '_blank');
  },
  
  // Facebook sharing
  shareToFacebook: function(productData) {
    const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(window.location.href)}`;
    window.open(facebookUrl, '_blank', 'width=600,height=400');
  },
  
  // Copy link to clipboard
  copyToClipboard: function() {
    navigator.clipboard.writeText(window.location.href).then(function() {
      // Show success message
      showNotification('Link copied to clipboard!', 'success');
    }).catch(function(err) {
      console.error('Could not copy text: ', err);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = window.location.href;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      showNotification('Link copied to clipboard!', 'success');
    });
  }
};

// Function to show notifications
function showNotification(message, type = 'info') {
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.textContent = message;
  
  // Style the notification
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${type === 'success' ? '#4CAF50' : '#2196F3'};
    color: white;
    padding: 12px 24px;
    border-radius: 4px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    z-index: 1000;
    font-family: Arial, sans-serif;
    font-size: 14px;
  `;
  
  // Add to page
  document.body.appendChild(notification);
  
  // Remove after 3 seconds
  setTimeout(() => {
    if (notification.parentNode) {
      notification.parentNode.removeChild(notification);
    }
  }, 3000);
}

// Function to setup event listeners for social sharing buttons
function setupSocialSharingListeners(productData) {
  // WhatsApp share button
  const whatsappBtn = document.getElementById('share-whatsapp');
  if (whatsappBtn) {
    whatsappBtn.addEventListener('click', () => SocialShare.shareToWhatsApp(productData));
  }
  
  // Facebook share button
  const facebookBtn = document.getElementById('share-facebook');
  if (facebookBtn) {
    facebookBtn.addEventListener('click', () => SocialShare.shareToFacebook(productData));
  }
  
  // Copy link button
  const copyBtn = document.getElementById('share-copy');
  if (copyBtn) {
    copyBtn.addEventListener('click', () => SocialShare.copyToClipboard());
  }
}

// Function to handle loading states
function setLoadingState(isLoading) {
  const loadingElement = document.getElementById('loading-indicator');
  if (loadingElement) {
    loadingElement.style.display = isLoading ? 'block' : 'none';
  }
  
  const productContent = document.getElementById('product-content');
  if (productContent) {
    productContent.style.display = isLoading ? 'none' : 'block';
  }
}

// Function to show error messages
function showError(message) {
  const errorElement = document.getElementById('error-message');
  if (errorElement) {
    errorElement.textContent = message;
    errorElement.style.display = 'block';
  } else {
    // Fallback: create error element
    const errorDiv = document.createElement('div');
    errorDiv.id = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
      background: #f44336;
      color: white;
      padding: 16px;
      margin: 16px;
      border-radius: 4px;
      text-align: center;
    `;
    document.body.insertBefore(errorDiv, document.body.firstChild);
  }
}

// Main initialization function
async function initializeProductPage() {
  try {
    // Show loading state
    setLoadingState(true);
    
    // Extract URL parameters
    const productId = getURLParameter('id');
    const productType = getURLParameter('type');
    
    // Validate required parameters
    if (!productId) {
      throw new Error('Product ID is required');
    }
    
    // Fetch product data
    const productData = await fetchProductData(productId, productType);
    
    // Populate the template with product data
    populateProductTemplate(productData);
    
    // Setup social sharing event listeners
    setupSocialSharingListeners(productData);
    
    // Hide loading state
    setLoadingState(false);
    
  } catch (error) {
    console.error('Failed to initialize product page:', error);
    setLoadingState(false);
    showError(`Failed to load product: ${error.message}`);
  }
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeProductPage);
} else {
  initializeProductPage();
}

// Export functions for external use if needed
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    getURLParameter,
    fetchProductData,
    populateProductTemplate,
    SocialShare,
    initializeProductPage
  };
}
