#!/usr/bin/env python3
"""
Lux AI v2.0 - AI Learning System
Tracks trade outcomes, recognizes patterns, predicts future performance
"""

import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import statistics

# Database path
DB_PATH = "/home/skux/.openclaw/workspace/agents/lux_ai_v2/trade_history.db"
PATTERNS_FILE = "/home/skux/.openclaw/workspace/agents/lux_ai_v2/pattern_library.json"

class TradeDatabase:
    """SQLite database for trade history"""
    
    def __init__(self):
        self.conn = None
        self.init_db()
    
    def init_db(self):
        """Initialize database with tables"""
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH)
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_ca TEXT NOT NULL,
                symbol TEXT,
                entry_mcap REAL,
                exit_mcap REAL,
                entry_price REAL,
                exit_price REAL,
                entry_time TIMESTAMP,
                exit_time TIMESTAMP,
                grade TEXT,
                narrative TEXT,
                pnl_pct REAL,
                strategy TEXT,
                duration_hours REAL,
                exit_reason TEXT,
                success BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT UNIQUE,
                narrative TEXT,
                min_mcap REAL,
                max_mcap REAL,
                signals_json TEXT,
                win_rate REAL,
                avg_return REAL,
                total_trades INTEGER,
                last_seen TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
        print("✅ Trade database initialized")
    
    def log_trade(self, trade_data: Dict):
        """Log a completed trade"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO trades (
                token_ca, symbol, entry_mcap, exit_mcap, entry_price, exit_price,
                entry_time, exit_time, grade, narrative, pnl_pct, strategy,
                duration_hours, exit_reason, success
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trade_data.get('token_ca'),
            trade_data.get('symbol'),
            trade_data.get('entry_mcap'),
            trade_data.get('exit_mcap'),
            trade_data.get('entry_price'),
            trade_data.get('exit_price'),
            trade_data.get('entry_time'),
            trade_data.get('exit_time'),
            trade_data.get('grade'),
            trade_data.get('narrative'),
            trade_data.get('pnl_pct'),
            trade_data.get('strategy'),
            trade_data.get('duration_hours'),
            trade_data.get('exit_reason'),
            trade_data.get('pnl_pct', 0) > 0
        ))
        
        self.conn.commit()
        print(f"✅ Trade logged: {trade_data.get('symbol')} ({trade_data.get('pnl_pct'):+.1f}%)")
    
    def get_trade_stats(self) -> Dict:
        """Get overall trade statistics"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as wins,
                AVG(pnl_pct) as avg_pnl,
                AVG(CASE WHEN success THEN pnl_pct END) as avg_win,
                AVG(CASE WHEN NOT success THEN pnl_pct END) as avg_loss
            FROM trades
        """)
        
        result = cursor.fetchone()
        total = result[0] or 0
        wins = result[1] or 0
        
        return {
            'total_trades': total,
            'wins': wins,
            'losses': total - wins,
            'win_rate': (wins / total * 100) if total > 0 else 0,
            'avg_pnl': result[2] or 0,
            'avg_win': result[3] or 0,
            'avg_loss': result[4] or 0
        }
    
    def get_narrative_performance(self) -> List[Dict]:
        """Get performance by narrative"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 
                narrative,
                COUNT(*) as trades,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as wins,
                AVG(pnl_pct) as avg_pnl
            FROM trades
            WHERE narrative IS NOT NULL
            GROUP BY narrative
            ORDER BY avg_pnl DESC
        """)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'narrative': row[0],
                'trades': row[1],
                'wins': row[2],
                'win_rate': (row[2] / row[1] * 100) if row[1] > 0 else 0,
                'avg_pnl': row[3]
            })
        
        return results
    
    def get_grade_performance(self) -> List[Dict]:
        """Get performance by grade"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 
                grade,
                COUNT(*) as trades,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as wins,
                AVG(pnl_pct) as avg_pnl
            FROM trades
            WHERE grade IS NOT NULL
            GROUP BY grade
            ORDER BY avg_pnl DESC
        """)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'grade': row[0],
                'trades': row[1],
                'wins': row[2],
                'win_rate': (row[2] / row[1] * 100) if row[1] > 0 else 0,
                'avg_pnl': row[3]
            })
        
        return results

class PatternRecognizer:
    """Recognize and store successful trading patterns"""
    
    def __init__(self):
        self.patterns = self.load_patterns()
    
    def load_patterns(self) -> Dict:
        """Load pattern library"""
        try:
            with open(PATTERNS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {'patterns': []}
    
    def save_patterns(self):
        """Save pattern library"""
        os.makedirs(os.path.dirname(PATTERNS_FILE), exist_ok=True)
        with open(PATTERNS_FILE, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def detect_pattern(self, trade: Dict) -> Optional[str]:
        """Detect which pattern this trade matches"""
        for pattern in self.patterns.get('patterns', []):
            if self.matches_pattern(trade, pattern):
                return pattern['name']
        return None
    
    def matches_pattern(self, trade: Dict, pattern: Dict) -> bool:
        """Check if trade matches pattern criteria"""
        signals = pattern.get('signals', [])
        
        for signal in signals:
            metric = signal.get('metric')
            condition = signal.get('condition')
            value = signal.get('value')
            
            trade_value = self.get_trade_metric(trade, metric)
            
            if condition == '>' and not (trade_value > value):
                return False
            elif condition == '<' and not (trade_value < value):
                return False
            elif condition == '==' and not (trade_value == value):
                return False
        
        return True
    
    def get_trade_metric(self, trade: Dict, metric: str):
        """Get metric value from trade"""
        if metric == 'narrative':
            return trade.get('narrative', '')
        elif metric == 'grade':
            return trade.get('grade', '')
        elif metric == 'entry_mcap':
            return trade.get('entry_mcap', 0)
        elif metric == 'pnl_pct':
            return trade.get('pnl_pct', 0)
        return 0
    
    def learn_pattern(self, trades: List[Dict], pattern_name: str, signals: List[Dict]):
        """Learn new pattern from successful trades"""
        wins = [t for t in trades if t.get('pnl_pct', 0) > 0]
        
        if len(wins) < 5:  # Need minimum sample size
            return
        
        win_rate = len(wins) / len(trades)
        avg_return = statistics.mean([t.get('pnl_pct', 0) for t in wins])
        
        pattern = {
            'name': pattern_name,
            'signals': signals,
            'win_rate': win_rate,
            'avg_return': avg_return,
            'total_trades': len(trades),
            'last_seen': datetime.now().isoformat()
        }
        
        # Update or add
        existing = [p for p in self.patterns['patterns'] if p['name'] == pattern_name]
        if existing:
            existing[0].update(pattern)
        else:
            self.patterns['patterns'].append(pattern)
        
        self.save_patterns()
        print(f"✅ Pattern learned: {pattern_name} ({win_rate*100:.0f}% win rate)")

class PredictiveEngine:
    """Predict future performance based on historical data"""
    
    def __init__(self, db: TradeDatabase):
        self.db = db
    
    def predict_win_probability(self, token: Dict) -> Dict:
        """Predict win probability for a token"""
        cursor = self.db.conn.cursor()
        
        # Query similar tokens
        narrative = token.get('narrative', '')
        grade = token.get('grade', '')
        mcap = token.get('entry_mcap', 0)
        
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN success THEN 1 ELSE 0 END) as wins,
                   AVG(pnl_pct) as avg_pnl
            FROM trades
            WHERE narrative = ? OR grade = ?
        """, (narrative, grade))
        
        row = cursor.fetchone()
        total = row[0] or 0
        wins = row[1] or 0
        avg_pnl = row[2] or 0
        
        win_prob = (wins / total * 100) if total > 0 else 50
        
        return {
            'win_probability': win_prob,
            'similar_trades': total,
            'expected_return': avg_pnl,
            'confidence': min(total / 10, 1.0)  # 0-1 based on sample size
        }
    
    def get_optimal_entry_range(self, narrative: str) -> Dict:
        """Get optimal entry market cap range for a narrative"""
        cursor = self.db.conn.cursor()
        
        cursor.execute("""
            SELECT entry_mcap, pnl_pct
            FROM trades
            WHERE narrative = ? AND success = TRUE
            ORDER BY entry_mcap
        """, (narrative,))
        
        rows = cursor.fetchall()
        if not rows:
            return {}
        
        mcaps = [r[0] for r in rows]
        pnls = [r[1] for r in rows]
        
        return {
            'min_optimal': min(mcaps),
            'max_optimal': max(mcaps),
            'median': statistics.median(mcaps),
            'avg_pnl': statistics.mean(pnls)
        }
    
    def suggest_position_size(self, token: Dict, portfolio_value: float) -> float:
        """Suggest position size based on Kelly Criterion"""
        prediction = self.predict_win_probability(token)
        
        win_prob = prediction['win_probability'] / 100
        avg_return = prediction['expected_return'] / 100
        avg_loss = 0.07  # Assume 7% stop loss
        
        if win_prob <= 0 or avg_return <= 0:
            return portfolio_value * 0.01  # 1% minimum
        
        # Kelly formula
        b = avg_return / avg_loss
        q = 1 - win_prob
        kelly = (win_prob * b - q) / b
        
        # Use half-Kelly for safety
        safe_kelly = kelly * 0.5
        
        # Cap at 5% of portfolio per trade
        return min(safe_kelly, 0.05) * portfolio_value

class AILearningSystem:
    """Main AI learning system"""
    
    def __init__(self):
        self.db = TradeDatabase()
        self.patterns = PatternRecognizer()
        self.predictor = PredictiveEngine(self.db)
    
    def log_trade(self, trade: Dict):
        """Log trade and update patterns"""
        self.db.log_trade(trade)
        
        # Check if it matches existing pattern
        pattern_name = self.patterns.detect_pattern(trade)
        if pattern_name:
            print(f"🎯 Pattern match: {pattern_name}")
    
    def get_insights(self) -> Dict:
        """Get AI insights"""
        stats = self.db.get_trade_stats()
        narratives = self.db.get_narrative_performance()
        grades = self.db.get_grade_performance()
        
        return {
            'overall_stats': stats,
            'top_narratives': narratives[:5] if narratives else [],
            'grade_performance': grades,
            'patterns': self.patterns.patterns.get('patterns', []),
            'recommendations': self.generate_recommendations(stats, narratives)
        }
    
    def generate_recommendations(self, stats: Dict, narratives: List[Dict]) -> List[str]:
        """Generate trading recommendations"""
        recs = []
        
        if stats['win_rate'] < 60:
            recs.append("⚠️ Win rate below 60% - consider tightening entry criteria")
        
        if stats['avg_pnl'] < 0.10:
            recs.append("📊 Avg PnL below 10% - optimize exit strategy")
        
        if narratives and len(narratives) > 0:
            top = narratives[0]
            recs.append(f"🎯 Focus on '{top['narrative']}' narrative ({top['win_rate']:.0f}% win rate)")
        
        recs.append("💡 Keep trade log updated for better predictions")
        
        return recs
    
    def analyze_token(self, token: Dict) -> Dict:
        """Analyze token with AI predictions"""
        prediction = self.predictor.predict_win_probability(token)
        entry_range = self.predictor.get_optimal_entry_range(token.get('narrative', ''))
        position_size = self.predictor.suggest_position_size(token, 2.0)  # 2 SOL portfolio
        
        return {
            'win_probability': prediction['win_probability'],
            'expected_return': prediction['expected_return'],
            'confidence': prediction['confidence'],
            'optimal_entry': entry_range,
            'suggested_position': position_size,
            'grade': 'A' if prediction['win_probability'] > 70 else 
                    'B' if prediction['win_probability'] > 50 else 'C'
        }

def demo():
    """Demo the AI learning system"""
    print("="*70)
    print("🧠 Lux AI v2.0 - Learning System Demo")
    print("="*70)
    print()
    
    ai = AILearningSystem()
    
    # Simulate logging some trades
    print("📊 Simulating trade history...")
    
    sample_trades = [
        {
            'token_ca': 'abc123',
            'symbol': 'AI_ALPHA',
            'narrative': 'ai_agent',
            'grade': 'A+',
            'entry_mcap': 500000,
            'pnl_pct': 0.25,
            'success': True
        },
        {
            'token_ca': 'def456',
            'symbol': 'MEME_DOG',
            'narrative': 'meme',
            'grade': 'A',
            'entry_mcap': 300000,
            'pnl_pct': -0.05,
            'success': False
        },
        {
            'token_ca': 'ghi789',
            'symbol': 'AI_BETA',
            'narrative': 'ai_agent',
            'grade': 'A+',
            'entry_mcap': 600000,
            'pnl_pct': 0.35,
            'success': True
        }
    ]
    
    for trade in sample_trades:
        ai.log_trade(trade)
    
    # Get insights
    print("\n" + "="*70)
    print("📈 AI INSIGHTS")
    print("="*70)
    
    insights = ai.get_insights()
    
    stats = insights['overall_stats']
    print(f"\\nOverall Performance:")
    print(f"  Total Trades: {stats['total_trades']}")
    print(f"  Win Rate: {stats['win_rate']:.1f}%")
    print(f"  Avg PnL: {stats['avg_pnl']*100:+.1f}%")
    print(f"  Avg Win: {stats['avg_win']*100:+.1f}%")
    print(f"  Avg Loss: {stats['avg_loss']*100:.1f}%")
    
    if insights['top_narratives']:
        print(f"\\nTop Narratives:")
        for n in insights['top_narratives']:
            print(f"  {n['narrative']}: {n['win_rate']:.0f}% win rate ({n['trades']} trades)")
    
    print(f"\\nRecommendations:")
    for rec in insights['recommendations']:
        print(f"  {rec}")
    
    # Analyze a new token
    print("\n" + "="*70)
    print("🔮 TOKEN PREDICTION")
    print("="*70)
    
    new_token = {
        'token_ca': 'xyz999',
        'symbol': 'AI_GAMMA',
        'narrative': 'ai_agent',
        'entry_mcap': 450000,
        'grade': 'A+'
    }
    
    analysis = ai.analyze_token(new_token)
    print(f"\\nToken: AI_GAMMA")
    print(f"  Win Probability: {analysis['win_probability']:.1f}%")
    print(f"  Expected Return: {analysis['expected_return']*100:+.1f}%")
    print(f"  Confidence: {analysis['confidence']*100:.0f}%")
    print(f"  Suggested Position: {analysis['suggested_position']:.3f} SOL")
    print(f"  AI Grade: {analysis['grade']}")
    
    print("\n✅ AI Learning System ready!")

if __name__ == "__main__":
    demo()
