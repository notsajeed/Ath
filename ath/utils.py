from pathlib import Path

def is_project_initialized(path: Path = None) -> bool:
    """Check if current directory has an Ath agent"""
    if path is None:
        path = Path.cwd()
    return (path / ".aibuddy").exists()

def get_project_stats(aibuddy_dir: Path) -> dict:
    """Get basic stats about the project"""
    from .storage import LocalStorage
    
    storage = LocalStorage(aibuddy_dir)
    chunks = storage.get_all_chunks()
    
    stats = {
        "total_chunks": len(chunks),
        "files": len(set(chunk["file_path"] for chunk in chunks)),
        "functions": len([c for c in chunks if c["chunk_type"] == "function"]),
        "classes": len([c for c in chunks if c["chunk_type"] == "class"])
    }
    
    return stats