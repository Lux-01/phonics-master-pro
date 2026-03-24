---
name: sensory-input-layer
description: Gather raw information from external sources - web scraping, API calls, blockchain queries, file parsing, and sentiment scanning. The eyes and ears of the OpenClaw ecosystem. Use when data is needed for ARAS reasoning and ALOE learning.
---

# Sensory Input Layer (SIL)

The data gathering layer that feeds ARAS and ALOE. Collects information from any external source.

## Philosophy

**ARAS can't reason without data. ALOE can't learn without examples.**

SIL is the sensory system - eyes, ears, and peripheral nervous system of OpenClaw.

## Input Capabilities

### 1. Web Scraping

Gather data from websites:
- Static HTML pages
- Dynamic JavaScript content
- API endpoints
- RSS/Atom feeds
- Sitemap crawling

### 2. API Queries

Fetch from any API:
- REST APIs (GET, POST, PUT, DELETE)
- GraphQL endpoints
- WebSocket streams
- gRPC services
- Rate limit handling

### 3. Blockchain Data

Solana and EVM queries:
- RPC node queries
- Token metadata
- Transaction history
- Account balances
- Program accounts
- LP pools and DEX data

### 4. File Parsing

Read local files:
- JSON, CSV, YAML, TOML
- Log files
- Markdown, text
- Binary formats (with handlers)
- Compressed archives

### 5. Social Sentiment

Analyze social signals:
- Twitter/X feeds
- Discord/Telegram channels
- Reddit discussions
- Moltbook feeds
- News aggregators

### 6. Narrative Detection

Identify emerging trends:
- Keyword frequency
- Topic clustering
- Sentiment scoring
- Momentum tracking
- Cross-platform correlation

## Input Pipeline

```
Request → Source Selection → Data Gathering → 
Cleaning → Normalization → Validation → Output
```

### Step 1: Request
```python
{
  "target": "solana_token_metadata",
  "identifier": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZoo", 
  "source": "jupiter_api",
  "priority": "high",
  "cache": true
}
```

### Step 2: Source Selection
Auto-select best source based on:
- Reliability score
- Latency
- Rate limits
- Freshness requirements

### Step 3: Data Gathering
Execute fetch/query:
```python
# Web
web_fetch(url, extract="markdown")

# API
api_call(endpoint, method="GET", headers={})

# Solana
rpc_call("getAccountInfo", [pubkey])

# File
read_file("data/tokens.json")
```

### Step 4: Cleaning & Normalization
Standardize output:
```python
{
  "raw_data": {...},
  "normalized": {
    "token_address": "...",
    "symbol": "...",
    "price_usd": 1.23,
    "timestamp": "2026-03-08T22:00:00Z"
  },
  "metadata": {
    "source": "jupiter_api",
    "fetched_at": "...",
    "latency_ms": 245
  }
}
```

### Step 5: Validation
Check data quality:
- Required fields present
- Values in expected ranges
- Timestamps current
- No error responses

## Data Sources

### Web Sources
| Source | Type | Reliability | Rate Limit |
|--------|------|-------------|------------|
| Brave Search | Web API | High | 2000/mo |
| web_fetch | HTML | Medium | N/A |
| RSS feeds | Feed | Medium | Per feed |

### Crypto APIs
| Source | Type | Reliability | Data |
|--------|------|-------------|------|
| Jupiter | Aggregator | High | Prices, swaps |
| Birdeye | Market data | High | OHLCV, metadata |
| Helius | RPC/Index | High | On-chain data |
| DexScreener | DEX data | High | Pairs, volume |

### File Sources
| Format | Methods | Use Case |
|--------|---------|----------|
| JSON | json.load() | APIs, config |
| CSV | csv.DictReader | Tables, exports |
| YAML | yaml.safe_load() | Config, docs |
| Logs | Line parsing | Events, errors |

## Usage Patterns

### Pattern 1: Single Source Fetch
```
User: "Get token metadata"
→ Identify source (Jupiter/Birdeye)
→ Fetch with retry
→ Clean and normalize
→ Return structured data
```

### Pattern 2: Multi-Source Aggregation
```
User: "Full token analysis"
→ Fetch metadata (Jupiter)
→ Fetch price history (Birdeye)
→ Fetch holders (Helius)
→ Fetch sentiment (Social)
→ Merge and normalize
→ Return comprehensive view
```

### Pattern 3: Continuous Monitoring
```
User: "Monitor this token"
→ Set up polling schedule
→ Fetch every 5 minutes
→ Detect changes
→ Feed to ALOE for learning
→ Alert on anomalies
```

## Integration with ALOE

SIL feeds observations to ALOE:

```python
# After each data fetch
aloe.observe(
    action="fetch_jupiter_price",
    outcome="success",
    context={
        "latency": 245,
        "data_quality": "high",
        "source": "jupiter_api"
    }
)
```

This teaches ALOE:
- Jupiter is fast for prices
- API has high reliability
- Cache TTL should be X

## Integration with ARAS

ARAS uses SIL for reasoning:

```
ARAS Question: "Is this token trending?"
→ SIL fetches price data
→ SIL fetches volume data  
→ SIL fetches social mentions
→ ARAS analyzes trends
→ ARAS returns conclusion
```

## Error Handling

Source failures automatically handled:

| Error | Retry | Fallback |
|-------|-------|----------|
| Timeout | Yes, 3x | Next source |
| Rate limit | Wait + retry | Cached data |
| 404 | No | Report missing |
| Parse error | Validate | Request format fix |

## Performance Optimization

### Caching Strategy
```python
CACHE_RULES = {
    "price_data": {"ttl": 60, "source": "birdeye"},
    "metadata": {"ttl": 3600, "source": "jupiter"},
    "social": {"ttl": 300, "source": "moltbook"}
}
```

### Parallel Fetching
Independent sources fetched simultaneously:
```python
# Parallel API calls
results = await asyncio.gather(
    fetch_jupiter(token),
    fetch_birdeye(token),
    fetch_helius(token)
)
```

## Commands

| Command | Action |
|---------|--------|
| "Fetch X from Y" | Single source query |
| "Get full data on X" | Multi-source aggregation |
| "Monitor X" | Continuous polling |
| "Check cache for X" | Use cached data |
| "Clear cache" | Reset data cache |

## Storage

Intermediate data stored in:
```
memory/sil/
├── cache/          # Temporary data cache
├── raw/            # Unprocessed fetches
├── normalized/     # Cleaned data
└── metadata/       # Fetch logs
```

## Safety

### Protected Queries
SIL will NOT:
- Access private endpoints without auth
- Scrape rate-limited sites aggressively
- Fetch malicious URLs
- Exfiltrate sensitive data

### Rate Limit Respect
- Built-in delays between requests
- Respects robots.txt
- API key rotation
- Graceful degradation

## Example Outputs

### Token Data (Jupiter)
```json
{
  "address": "EPjFWdd5...",
  "symbol": "USDC",
  "name": "USD Coin",
  "decimals": 6,
  "price": 1.00,
  "volume_24h": 1548923400,
  "liquidity_usd": 892340000,
  "source": "jupiter",
  "timestamp": "2026-03-08T22:00:00Z"
}
```

### Solana Account (Helius)
```json
{
  "pubkey": "JBhVoSaX...",
  "lamports": 1234567,
  "owner": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
  "executable": false,
  "data": {...},
  "source": "helius_rpc"
}
```

### Social Sentiment
```json
{
  "mention_count": 47,
  "sentiment_score": 0.72,
  "trending": true,
  "top_keywords": ["bullish", "pump", "moon"],
  "sources": ["twitter", "discord", "moltbook"]
}
```
