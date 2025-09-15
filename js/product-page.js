// Google Sheets API Configuration
const API_KEY = 'AIzaSyAWWpa4xPGR8aBWKqSq0oKOp6a0XELijh0';
const SPREADSHEET_ID = '1JT5j6xifWkRcaeZIDzQjhB1RArzFEyqxSLQxnAObfms';
const WHATSAPP_NUMBER = '+919763416561';

let currentProduct = null;

// Initialize product page
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const productId = urlParams.get('id');
    const productType = urlParams.get('type');
    
    if (productId && productType) {
        loadProductDetails(productId, productType);
    } else {
        showError('Invalid product URL');
    }
});

// Load product details
async function loadProductDetails(productId, type) {
    try {
        console.log('🔍 Loading product details for:', productId, type);
        
        const range = type === 'rent' ? 'Rental!A:V' : 'Sale!A:U';
        const data = await fetchSheetData(range);
        const product = parseProductData(data, type, productId);
        
        if (product) {
            currentProduct = product;
            displayProductDetails(product);
            updatePageMeta(product);
        } else {
            showError('Product not found');
        }
    } catch (error) {
        console
