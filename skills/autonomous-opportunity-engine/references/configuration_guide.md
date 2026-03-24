# AOE Configuration Guide

## Basic Configuration

### Risk Tolerance
```yaml
risk_tolerance: moderate  # conservative / moderate / aggressive
```

**Conservative:** Only act on 90+ scores, always ask for confirmation
**Moderate:** Auto-act on 85+ for non-financial, ask for financial
**Aggressive:** Auto-act on 80+ when high confidence

### Auto-Action Rules

```yaml
auto_actions:
  # Financial - never auto-act
  crypto_trades: false
  token_purchases: false
  
  # Development - auto on high confidence
  security_patches: true
  dependency_updates: ask_first
  performance_optimizations: ask_first
  
  # Content - usually ask
  content_creation: ask_first
  social_posts: false
  
  # Research - auto on relevant
  deep_research: auto_if_relevant
  quick_scans: true
  
  # Network - always ask
  dm_responses: false
  collaboration_requests: false
```

### Scoring Thresholds

```yaml
scores:
  # Minimum to consider
  minimum_detect: 50
  
  # Minimum to add to queue
  minimum_queue: 60
  
  # Minimum to alert
  minimum_alert: 75
  
  # Minimum for auto-action (non-financial)
  auto_action: 85
  
  # Minimum for immediate alert
  urgent_alert: 90
```

## Scanner Configuration

### Market Scanner
```yaml
scanners:
  market:
    enabled: true
    frequency_minutes: 5
    priority: high
    
    # Detection criteria
    volume_spike_threshold: 3.0  # 3x average
    price_change_threshold: 0.20  # 20%
    new_token_age_hours: 2
    liquidity_change_threshold: 0.50  # 50%
    
    # Data sources
    sources:
      - dexscreener
      - birdeye
      - jupiter
      - pumpfun
```

### Whale Scanner
```yaml
  whale:
    enabled: true
    frequency_minutes: 2
    priority: high
    
    tracked_wallets:
      - address: "JBhVoSaX..."
        label: "Smart Money"
        importance: high
      - address: "..."
        label: "Dev Wallet"
        importance: high
    
    detection:
      min_buy_size_sol: 1.0
      multiple_buys_threshold: 4
      time_window: 30  # seconds
```

### Social Scanner
```yaml
  social:
    enabled: true
    frequency_minutes: 15
    priority: medium
    
    platforms:
      - moltbook
      - twitter
      - discord_channels:
        - "alpha-updates"
        - "trading-floor"
    
    detection:
      narrative_emerging_threshold: 10  # mentions/hour
      sentiment_shift_threshold: 0.2
      influencer_calls_threshold: 3
```

### Dev Scanner
```yaml
  dev:
    enabled: true
    frequency_hours: 6
    priority: medium
    
    tracking:
      - github_releases
      - npm_updates
      # - docker_hub
      # - api_changelogs
    
    detection:
      security_patch: immediate
      major_version: add_to_queue
      breaking_change: high_priority
      performance_gain_threshold: 0.20  # 20% improvement
```

## Scoring Weights

Customize how opportunities are scored:

```yaml
scoring_weights:
  potential: 0.25
  probability: 0.25
  risk: -0.20
  speed: 0.15
  effort: -0.10
  fit: 0.15
  alpha: 0.20
```

**Total must equal 1.0 (or adjust negative weights accordingly)**

## Watchlists

### Token Watchlist
```yaml
watchlists:
  tokens:
    - symbol: SOL
      address: "So111111..."
      alert_on_volume: true
      
    - symbol: JUP
      address: "JUPyiwrY..."
      narrative: DEX
      
    - symbol: BONK
      address: "DezXAZ8z..."
      risk_level: meme
```

### Narrative Watchlist
```yaml
  narratives:
    - name: "AI Agents"
      keywords: ["AI", "agent", "autonomous"]
      weight: 1.5  # Boost score for these
      
    - name: "DePIN"
      keywords: ["DePIN", "infrastructure", "hardware"]
      weight: 1.2
      
    - name: "Gaming"
      keywords: ["gamefi", "play", "gaming"]
      weight: 1.0
```

## Alert Configuration

### Alert Channels
```yaml
alerts:
  channels:
    immediate:
      type: telegram
      score_threshold: 85
      priority: high
      
    digest:
      type: telegram_daily
      score_threshold: 70
      time: "09:00"
      timezone: "Australia/Sydney"
      
    dashboard:
      type: web_dashboard
      score_threshold: 60
      access: always
```

### Quiet Hours
```yaml
  quiet_hours:
    enabled: true
    start: "23:00"
    end: "08:00"
    timezone: "Australia/Sydney"
    exceptions:  # Always alert for
      - score_95_plus: true
      - security_patches: true
      - critical_bugs: true
```

## Integration Settings

### ATS Integration
```yaml
integrations:
  autonomous_trading_strategist:
    enabled: true
    auto_analyze_scores: >= 80
    include_thesis: true
    risk_assessment: always
```

### LPM Integration
```yaml
  long_term_project_manager:
    enabled: true
    auto_create_tasks: >= 85
    include_analysis: true
    deadline_from_estimate: true
```

### AWB Integration
```yaml
  autonomous_workflow_builder:
    enabled: true
    auto_build: repeated_tasks_only
    min_repetitions: 3
```

## Performance Tuning

### Resource Limits
```yaml
performance:
  max_cpu_percent: 20
  max_memory_mb: 512
  
  # Throttling
  max_requests_per_minute: 60
  request_burst_limit: 10
  
  # Caching
  cache_ttl_minutes: 5
  max_cache_size_mb: 100
```

### Priority Queue
```yaml
queue_management:
  max_queue_size: 100
  auto_expire_hours: 72  # Remove stale opportunities
  highlight_top_n: 10
  
  priority_boost:
    - your_watchlist_tokens: +10
    - your_narratives: +5
    - high_time_sensitivity: +15
```

## Testing Configuration

### Test Mode
```yaml
test_mode:
  enabled: false
  simulate_only: true  # Detect but don't act
  log_all_decisions: true
  
  # Test scenarios
  scenarios:
    - simulate_token_launch
    - simulate_security_patch
    - simulate_content_gap
```

### Backtesting
```yaml
backtesting:
  enabled: false
  historical_data_days: 30
  opportunity_types:
    - tokens
    - dev_updates
    - content_gaps
```

## Example Full Config

```yaml
# /memory/aoe/config.yaml

user: Tem
risk_tolerance: moderate

auto_actions:
  crypto_analysis: true        # Auto-analyze high-score tokens
  token_trades: false          # Never auto-trade
  dev_patches: true            # Auto-create security tasks
  content: ask_first           # Ask before content

scores:
  minimum_detect: 50
  minimum_queue: 60
  minimum_alert: 75
  auto_action: 85
  urgent_alert: 90

scanners:
  market:
    enabled: true
    frequency_minutes: 5
    
  whale:
    enabled: true
    frequency_minutes: 2
    tracked_wallets:
      - "JBhVoSaX..."
      - "39azUYFW..."
      
  social:
    enabled: true
    frequency_minutes: 15
    
  dev:
    enabled: true
    frequency_hours: 6

watchlists:
  tokens: ["SOL", "JUP", "BONK", "WIF"]
  narratives: ["AI Agents", "DePIN"]

alerts:
  immediate:
    score_threshold: 85
    channels: [telegram]
    
  digest:
    score_threshold: 70
    time: "09:00"
    timezone: "Australia/Sydney"

quiet_hours:
  enabled: true
  start: "23:00"
  end: "08:00"
  timezone: "Australia/Sydney"
```
