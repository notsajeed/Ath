from pathlib import Path

from pathlib import Path

def find_project_root(start_dir=None):
    """
    Find the project root directory by looking for project indicators.
    Searches upward from start_dir (defaults to current directory).
    
    Returns the directory containing project files, or current directory if not found.
    """
    if start_dir is None:
        start_dir = Path.cwd()
    else:
        start_dir = Path(start_dir)
    
    current = start_dir.resolve()
    
    # Project indicators to look for (in order of preference)
    project_indicators = [
        '.aibuddy',      # Existing ath project
        'setup.py',      # Python setuptools project
        'pyproject.toml', # Modern Python project
        '.git',          # Git repository
        'requirements.txt', # Python dependencies
        'Pipfile',       # Pipenv project
        'poetry.lock',   # Poetry project
    ]
    
    # Walk up the directory tree
    while current != current.parent:  # Stop at filesystem root
        
        # Check for any project indicators in current directory
        for indicator in project_indicators:
            if (current / indicator).exists():
                return current
        
        # Move to parent directory
        current = current.parent
    
    # If we reach here, no project root found - use the starting directory
    return start_dir

def find_aibuddy_dir(start_dir=None):
    """
    Find existing .aibuddy directory by searching upward.
    Returns None if not found.
    """
    if start_dir is None:
        start_dir = Path.cwd()
    else:
        start_dir = Path(start_dir)
    
    current = start_dir.resolve()
    
    # Walk up looking for .aibuddy
    while current != current.parent:
        aibuddy_path = current / '.aibuddy'
        if aibuddy_path.exists():
            return aibuddy_path
        current = current.parent
    
    return None

# Usage examples:
if __name__ == "__main__":
    # Test the functions
    project_root = find_project_root()
    print(f"Project root: {project_root}")
    
    existing_aibuddy = find_aibuddy_dir()
    if existing_aibuddy:
        print(f"Found existing .aibuddy at: {existing_aibuddy}")
    else:
        print("No existing .aibuddy found")


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

