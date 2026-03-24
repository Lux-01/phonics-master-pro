---
name: chart-analyzer
description: Analyze trading charts for patterns, support/resistance, and trading signals. Use when the user wants technical analysis of price charts, pattern detection (double bottom, cup & handle, triangles), support/resistance levels, RSI/MACD indicators, or trading signals from chart images. Works with screenshots of TradingView, MetaTrader, or any charting platform.
---

# Chart Analyzer Skill

Analyze trading charts for technical patterns and trading signals.

## Capabilities

- **Pattern Detection**: Double Bottom, Cup & Handle, Head & Shoulders, Triangles
- **Support/Resistance**: Dynamic level detection with touch counts
- **Indicators**: RSI, MACD, Trend Analysis
- **Trading Signals**: Entry, Stop Loss, Target prices with Risk:Reward ratios
- **Fibonacci Levels**: Auto-calculated retracements

## When to Use

Use this skill when the user:
- Shares a chart image/screenshot
- Asks for technical analysis
- Wants pattern detection
- Needs trading signals
- Requests support/resistance levels

## Workflow

1. **Get Chart Image**: User provides image path or screenshot
2. **Extract Price Data**: Use edge detection to extract price line
3. **Analyze Patterns**: Run pattern detection algorithms
4. **Calculate Indicators**: RSI, MACD, Trend
5. **Generate Signals**: Entry/Stop/Target with confidence scores
6. **Report Results**: Clear, actionable output

## Usage

### Analyzing a Chart

```python
# Load and analyze chart
from scripts.chart_analyzer import ChartAnalyzer

analyzer = ChartAnalyzer()
results = analyzer.analyze_image("path/to/chart.png")

# Results include:
# - Detected patterns
# - Support/resistance levels
# - Trading signals
# - Indicator values
```

### Pattern Detection

The analyzer detects:
- **Double Bottom**: W-shape reversal pattern
- **Cup & Handle**: Bullish continuation
- **Head & Shoulders**: Bearish reversal
- **Triangles**: Ascending, Descending, Symmetrical

### Output Format

```
📊 CHART ANALYSIS

Patterns Detected:
• Double Bottom (85% confidence)
  Entry: $45.20 | Stop: $42.00 | Target: $52.00
  Risk:Reward = 1:2.4

Support/Resistance:
• Support: $42.50 (3 touches)
• Resistance: $48.00 (2 touches)

Indicators:
• RSI: 42.5 (neutral)
• MACD: Bullish crossover
• Trend: Bullish (65% strength)

💡 SIGNAL: BUY
   Entry on neckline break above $45.20
```

## Technical Details

- Uses OpenCV for image processing
- Scipy for signal processing
- Supports any chart screenshot
- Works with all timeframes
