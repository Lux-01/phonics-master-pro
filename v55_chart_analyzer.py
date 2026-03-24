#!/usr/bin/env python3
"""
Solana Alpha Hunter v5.5 - Chart Analysis Edition
Adds: 15m candle TA, breakout detection, pattern recognition
Integrates: v5.4 fundamentals + chart analysis
"""

import sys
import os
sys.path.insert(0, '/home/skux/.openclaw/workspace')

from chart_analyzer import ChartAnalyzer, ChartSignals
import json
from typing import Tuple, List

def calculate_combined_grade_v55(fundamentals_grade: str, fundamentals_score: int, 
                                  chart_score: int, chart_signals: ChartSignals) -> Tuple[str, int, List]:
    """
    Combine v5.4 fundamentals with v5.5 chart analysis
    Returns: (final_grade, total_score, reasons)
    """
    total_score = fundamentals_score + chart_score
    reasons = []
    
    # Grade thresholds
    if total_score >= 22:
        grade = "A+"
    elif total_score >= 18:
        grade = "A"
    elif total_score >= 15:
        grade = "A-"
    elif total_score >= 12:
        grade = "B+"
    elif total_score >= 10:
        grade = "B"
    else:
        grade = fundamentals_grade if fundamentals_grade else "C"
    
    # Chart-based modifiers
    if chart_signals.breakout_detected:
        if grade not in ["A+", "A"]:
            grade = "A"  # Upgrade on breakout
        reasons.append("🚀 BREAKOUT detected")
    
    if chart_signals.breakdown_detected:
        grade = "B-"  # Downgrade on breakdown
        reasons.append("⚠️ BREAKDOWN - Wait")
    
    if chart_signals.rsi > 80:
        grade = max(grade, "B+")  # Cap grade on extreme overbought
        reasons.append("🔥 Overbought - take profit zone")
    
    # Oscillator detection - mean reversion opportunities
    if chart_signals.oscillator_detected:
        if grade not in ["A+", "A"]:
            grade = min(grade, "A")  # Upgrade for range-bound mean reversion
        if chart_signals.oscillator_score >= 8:
            reasons.append(f"🔄 STRONG OSCILLATOR ({chart_signals.range_pct:.1f}% range, {chart_signals.sr_touches} touches)")
        else:
            reasons.append(f"🔄 Oscillator detected ({chart_signals.range_pct:.1f}% range)")
    
    return grade, total_score, reasons

def analyze_with_charts(token_data: dict) -> dict:
    """Full v5.5 analysis with charts"""
    ca = token_data.get('ca')
    
    print(f"\n📊 v5.5 Chart Analysis for {ca[:20]}...")
    
    # Initialize chart analyzer
    analyzer = ChartAnalyzer(timeframe='15m')
    
    # Get chart signals
    signals, chart_score, analysis = analyzer.analyze_token_chart(ca)
    
    # Store chart data
    token_data['chart_signals'] = {
        'rsi': signals.rsi,
        'ema_9': signals.ema_9,
        'ema_21': signals.ema_21,
        'vwap': signals.vwap,
        'support': signals.support,
        'resistance': signals.resistance,
        'trend': signals.trend,
        'breakout': signals.breakout_detected,
        'breakdown': signals.breakdown_detected,
        'consolidating': signals.consolidating,
        'volume_trend': signals.volume_trend,
        'chart_score': chart_score,
        'analysis': analysis,
        'oscillator': {
            'detected': signals.oscillator_detected,
            'score': signals.oscillator_score,
            'range_pct': signals.range_pct,
            'sr_touches': signals.sr_touches
        }
    }
    
    # Calculate combined grade
    fundamentals_grade = token_data.get('grade', 'F')
    fundamentals_score = token_data.get('score', 0)
    
    final_grade, total_score, reasons = calculate_combined_grade_v55(
        fundamentals_grade, fundamentals_score, chart_score, signals
    )
    
    token_data['grade_v55'] = final_grade
    token_data['score_v55'] = total_score
    token_data['chart_reasons'] = reasons
    
    print(f"\n🎯 v5.5 Combined Result:")
    print(f"   Fundamentals: {fundamentals_grade} ({fundamentals_score}/20)")
    print(f"   Chart: {chart_score}/10")
    print(f"   Total: {total_score}/30")
    print(f"   Final Grade: {final_grade}")
    
    if reasons:
        print(f"   Signals: {', '.join(reasons)}")
    
    return token_data

def enhance_v54_results_with_charts():
    """Enhance existing v5.4 results with chart analysis"""
    print("=" * 80)
    print("🚀 SOLANA ALPHA HUNTER v5.5 - Chart Analysis Edition")
    print("📊 Timeframe: 15m candles | RSI | EMA | VWAP | Breakout")
    print("=" * 80)
    print()
    
    # Load v5.4 results
    try:
        with open('/home/skux/.openclaw/workspace/alpha_results_v54.json', 'r') as f:
            v54_results = json.load(f)
    except:
        print("❌ No v5.4 results found. Run v5.4 first.")
        return
    
    print(f"Analyzing {len(v54_results)} tokens from v5.4...")
    
    enhanced = []
    for token in v54_results:
        # Only chart Grade A and B tokens
        current_grade = token.get('grade', '')
        if 'A' in current_grade or 'B' in current_grade:
            try:
                enhanced_token = analyze_with_charts(token)
                enhanced.append(enhanced_token)
            except Exception as e:
                print(f"  ⚠️ Chart analysis failed: {e}")
                enhanced.append(token)
        else:
            enhanced.append(token)
    
    # Save v5.5 results
    with open('/home/skux/.openclaw/workspace/alpha_results_v55.json', 'w') as f:
        json.dump(enhanced, f, indent=2)
    
    print()
    print("=" * 80)
    print(f"✅ v5.5 Analysis Complete")
    print(f"📊 Enhanced: {len(enhanced)} tokens with chart data")
    print(f"💾 Saved: alpha_results_v55.json")
    print("=" * 80)
    
    # Show top results
    print("\n🏆 TOP CHART SETUPS:")
    
    chart_setups = sorted(
        [t for t in enhanced if t.get('chart_signals', {}).get('breakout')],
        key=lambda x: x.get('score_v55', 0),
        reverse=True
    )[:5]
    
    for i, token in enumerate(chart_setups, 1):
        name = token.get('name', '?')
        grade = token.get('grade_v55', '?')
        score = token.get('score_v55', 0)
        signals = token.get('chart_signals', {})
        
        print(f"\n{i}. {name} | Grade {grade} ({score}/30)")
        print(f"   RSI: {signals.get('rsi')} | Trend: {signals.get('trend')}")
        print(f"   🚀 Breakout: {signals.get('breakout')}")
        print(f"   📈 Above VWAP: {signals.get('vwap') and token.get('mcap',0) > signals.get('vwap',0)}")

if __name__ == "__main__":
    enhance_v54_results_with_charts()
