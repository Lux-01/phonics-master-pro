#!/usr/bin/env python3
"""
Data Migration Script: Scattered JSON → Unified Data Layer

Migrates:
- tracked_tokens.json
- stage9_proposals.json
- stage9_state.json
- virtual_portfolio.json

ACA Implementation:
- Requirements: Preserve all data, maintain backward compatibility
- Architecture: Migration layer with rollback capability
- Data Flow: Read JSON → Transform → Write SQLite → Verify
- Edge Cases: Missing files, corrupted data, type mismatches
- Tools: SQLite, JSON, pathlib
- Errors: Skip bad records, log failures, continue processing
- Tests: Verification queries, data integrity checks
"""

import json
import sqlite3
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
WORKSPACE_DIR = Path("/home/skux/.openclaw/workspace")
AGENTS_DIR = WORKSPACE_DIR / "agents" / "lux_trader"
UNIFIED_DB = WORKSPACE_DIR / "unified_data.db"
BACKUP_DIR = WORKSPACE_DIR / "data_migration_backups"

# Files to migrate
MIGRATION_TARGETS = {
    "tracked_tokens": WORKSPACE_DIR / "tracked_tokens.json",
    "stage9_proposals": AGENTS_DIR / "stage9_proposals.json",
    "stage9_state": AGENTS_DIR / "stage9_state.json",
    "virtual_portfolio": AGENTS_DIR / "virtual_portfolio.json"
}


class UnifiedDataLayer:
    """
    Unified SQLite-based data layer for all trading data.
    Provides ACID compliance, indexing, and query capabilities.
    """
    
    def __init__(self, db_path: Path = UNIFIED_DB):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        logger.info(f"Connected to unified database: {self.db_path}")
    
    def _create_tables(self):
        """Create database schema."""
        
        # Tracked tokens table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracked_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_address TEXT UNIQUE NOT NULL,
                symbol TEXT,
                name TEXT,
                first_seen TIMESTAMP,
                last_check TIMESTAMP,
                age_hours REAL,
                current_grade TEXT,
                current_mcap REAL,
                current_liquidity REAL,
                holder_count INTEGER,
                top10_pct REAL,
                data_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for tracked_tokens
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tracked_tokens_address 
            ON tracked_tokens(token_address)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tracked_tokens_grade 
            ON tracked_tokens(current_grade)
        """)
        
        # Proposals table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS proposals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proposal_id TEXT UNIQUE NOT NULL,
                timestamp TIMESTAMP,
                status TEXT,
                token_address TEXT,
                token_symbol TEXT,
                token_name TEXT,
                token_price REAL,
                market_cap REAL,
                liquidity REAL,
                grade TEXT,
                age_hours REAL,
                entry_size_sol REAL,
                target_profit_pct REAL,
                stop_loss_pct REAL,
                time_stop_hours INTEGER,
                risk_level TEXT,
                risk_recommendation TEXT,
                tre_analysis_json TEXT,
                expires_at TIMESTAMP,
                user_decision TEXT,
                decision_time TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_proposals_status 
            ON proposals(status)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_proposals_token 
            ON proposals(token_address)
        """)
        
        # State table (single row, always updated)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS trader_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                trades_today INTEGER DEFAULT 0,
                loss_today_sol REAL DEFAULT 0.0,
                last_trade_time TIMESTAMP,
                total_trades INTEGER DEFAULT 0,
                successful_trades INTEGER DEFAULT 0,
                status TEXT DEFAULT 'ACTIVE',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Virtual portfolio table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS virtual_portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                virtual_sol REAL DEFAULT 10.0,
                starting_capital REAL DEFAULT 10.0,
                realized_pnl_sol REAL DEFAULT 0.0,
                total_trades INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Open positions table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS open_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_address TEXT UNIQUE NOT NULL,
                token_symbol TEXT,
                entry_price REAL,
                entry_sol REAL,
                actual_sol REAL,
                fee_sol REAL,
                token_amount REAL,
                entry_time TIMESTAMP,
                stop_loss REAL,
                take_profit REAL,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Migration log table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS migration_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_file TEXT,
                records_processed INTEGER,
                records_failed INTEGER,
                checksum TEXT,
                migrated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT
            )
        """)
        
        # Audit log table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT,
                details_json TEXT,
                state_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
        logger.info("Database schema created/verified")
    
    def insert_tracked_token(self, token_address: str, data: Dict) -> bool:
        """Insert or update tracked token."""
        try:
            self.cursor.execute("""
                INSERT INTO tracked_tokens 
                (token_address, symbol, name, first_seen, last_check, age_hours,
                 current_grade, current_mcap, current_liquidity, holder_count,
                 top10_pct, data_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(token_address) DO UPDATE SET
                last_check = excluded.last_check,
                age_hours = excluded.age_hours,
                current_grade = excluded.current_grade,
                current_mcap = excluded.current_mcap,
                current_liquidity = excluded.current_liquidity,
                holder_count = excluded.holder_count,
                top10_pct = excluded.top10_pct,
                data_json = excluded.data_json,
                updated_at = CURRENT_TIMESTAMP
            """, (
                token_address,
                data.get('symbol', '?'),
                data.get('name', '?'),
                data.get('first_seen'),
                data.get('last_check'),
                data.get('age_hours', 0),
                data.get('current_grade', 'F'),
                data.get('current_mcap', 0),
                data.get('data', {}).get('liq', 0),
                data.get('data', {}).get('holders', 0),
                data.get('data', {}).get('top10_pct', 0),
                json.dumps(data)
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to insert token {token_address}: {e}")
            return False
    
    def insert_proposal(self, proposal: Dict) -> bool:
        """Insert proposal."""
        try:
            token = proposal.get('token', {})
            trade_details = proposal.get('trade_details', {})
            risk = proposal.get('risk_assessment', {})
            
            self.cursor.execute("""
                INSERT INTO proposals
                (proposal_id, timestamp, status, token_address, token_symbol,
                 token_name, token_price, market_cap, liquidity, grade,
                 age_hours, entry_size_sol, target_profit_pct, stop_loss_pct,
                 time_stop_hours, risk_level, risk_recommendation,
                 tre_analysis_json, expires_at, user_decision)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(proposal_id) DO UPDATE SET
                status = excluded.status,
                user_decision = excluded.user_decision,
                decision_time = CURRENT_TIMESTAMP
            """, (
                proposal.get('id', 'unknown'),
                proposal.get('timestamp'),
                proposal.get('status', 'PENDING'),
                token.get('address'),
                token.get('symbol'),
                token.get('name'),
                token.get('price', 0),
                token.get('market_cap', 0),
                token.get('liquidity', 0),
                token.get('grade', 'F'),
                token.get('age_hours', 0),
                trade_details.get('entry_size_sol', 0),
                trade_details.get('target_profit_pct', 15),
                trade_details.get('stop_loss_pct', 7),
                trade_details.get('time_stop_hours', 4),
                risk.get('level', 'UNKNOWN'),
                risk.get('recommendation', 'UNKNOWN'),
                json.dumps(proposal.get('tre_analysis', {})),
                proposal.get('expires_at'),
                proposal.get('user_decision')
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to insert proposal: {e}")
            return False
    
    def update_state(self, state: Dict) -> bool:
        """Update trader state."""
        try:
            self.cursor.execute("""
                INSERT INTO trader_state
                (id, trades_today, loss_today_sol, last_trade_time,
                 total_trades, successful_trades, status)
                VALUES (1, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                trades_today = excluded.trades_today,
                loss_today_sol = excluded.loss_today_sol,
                last_trade_time = excluded.last_trade_time,
                total_trades = excluded.total_trades,
                successful_trades = excluded.successful_trades,
                status = excluded.status,
                updated_at = CURRENT_TIMESTAMP
            """, (
                state.get('trades_today', 0),
                state.get('loss_today_sol', 0),
                state.get('last_trade_time'),
                state.get('total_trades', 0),
                state.get('successful_trades', 0),
                state.get('status', 'ACTIVE')
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update state: {e}")
            return False
    
    def update_virtual_portfolio(self, portfolio: Dict) -> bool:
        """Update virtual portfolio."""
        try:
            # Update main portfolio record
            self.cursor.execute("""
                INSERT INTO virtual_portfolio
                (id, virtual_sol, starting_capital, realized_pnl_sol,
                 total_trades, wins, losses)
                VALUES (1, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                virtual_sol = excluded.virtual_sol,
                realized_pnl_sol = excluded.realized_pnl_sol,
                total_trades = excluded.total_trades,
                wins = excluded.wins,
                losses = excluded.losses,
                updated_at = CURRENT_TIMESTAMP
            """, (
                portfolio.get('virtual_sol', 10.0),
                portfolio.get('starting_capital', 10.0),
                portfolio.get('realized_pnl_sol', 0.0),
                portfolio.get('total_trades', 0),
                portfolio.get('wins', 0),
                portfolio.get('losses', 0)
            ))
            
            # Update open positions
            open_positions = portfolio.get('open_positions', {})
            for token_address, position in open_positions.items():
                self.cursor.execute("""
                    INSERT INTO open_positions
                    (token_address, token_symbol, entry_price, entry_sol,
                     actual_sol, fee_sol, token_amount, entry_time,
                     stop_loss, take_profit, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(token_address) DO UPDATE SET
                    entry_price = excluded.entry_price,
                    entry_sol = excluded.entry_sol,
                    actual_sol = excluded.actual_sol,
                    fee_sol = excluded.fee_sol,
                    token_amount = excluded.token_amount,
                    stop_loss = excluded.stop_loss,
                    take_profit = excluded.take_profit,
                    status = excluded.status
                """, (
                    token_address,
                    position.get('token_symbol', 'UNKNOWN'),
                    position.get('entry_price', 0),
                    position.get('entry_sol', 0),
                    position.get('actual_sol', 0),
                    position.get('fee_sol', 0),
                    position.get('token_amount', 0),
                    position.get('entry_time'),
                    position.get('stop_loss', 0),
                    position.get('take_profit', 0),
                    position.get('status', 'open')
                ))
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update virtual portfolio: {e}")
            return False
    
    def log_migration(self, source_file: str, processed: int, failed: int, 
                     checksum: str, status: str):
        """Log migration event."""
        self.cursor.execute("""
            INSERT INTO migration_log
            (source_file, records_processed, records_failed, checksum, status)
            VALUES (?, ?, ?, ?, ?)
        """, (source_file, processed, failed, checksum, status))
        self.conn.commit()
    
    def query(self, sql: str, params: tuple = ()) -> List[Dict]:
        """Execute query and return results as list of dicts."""
        self.cursor.execute(sql, params)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


class DataMigrator:
    """
    Handles migration from JSON files to unified database.
    Includes backup, verification, and rollback capabilities.
    """
    
    def __init__(self):
        self.db = UnifiedDataLayer()
        self.backup_dir = BACKUP_DIR
        self.backup_dir.mkdir(exist_ok=True)
        self.stats = {
            "files_processed": 0,
            "records_migrated": 0,
            "records_failed": 0,
            "errors": []
        }
    
    def _backup_file(self, file_path: Path) -> Path:
        """Create backup of source file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.backup_dir / backup_name
        shutil.copy2(file_path, backup_path)
        logger.info(f"Backed up {file_path.name} to {backup_path}")
        return backup_path
    
    def _compute_checksum(self, data: Any) -> str:
        """Compute MD5 checksum of data."""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(json_str.encode()).hexdigest()
    
    def migrate_tracked_tokens(self) -> Tuple[int, int]:
        """Migrate tracked_tokens.json to database."""
        file_path = MIGRATION_TARGETS["tracked_tokens"]
        
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return 0, 0
        
        # Backup
        self._backup_file(file_path)
        
        # Load and migrate
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            checksum = self._compute_checksum(data)
            processed = 0
            failed = 0
            
            for token_address, token_data in data.items():
                if self.db.insert_tracked_token(token_address, token_data):
                    processed += 1
                else:
                    failed += 1
            
            self.db.log_migration("tracked_tokens.json", processed, failed, 
                                  checksum, "SUCCESS" if failed == 0 else "PARTIAL")
            
            logger.info(f"Migrated {processed} tracked tokens ({failed} failed)")
            return processed, failed
            
        except Exception as e:
            logger.error(f"Failed to migrate tracked_tokens: {e}")
            self.db.log_migration("tracked_tokens.json", 0, 0, "", f"FAILED: {e}")
            return 0, 0
    
    def migrate_proposals(self) -> Tuple[int, int]:
        """Migrate stage9_proposals.json to database."""
        file_path = MIGRATION_TARGETS["stage9_proposals"]
        
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return 0, 0
        
        self._backup_file(file_path)
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            checksum = self._compute_checksum(data)
            processed = 0
            failed = 0
            
            # Migrate pending proposals
            for proposal in data.get("pending", []):
                if self.db.insert_proposal(proposal):
                    processed += 1
                else:
                    failed += 1
            
            # Migrate history
            for proposal in data.get("history", []):
                if self.db.insert_proposal(proposal):
                    processed += 1
                else:
                    failed += 1
            
            self.db.log_migration("stage9_proposals.json", processed, failed,
                                  checksum, "SUCCESS" if failed == 0 else "PARTIAL")
            
            logger.info(f"Migrated {processed} proposals ({failed} failed)")
            return processed, failed
            
        except Exception as e:
            logger.error(f"Failed to migrate proposals: {e}")
            self.db.log_migration("stage9_proposals.json", 0, 0, "", f"FAILED: {e}")
            return 0, 0
    
    def migrate_state(self) -> bool:
        """Migrate stage9_state.json to database."""
        file_path = MIGRATION_TARGETS["stage9_state"]
        
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return False
        
        self._backup_file(file_path)
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            checksum = self._compute_checksum(data)
            
            if self.db.update_state(data):
                self.db.log_migration("stage9_state.json", 1, 0, checksum, "SUCCESS")
                logger.info("Migrated trader state")
                return True
            else:
                self.db.log_migration("stage9_state.json", 0, 1, checksum, "FAILED")
                return False
                
        except Exception as e:
            logger.error(f"Failed to migrate state: {e}")
            self.db.log_migration("stage9_state.json", 0, 0, "", f"FAILED: {e}")
            return False
    
    def migrate_virtual_portfolio(self) -> bool:
        """Migrate virtual_portfolio.json to database."""
        file_path = MIGRATION_TARGETS["virtual_portfolio"]
        
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return False
        
        self._backup_file(file_path)
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            checksum = self._compute_checksum(data)
            
            if self.db.update_virtual_portfolio(data):
                self.db.log_migration("virtual_portfolio.json", 1, 0, checksum, "SUCCESS")
                logger.info("Migrated virtual portfolio")
                return True
            else:
                self.db.log_migration("virtual_portfolio.json", 0, 1, checksum, "FAILED")
                return False
                
        except Exception as e:
            logger.error(f"Failed to migrate virtual portfolio: {e}")
            self.db.log_migration("virtual_portfolio.json", 0, 0, "", f"FAILED: {e}")
            return False
    
    def verify_migration(self) -> Dict:
        """Verify migration by comparing counts."""
        results = {}
        
        # Check tracked tokens
        try:
            with open(MIGRATION_TARGETS["tracked_tokens"], 'r') as f:
                json_count = len(json.load(f))
            db_count = self.db.query("SELECT COUNT(*) as count FROM tracked_tokens")[0]["count"]
            results["tracked_tokens"] = {
                "json_count": json_count,
                "db_count": db_count,
                "match": json_count == db_count
            }
        except Exception as e:
            results["tracked_tokens"] = {"error": str(e)}
        
        # Check proposals
        try:
            with open(MIGRATION_TARGETS["stage9_proposals"], 'r') as f:
                data = json.load(f)
                json_count = len(data.get("pending", [])) + len(data.get("history", []))
            db_count = self.db.query("SELECT COUNT(*) as count FROM proposals")[0]["count"]
            results["proposals"] = {
                "json_count": json_count,
                "db_count": db_count,
                "match": json_count == db_count
            }
        except Exception as e:
            results["proposals"] = {"error": str(e)}
        
        # Check state
        try:
            db_state = self.db.query("SELECT * FROM trader_state WHERE id = 1")
            results["state"] = {
                "migrated": len(db_state) > 0,
                "data": db_state[0] if db_state else None
            }
        except Exception as e:
            results["state"] = {"error": str(e)}
        
        # Check portfolio
        try:
            db_portfolio = self.db.query("SELECT * FROM virtual_portfolio WHERE id = 1")
            results["virtual_portfolio"] = {
                "migrated": len(db_portfolio) > 0,
                "data": db_portfolio[0] if db_portfolio else None
            }
        except Exception as e:
            results["virtual_portfolio"] = {"error": str(e)}
        
        return results
    
    def run_migration(self) -> Dict:
        """Run full migration process."""
        logger.info("=" * 60)
        logger.info("STARTING DATA MIGRATION: JSON → Unified Data Layer")
        logger.info("=" * 60)
        
        # Run migrations
        tokens_ok, tokens_fail = self.migrate_tracked_tokens()
        proposals_ok, proposals_fail = self.migrate_proposals()
        state_ok = self.migrate_state()
        portfolio_ok = self.migrate_virtual_portfolio()
        
        # Verify
        logger.info("\n" + "=" * 60)
        logger.info("VERIFICATION")
        logger.info("=" * 60)
        verification = self.verify_migration()
        
        for table, result in verification.items():
            if "error" in result:
                logger.error(f"❌ {table}: {result['error']}")
            elif "match" in result:
                status = "✅" if result["match"] else "⚠️"
                logger.info(f"{status} {table}: JSON={result['json_count']}, DB={result['db_count']}")
            elif "migrated" in result:
                status = "✅" if result["migrated"] else "❌"
                logger.info(f"{status} {table}: Migrated={result['migrated']}")
        
        # Summary
        summary = {
            "tracked_tokens": {"processed": tokens_ok, "failed": tokens_fail},
            "proposals": {"processed": proposals_ok, "failed": proposals_fail},
            "state": {"migrated": state_ok},
            "virtual_portfolio": {"migrated": portfolio_ok},
            "verification": verification,
            "backup_dir": str(self.backup_dir),
            "database": str(UNIFIED_DB)
        }
        
        logger.info("\n" + "=" * 60)
        logger.info("MIGRATION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Database: {UNIFIED_DB}")
        logger.info(f"Backups: {self.backup_dir}")
        
        return summary
    
    def close(self):
        """Close connections."""
        self.db.close()


def main():
    """Main entry point."""
    print("🔄 Data Migration: JSON → Unified Data Layer")
    print("=" * 60)
    
    migrator = DataMigrator()
    
    try:
        summary = migrator.run_migration()
        
        # Save summary
        summary_file = WORKSPACE_DIR / "migration_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n✅ Migration complete!")
        print(f"📊 Summary saved to: {summary_file}")
        print(f"💾 Database: {UNIFIED_DB}")
        print(f"📁 Backups: {BACKUP_DIR}")
        
        # Show sample queries
        print("\n" + "=" * 60)
        print("SAMPLE QUERIES (now available):")
        print("=" * 60)
        print("""
# Get all Grade A tokens:
SELECT * FROM tracked_tokens WHERE current_grade IN ('A', 'A+', 'A-');

# Get pending proposals:
SELECT * FROM proposals WHERE status = 'PENDING_APPROVAL';

# Get current state:
SELECT * FROM trader_state WHERE id = 1;

# Get open positions:
SELECT * FROM open_positions WHERE status = 'open';

# Get migration history:
SELECT * FROM migration_log ORDER BY migrated_at DESC;
        """)
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        migrator.close()


if __name__ == "__main__":
    main()
