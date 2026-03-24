---
name: integration-orchestrator
tier: 5
type: integration-layer
status: active
description: Coordinates cross-skill workflows, monitors health, and triggers workflows across the skill ecosystem. Now includes API wrapper generation, data transformation, and compatibility layers for new services.
---

# Integration Orchestrator Skill

Coordinates cross-skill workflows, monitors health, and triggers workflows across the skill ecosystem.

## Purpose

The Integration Orchestrator acts as the central nervous system for all skills, ensuring:
- Skills are properly configured and healthy
- Periodic workflows run on schedule
- State is maintained across sessions
- Cross-skill dependencies are coordinated

## Commands

```bash
# Run weekly skill activation audit
python integration_orchestrator.py audit

# Run monthly income review
python integration_orchestrator.py income

# Quick health check of all skills
python integration_orchestrator.py health

# Initialize state files
python integration_orchestrator.py init

# Run full orchestration cycle
python integration_orchestrator.py

# Generate API wrapper (NEW)
python integration_orchestrator.py generate-wrapper --api-url URL --output-dir ./wrappers/

# Test integration (NEW)
python integration_orchestrator.py test-integration --config integration.json
```

## State Files

- `memory/skill_activation_state.json` - Tracks active/dormant skills
- `memory/income_streams.json` - Tracks revenue streams and MRR

## Cron Schedule

- **Weekly Audit**: Sundays at 9:00 AM (every 604800000ms)
- **Monthly Review**: 1st of month at 9:00 AM (every 2592000000ms ≈ 30 days)

## Architecture

```
Integration Orchestrator
├── Load Skill Configs (from skills/)
├── Monitor Health (check each skill)
├── Update State (skill_activation_state.json)
├── Trigger Workflows (as needed)
└── Update Income (income_streams.json)
```

## Error Handling

- Missing state files → create with defaults
- API failures → retry with backoff
- Empty skill lists → log warning
- Invalid JSON → fallback to defaults

## ACA Compliance

This skill implements all 7 ACA engineering steps:
1. Requirements: Coordinates workflows
2. Architecture: Modular design with clear interfaces
3. Data Flow: State files → managers → updates
4. Edge Cases: Defaults for missing files
5. Tool Constraints: Python 3.10+, JSON persistence
6. Error Handling: Try/except with logging
7. Testing: Self-test on init

---

# 🔌 Integration Compatibility Engine (ICE)

**"Makes APIs play nice together."**

Automatically generates API wrappers, data transformers, and integration layers for new services.

## Capabilities

- **API wrapper generation:** Auto-build Python client
- **Data transformation:** Convert between formats
- **Compatibility layers:** Bridge different systems
- **Auth handling:** Integrate various auth methods
- **Rate limiting:** Built-in throttling

## Supported APIs

- REST APIs (OpenAPI/Swagger)
- GraphQL
- WebSocket
- gRPC
- Custom protocols

## API Wrapper Generation

### Auto-Generate from OpenAPI
```bash
# Analyze API specification
python3 ice.py --analyze-api "https://api.example.com/openapi.json"

# Generate Python wrapper
python3 ice.py --generate-wrapper \
  --api-url "https://api.example.com" \
  --spec "https://api.example.com/openapi.json" \
  --output-dir ./wrappers/example_api/ \
  --auth-type bearer
```

### Generated Wrapper Structure
```
wrappers/
└── example_api/
    ├── __init__.py
    ├── client.py          # Main API client
    ├── auth.py            # Authentication handlers
    ├── models.py          # Data models
    ├── transformers.py    # Data transformations
    └── tests/
        └── test_client.py
```

### Generated Client Example
```python
# Generated Python client
from wrappers.example_api import ExampleClient

client = ExampleClient(
    base_url="https://api.example.com",
    auth_token="your_token"
)

# Auto-generated methods from API spec
users = client.users.list(limit=10)
user = client.users.get(id=123)
new_user = client.users.create(name="John", email="john@example.com")
```

## Data Transformation

### Schema Mapping
```python
# Transform data between formats
transformer = DataTransformer()

# Map source → target
mapping = {
    "user_name": "name",
    "user_email": "email",
    "created_at": "registration_date",
    "is_active": "status"  # With value transformation
}

# Transform with value conversion
result = transformer.transform(
    source_data,
    mapping=mapping,
    converters={
        "status": lambda x: "active" if x else "inactive"
    }
)
```

### Format Converters
```python
# JSON ↔ XML
xml_data = transformer.json_to_xml(json_data)
json_data = transformer.xml_to_json(xml_data)

# CSV ↔ JSON
csv_data = transformer.json_to_csv(records)
records = transformer.csv_to_json(csv_data)

# Protocol Buffers ↔ JSON
pb_message = transformer.json_to_protobuf(json_data, schema)
json_data = transformer.protobuf_to_json(pb_message)
```

## Compatibility Layers

### Bridge Different Systems
```python
# Create compatibility layer between systems
bridge = CompatibilityBridge()

# System A (SOAP/Enterprise) ↔ System B (REST/Modern)
bridge.add_adapter("sap", SAPAdapter())
bridge.add_adapter("modern", RESTAdapter())

# Route and transform
result = bridge.route(
    from_system="sap",
    to_system="modern",
    data=sap_data,
    transform_rules=modern_rules
)
```

### Authentication Integration
```python
# Handle various auth methods
auth_handlers = {
    "api_key": APIKeyAuth(),
    "oauth2": OAuth2Auth(),
    "bearer": BearerTokenAuth(),
    "basic": BasicAuth(),
    "custom": CustomAuth()
}

# Auto-detect and configure
auth = auth_handlers.detect(api_spec)
client = Client(auth=auth, **config)
```

## Rate Limiting & Throttling

### Built-in Rate Limiting
```python
# Configure rate limits
limiter = RateLimiter(
    requests_per_second=10,
    burst_size=20,
    retry_after="429"  # Respect server's Retry-After header
)

# Use with client
client = Client(rate_limiter=limiter)
```

### Adaptive Throttling
```python
# Automatically adjust based on API response
throttler = AdaptiveThrottler(
    initial_rps=10,
    min_rps=1,
    max_rps=100,
    backoff_factor=2
)

# Monitors responses and adjusts
# 429/503 → decrease rate
# 200 OK → slowly increase rate
```

## Integration Testing

### Automated Tests
```python
# Test integration before deployment
runner = IntegrationTestRunner()

# Load test config
config = {
    "api": "https://api.example.com",
    "tests": [
        {"method": "GET", "endpoint": "/users", "expect": 200},
        {"method": "POST", "endpoint": "/users", "data": {...}, "expect": 201},
        {"method": "GET", "endpoint": "/users/99999", "expect": 404}
    ]
}

# Run tests
results = runner.run(config)
# Report: 3/3 passed
```

### Contract Testing
```python
# Ensure API compatibility on updates
contract = ContractTest()

# Define expected API behavior
contract.expect("/users", methods=["GET", "POST"])
contract.expect("/users/{id}", methods=["GET", "PUT", "DELETE"])
contract.expect_schema("User", required=["id", "name", "email"])

# Validate against actual API
violations = contract.validate(api_spec)
```

## Usage Examples

### Generate Wrapper for New API
```bash
# New Solana DEX API
python3 ice.py --generate-wrapper \
  --api-url "https://api.jupiter.exchange" \
  --spec "https://docs.jup.ag/openapi.json" \
  --output-dir ./wrappers/jupiter/ \
  --auth-type bearer

# Use generated wrapper
from wrappers.jupiter import JupiterClient

jupiter = JupiterClient(token=os.getenv("JUPITER_API_KEY"))
quote = jupiter.swap.quote(
    input_mint="So11111111111111111111111111111111111111112",
    output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    amount=1000000000
)
```

### Transform Data Between Systems
```python
# Exchange A data → Exchange B format
from integration_orchestrator import DataTransformer

transformer = DataTransformer()

order_a = {
    "symbol": "SOL-USDC",
    "side": "buy",
    "quantity": "1.5",
    "price": "150.00"
}

order_b = transformer.transform(
    order_a,
    mapping={
        "symbol": "market_id",
        "side": "direction",
        "quantity": "size",
        "price": "limit_price"
    },
    converters={
        "market_id": lambda x: x.replace("-", "_"),
        "direction": str.upper
    }
)
# Result: {"market_id": "SOL_USDC", "direction": "BUY", ...}
```

## Integration Commands

| Command | Action |
|---------|--------|
| `analyze-api URL` | Analyze OpenAPI/Swagger spec |
| `generate-wrapper` | Create Python API client |
| `test-integration` | Run integration tests |
| `transform-data` | Convert between formats |
| `validate-contract` | Check API compatibility |
| `list-wrappers` | Show available wrappers |

## Benefits of Integrated ICE

1. **Faster Integration:** Auto-generate code instead of writing by hand
2. **Fewer Bugs:** Generated code follows spec exactly
3. **Easy Updates:** Regenerate when API changes
4. **Standardization:** Consistent interface across all APIs
5. **Testing:** Built-in integration validation
