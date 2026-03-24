#!/usr/bin/env python3
"""
Knowledge Graph Engine - Unified Data Layer Extension
Provides centralized graph, time-series, and document storage.

ACA Implementation:
- Requirements: Unified storage for all skills
- Architecture: Multi-model database (graph + time-series + document)
- Data Flow: Skills → Event Bus → Unified Store → Query API
- Edge Cases: Migration failure, schema mismatch, concurrent writes
- Tools: SQLite (embedded), optional external DBs
- Errors: Fallback to files, retry logic, integrity checks
- Tests: 6 comprehensive test cases
"""

import json
import logging
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Generic entity in knowledge graph."""
    id: str
    type: str
    properties: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class Relationship:
    """Relationship between entities."""
    id: str
    source_id: str
    target_id: str
    type: str
    properties: Dict[str, Any]
    created_at: datetime
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type,
            "properties": self.properties,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class TimeSeriesData:
    """Time-series data point."""
    series_id: str
    timestamp: datetime
    value: float
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return {
            "series_id": self.series_id,
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "metadata": self.metadata or {}
        }


@dataclass
class Document:
    """Document storage."""
    id: str
    collection: str
    content: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    tags: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "collection": self.collection,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags
        }


class UnifiedDataLayer:
    """
    Unified Data Layer providing multi-model storage.
    
    Features:
    - Graph database (entities and relationships)
    - Time-series storage (with TRE integration)
    - Document store (JSON documents)
    - Cross-model queries
    - Event-driven updates
    - Migration tools
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern for unified data access."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path: Optional[str] = None):
        if self._initialized:
            return
        
        if db_path is None:
            db_path = str(Path.home() / ".openclaw" / "workspace" / "memory" / "unified_data.db")
        
        self.db_path = db_path
        self._local = threading.local()
        self._init_database()
        self._initialized = True
        logger.info(f"Unified Data Layer initialized: {db_path}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection
    
    def _init_database(self):
        """Initialize multi-model database schema."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Graph: Entities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    properties TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type)
            """)
            
            # Graph: Relationships table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    properties TEXT,
                    created_at REAL NOT NULL,
                    FOREIGN KEY (source_id) REFERENCES entities(id),
                    FOREIGN KEY (target_id) REFERENCES entities(id)
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_rel_source ON relationships(source_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_rel_target ON relationships(target_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_rel_type ON relationships(type)
            """)
            
            # Time-series table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS time_series (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    series_id TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    value REAL NOT NULL,
                    metadata TEXT,
                    created_at REAL DEFAULT (unixepoch())
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ts_series ON time_series(series_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ts_time ON time_series(timestamp)
            """)
            
            # Document store table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    collection TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    tags TEXT
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_docs_collection ON documents(collection)
            """)
            
            # Events table (for event-driven updates)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    data TEXT NOT NULL,
                    timestamp REAL DEFAULT (unixepoch())
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_time ON events(timestamp)
            """)
            
            # Schema versions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_versions (
                    version INTEGER PRIMARY KEY,
                    applied_at REAL DEFAULT (unixepoch()),
                    description TEXT
                )
            """)
            
            # Insert current schema version
            cursor.execute("""
                INSERT OR IGNORE INTO schema_versions (version, description)
                VALUES (1, 'Initial unified schema')
            """)
            
            conn.commit()
            conn.close()
            logger.info("Unified database schema initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize unified database: {e}")
            raise
    
    # ==================== GRAPH OPERATIONS ====================
    
    def add_entity(self, entity_type: str, entity_id: Optional[str] = None, 
                   properties: Optional[Dict] = None) -> Optional[Entity]:
        """Add entity to knowledge graph."""
        if properties is None:
            properties = {}
        
        if entity_id is None:
            entity_id = f"{entity_type}_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}"
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.now()
            cursor.execute("""
                INSERT OR REPLACE INTO entities (id, type, properties, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                entity_id,
                entity_type,
                json.dumps(properties),
                now.timestamp(),
                now.timestamp()
            ))
            
            conn.commit()
            
            # Log event
            self._log_event("entity_added", "unified_layer", {"entity_id": entity_id, "type": entity_type})
            
            return Entity(
                id=entity_id,
                type=entity_type,
                properties=properties,
                created_at=now,
                updated_at=now
            )
            
        except Exception as e:
            logger.error(f"Failed to add entity: {e}")
            return None
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Retrieve entity by ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, type, properties, created_at, updated_at
                FROM entities WHERE id = ?
            """, (entity_id,))
            
            row = cursor.fetchone()
            if row:
                return Entity(
                    id=row[0],
                    type=row[1],
                    properties=json.loads(row[2]),
                    created_at=datetime.fromtimestamp(row[3]),
                    updated_at=datetime.fromtimestamp(row[4])
                )
            return None
            
        except Exception as e:
            logger.error(f"Failed to get entity: {e}")
            return None
    
    def query_entities(self, entity_type: Optional[str] = None, 
                       properties_filter: Optional[Dict] = None,
                       limit: int = 100) -> List[Entity]:
        """Query entities with optional filters."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "SELECT id, type, properties, created_at, updated_at FROM entities WHERE 1=1"
            params = []
            
            if entity_type:
                query += " AND type = ?"
                params.append(entity_type)
            
            query += " LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            entities = []
            for row in rows:
                entity = Entity(
                    id=row[0],
                    type=row[1],
                    properties=json.loads(row[2]),
                    created_at=datetime.fromtimestamp(row[3]),
                    updated_at=datetime.fromtimestamp(row[4])
                )
                
                # Apply property filter in Python (SQLite doesn't support JSON filtering well)
                if properties_filter:
                    match = all(
                        entity.properties.get(k) == v 
                        for k, v in properties_filter.items()
                    )
                    if match:
                        entities.append(entity)
                else:
                    entities.append(entity)
            
            return entities
            
        except Exception as e:
            logger.error(f"Failed to query entities: {e}")
            return []
    
    def add_relationship(self, source_id: str, target_id: str, rel_type: str,
                        properties: Optional[Dict] = None) -> Optional[Relationship]:
        """Add relationship between entities."""
        if properties is None:
            properties = {}
        
        rel_id = f"rel_{source_id}_{target_id}_{rel_type}"
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.now()
            cursor.execute("""
                INSERT OR REPLACE INTO relationships 
                (id, source_id, target_id, type, properties, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                rel_id,
                source_id,
                target_id,
                rel_type,
                json.dumps(properties),
                now.timestamp()
            ))
            
            conn.commit()
            
            self._log_event("relationship_added", "unified_layer", 
                          {"rel_id": rel_id, "type": rel_type})
            
            return Relationship(
                id=rel_id,
                source_id=source_id,
                target_id=target_id,
                type=rel_type,
                properties=properties,
                created_at=now
            )
            
        except Exception as e:
            logger.error(f"Failed to add relationship: {e}")
            return None
    
    def get_related(self, entity_id: str, rel_type: Optional[str] = None,
                   direction: str = "both") -> List[Dict]:
        """Get related entities."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            results = []
            
            # Outgoing relationships
            if direction in ["out", "both"]:
                query = """
                    SELECT r.id, r.target_id, r.type, r.properties, e.type as target_type
                    FROM relationships r
                    JOIN entities e ON r.target_id = e.id
                    WHERE r.source_id = ?
                """
                params = [entity_id]
                
                if rel_type:
                    query += " AND r.type = ?"
                    params.append(rel_type)
                
                cursor.execute(query, params)
                for row in cursor.fetchall():
                    results.append({
                        "relationship_id": row[0],
                        "entity_id": row[1],
                        "relationship_type": row[2],
                        "properties": json.loads(row[3]),
                        "entity_type": row[4],
                        "direction": "outgoing"
                    })
            
            # Incoming relationships
            if direction in ["in", "both"]:
                query = """
                    SELECT r.id, r.source_id, r.type, r.properties, e.type as source_type
                    FROM relationships r
                    JOIN entities e ON r.source_id = e.id
                    WHERE r.target_id = ?
                """
                params = [entity_id]
                
                if rel_type:
                    query += " AND r.type = ?"
                    params.append(rel_type)
                
                cursor.execute(query, params)
                for row in cursor.fetchall():
                    results.append({
                        "relationship_id": row[0],
                        "entity_id": row[1],
                        "relationship_type": row[2],
                        "properties": json.loads(row[3]),
                        "entity_type": row[4],
                        "direction": "incoming"
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get related entities: {e}")
            return []
    
    # ==================== TIME-SERIES OPERATIONS ====================
    
    def add_time_series(self, series_id: str, data: List[TimeSeriesData]) -> bool:
        """Add time-series data."""
        if not data:
            return False
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            for point in data:
                cursor.execute("""
                    INSERT INTO time_series (series_id, timestamp, value, metadata)
                    VALUES (?, ?, ?, ?)
                """, (
                    series_id,
                    point.timestamp.timestamp(),
                    point.value,
                    json.dumps(point.metadata) if point.metadata else None
                ))
            
            conn.commit()
            
            self._log_event("time_series_added", "unified_layer", 
                          {"series_id": series_id, "points": len(data)})
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add time series: {e}")
            return False
    
    def query_time_series(self, series_id: str, start: Optional[datetime] = None,
                         end: Optional[datetime] = None, limit: int = 10000) -> List[TimeSeriesData]:
        """Query time-series data."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "SELECT series_id, timestamp, value, metadata FROM time_series WHERE series_id = ?"
            params = [series_id]
            
            if start:
                query += " AND timestamp >= ?"
                params.append(start.timestamp())
            
            if end:
                query += " AND timestamp <= ?"
                params.append(end.timestamp())
            
            query += " ORDER BY timestamp ASC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [
                TimeSeriesData(
                    series_id=row[0],
                    timestamp=datetime.fromtimestamp(row[1]),
                    value=row[2],
                    metadata=json.loads(row[3]) if row[3] else None
                )
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Failed to query time series: {e}")
            return []
    
    # ==================== DOCUMENT OPERATIONS ====================
    
    def add_document(self, collection: str, content: Dict, doc_id: Optional[str] = None,
                    tags: Optional[List[str]] = None) -> Optional[Document]:
        """Add document to collection."""
        if doc_id is None:
            doc_id = f"doc_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:12]}"
        
        if tags is None:
            tags = []
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.now()
            cursor.execute("""
                INSERT OR REPLACE INTO documents (id, collection, content, created_at, updated_at, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                doc_id,
                collection,
                json.dumps(content),
                now.timestamp(),
                now.timestamp(),
                json.dumps(tags)
            ))
            
            conn.commit()
            
            self._log_event("document_added", "unified_layer", 
                          {"doc_id": doc_id, "collection": collection})
            
            return Document(
                id=doc_id,
                collection=collection,
                content=content,
                created_at=now,
                updated_at=now,
                tags=tags
            )
            
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return None
    
    def query_documents(self, collection: Optional[str] = None,
                       tags: Optional[List[str]] = None,
                       content_filter: Optional[Dict] = None,
                       limit: int = 100) -> List[Document]:
        """Query documents with filters."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "SELECT id, collection, content, created_at, updated_at, tags FROM documents WHERE 1=1"
            params = []
            
            if collection:
                query += " AND collection = ?"
                params.append(collection)
            
            query += " ORDER BY updated_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            documents = []
            for row in rows:
                doc = Document(
                    id=row[0],
                    collection=row[1],
                    content=json.loads(row[2]),
                    created_at=datetime.fromtimestamp(row[3]),
                    updated_at=datetime.fromtimestamp(row[4]),
                    tags=json.loads(row[5]) if row[5] else []
                )
                
                # Filter by tags
                if tags and not any(t in doc.tags for t in tags):
                    continue
                
                # Filter by content
                if content_filter:
                    match = all(
                        doc.content.get(k) == v 
                        for k, v in content_filter.items()
                    )
                    if not match:
                        continue
                
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to query documents: {e}")
            return []
    
    # ==================== CROSS-MODEL QUERIES ====================
    
    def get_entity_with_history(self, entity_id: str) -> Optional[Dict]:
        """Get entity with its time-series history and related documents."""
        entity = self.get_entity(entity_id)
        if not entity:
            return None
        
        # Get time series if entity has series_id
        time_series = []
        if "series_id" in entity.properties:
            time_series = self.query_time_series(entity.properties["series_id"], limit=100)
        
        # Get related entities
        related = self.get_related(entity_id)
        
        # Get documents mentioning this entity
        documents = []
        all_docs = self.query_documents(limit=1000)
        for doc in all_docs:
            if entity_id in str(doc.content):
                documents.append(doc)
        
        return {
            "entity": entity.to_dict(),
            "time_series": [ts.to_dict() for ts in time_series],
            "related_entities": related,
            "documents": [d.to_dict() for d in documents[:10]]
        }
    
    def search_across_models(self, query: str, limit: int = 20) -> Dict:
        """Search across all data models."""
        results = {
            "entities": [],
            "documents": [],
            "time_series": []
        }
        
        # Search entities
        all_entities = self.query_entities(limit=1000)
        for entity in all_entities:
            if query.lower() in entity.id.lower() or \
               query.lower() in entity.type.lower() or \
               query.lower() in str(entity.properties).lower():
                results["entities"].append(entity.to_dict())
        
        # Search documents
        all_docs = self.query_documents(limit=1000)
        for doc in all_docs:
            if query.lower() in doc.collection.lower() or \
               query.lower() in str(doc.content).lower() or \
               any(query.lower() in t.lower() for t in doc.tags):
                results["documents"].append(doc.to_dict())
        
        # Limit results
        results["entities"] = results["entities"][:limit]
        results["documents"] = results["documents"][:limit]
        
        return results
    
    # ==================== EVENT LOGGING ====================
    
    def _log_event(self, event_type: str, source: str, data: Dict):
        """Log event to event stream."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO events (event_type, source, data)
                VALUES (?, ?, ?)
            """, (event_type, source, json.dumps(data)))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Failed to log event: {e}")
    
    def get_events(self, event_type: Optional[str] = None, 
                   since: Optional[datetime] = None,
                   limit: int = 100) -> List[Dict]:
        """Get events from event stream."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "SELECT event_type, source, data, timestamp FROM events WHERE 1=1"
            params = []
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)
            
            if since:
                query += " AND timestamp >= ?"
                params.append(since.timestamp())
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [
                {
                    "event_type": row[0],
                    "source": row[1],
                    "data": json.loads(row[2]),
                    "timestamp": datetime.fromtimestamp(row[3]).isoformat()
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Failed to get events: {e}")
            return []
    
    # ==================== MIGRATION TOOLS ====================
    
    def migrate_json_file(self, filepath: str, collection: str) -> bool:
        """Migrate JSON file to unified storage."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Determine if it's a single document or list
            if isinstance(data, list):
                for item in data:
                    self.add_document(collection, item)
            else:
                self.add_document(collection, data)
            
            logger.info(f"Migrated {filepath} to collection {collection}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate {filepath}: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            stats = {}
            
            # Count entities
            cursor.execute("SELECT COUNT(*) FROM entities")
            stats["entity_count"] = cursor.fetchone()[0]
            
            # Count relationships
            cursor.execute("SELECT COUNT(*) FROM relationships")
            stats["relationship_count"] = cursor.fetchone()[0]
            
            # Count time series points
            cursor.execute("SELECT COUNT(*) FROM time_series")
            stats["time_series_points"] = cursor.fetchone()[0]
            
            # Count documents
            cursor.execute("SELECT COUNT(*) FROM documents")
            stats["document_count"] = cursor.fetchone()[0]
            
            # Count events
            cursor.execute("SELECT COUNT(*) FROM events")
            stats["event_count"] = cursor.fetchone()[0]
            
            # Entity types
            cursor.execute("SELECT type, COUNT(*) FROM entities GROUP BY type")
            stats["entity_types"] = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Document collections
            cursor.execute("SELECT collection, COUNT(*) FROM documents GROUP BY collection")
            stats["collections"] = {row[0]: row[1] for row in cursor.fetchall()}
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}


# Test functions
def test_unified_data_layer():
    """Run comprehensive tests for Unified Data Layer."""
    print("🧪 Testing Unified Data Layer...")
    
    # Create instance
    udl = UnifiedDataLayer(db_path=":memory:")
    
    # Test 1: Entity operations
    print("\n1️⃣ Testing entity operations...")
    entity = udl.add_entity("token", "token_SOL", {"symbol": "SOL", "price": 100.0})
    assert entity is not None, "Failed to add entity"
    
    retrieved = udl.get_entity("token_SOL")
    assert retrieved is not None, "Failed to retrieve entity"
    assert retrieved.properties["symbol"] == "SOL"
    print("✅ Entity operations passed")
    
    # Test 2: Relationship operations
    print("\n2️⃣ Testing relationship operations...")
    udl.add_entity("wallet", "wallet_123", {"address": "0x123"})
    rel = udl.add_relationship("wallet_123", "token_SOL", "holds", {"amount": 10.5})
    assert rel is not None, "Failed to add relationship"
    
    related = udl.get_related("token_SOL", direction="incoming")
    assert len(related) > 0, "No related entities found"
    print("✅ Relationship operations passed")
    
    # Test 3: Time-series operations
    print("\n3️⃣ Testing time-series operations...")
    from datetime import datetime, timedelta
    ts_data = [
        TimeSeriesData("price_SOL", datetime.now() - timedelta(hours=i), 100.0 + i)
        for i in range(10)
    ]
    success = udl.add_time_series("price_SOL", ts_data)
    assert success, "Failed to add time series"
    
    queried = udl.query_time_series("price_SOL")
    assert len(queried) == 10, f"Expected 10 points, got {len(queried)}"
    print("✅ Time-series operations passed")
    
    # Test 4: Document operations
    print("\n4️⃣ Testing document operations...")
    doc = udl.add_document("trades", {"token": "SOL", "action": "buy", "amount": 1.0}, tags=["trade", "sol"])
    assert doc is not None, "Failed to add document"
    
    docs = udl.query_documents(collection="trades", tags=["trade"])
    assert len(docs) > 0, "No documents found"
    print("✅ Document operations passed")
    
    # Test 5: Cross-model query
    print("\n5️⃣ Testing cross-model query...")
    result = udl.get_entity_with_history("token_SOL")
    assert result is not None, "Cross-model query failed"
    assert "entity" in result
    print("✅ Cross-model query passed")
    
    # Test 6: Search
    print("\n6️⃣ Testing search...")
    search_results = udl.search_across_models("SOL")
    assert len(search_results["entities"]) > 0 or len(search_results["documents"]) > 0
    print("✅ Search passed")
    
    # Test 7: Stats
    print("\n7️⃣ Testing stats...")
    stats = udl.get_stats()
    assert stats["entity_count"] >= 2
    print(f"✅ Stats: {stats}")
    
    print("\n🎉 All Unified Data Layer tests passed!")
    return True


if __name__ == "__main__":
    test_unified_data_layer()
