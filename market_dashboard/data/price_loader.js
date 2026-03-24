
// Auto-generated price loader for Market Dashboard
// Fetches real-time prices from Binance

const BINANCE_SYMBOLS = {
    "XRP": "XRPUSDT",
    "ADA": "ADAUSDT", 
    "SOL": "SOLUSDT",
    "ETH": "ETHUSDT",
    "BTC": "BTCUSDT",
    "SUI": "SUIUSDT",
    "TIA": "TIAUSDT"
};

// Fetch prices from Binance API
async function fetchBinancePrices() {
    const prices = {};
    
    for (const [name, symbol] of Object.entries(BINANCE_SYMBOLS)) {
        try {
            const response = await fetch(`https://api.binance.com/api/v3/ticker/24hr?symbol=${symbol}`);
            const data = await response.json();
            
            prices[name] = {
                price: parseFloat(data.lastPrice),
                change: parseFloat(data.priceChangePercent),
                high: parseFloat(data.highPrice),
                low: parseFloat(data.lowPrice),
                volume: parseFloat(data.volume)
            };
        } catch (e) {
            console.error(`Failed to fetch ${name}:`, e);
        }
    }
    
    return prices;
}

// Update dashboard with real prices
async function updateDashboardPrices() {
    console.log('🔄 Fetching real-time prices from Binance...');
    
    const prices = await fetchBinancePrices();
    
    // Update each asset card
    for (const [name, data] of Object.entries(prices)) {
        // Find asset card by name
        const assetCards = document.querySelectorAll('.asset-card');
        
        assetCards.forEach(card => {
            const assetName = card.querySelector('.asset-name');
            if (assetName && assetName.textContent === name) {
                // Update price
                const priceEl = card.querySelector('.asset-price-value');
                if (priceEl) {
                    const formattedPrice = data.price > 100 
                        ? `$${data.price.toLocaleString('en-US', {maximumFractionDigits: 2})}`
                        : `$${data.price.toFixed(4)}`;
                    priceEl.textContent = formattedPrice;
                    priceEl.style.color = data.change >= 0 ? '#10b981' : '#ef4444';
                }
                
                // Update change
                const changeEl = card.querySelector('.asset-price-change');
                if (changeEl) {
                    const sign = data.change >= 0 ? '+' : '';
                    changeEl.textContent = `${sign}${data.change.toFixed(2)}% (24h)`;
                    changeEl.className = `asset-price-change ${data.change >= 0 ? 'positive' : 'negative'}`;
                }
                
                // Add live indicator
                card.style.borderColor = data.change >= 0 ? '#10b981' : '#ef4444';
                setTimeout(() => {
                    card.style.borderColor = '';
                }, 1000);
            }
        });
    }
    
    // Update timestamp
    const now = new Date();
    document.getElementById('lastUpdated').textContent = now.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    console.log('✅ Prices updated from Binance');
}

// Auto-update every 30 seconds
setInterval(updateDashboardPrices, 30000);

// Initial load
document.addEventListener('DOMContentLoaded', updateDashboardPrices);
