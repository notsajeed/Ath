import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any
from .scanner import CodeChunk

class LocalStorage:
    def __init__(self, aibuddy_dir: Path):
        self.aibuddy_dir = aibuddy_dir
        self.db_path = aibuddy_dir / "data.db"
        self.config_path = aibuddy_dir / "config.json"
        self.history_path = aibuddy_dir / "chat_history.json"
    
    def init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS code_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                chunk_type TEXT NOT NULL,
                name TEXT NOT NULL,
                content TEXT NOT NULL,
                line_start INTEGER,
                line_end INTEGER,
                docstring TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Create config file
        config = {
            "version": "0.1.0",
            "initialized_at": str(Path.cwd()),
            "settings": {
                "max_context_chunks": 10
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def store_code_chunks(self, chunks: List[CodeChunk]):
        """Store code chunks in database"""
        conn = sqlite3.connect(self.db_path)
        
        # Clear existing chunks
        conn.execute("DELETE FROM code_chunks")
        
        # Insert new chunks
        for chunk in chunks:
            conn.execute('''
                INSERT INTO code_chunks 
                (file_path, chunk_type, name, content, line_start, line_end, docstring)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                chunk.file_path, chunk.chunk_type, chunk.name, 
                chunk.content, chunk.line_start, chunk.line_end, chunk.docstring
            ))
        
        conn.commit()
        conn.close()
    
    def get_all_chunks(self) -> List[Dict[str, Any]]:
        """Get all stored code chunks"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dicts
        
        cursor = conn.execute("SELECT * FROM code_chunks ORDER BY file_path, line_start")
        chunks = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return chunks
    
    def get_chunks_by_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Get code chunks for a specific file"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute(
            "SELECT * FROM code_chunks WHERE file_path = ? ORDER BY line_start", 
            (file_path,)
        )
        chunks = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return chunks
    
    def save_chat(self, question: str, response: str):
        """Save chat interaction"""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO chat_history (question, response) VALUES (?, ?)",
            (question, response)
        )
        conn.commit()
        conn.close()