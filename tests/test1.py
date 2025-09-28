#!/usr/bin/env python3
"""
A random test Python file with various code patterns for testing purposes.
Includes classes, functions, decorators, and different programming constructs.
"""

import json
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from functools import wraps

# Global constant
MAX_RETRIES = 3

@dataclass
class User:
    """Simple user data class"""
    id: int
    name: str
    email: str
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

def retry(max_attempts: int = 3):
    """Decorator to retry function calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    print(f"Attempt {attempt + 1} failed: {e}")
            return None
        return wrapper
    return decorator

class DatabaseManager:
    """Mock database manager with various operations"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.users: Dict[int, User] = {}
        self._next_id = 1
    
    @retry(max_attempts=MAX_RETRIES)
    def create_user(self, name: str, email: str) -> User:
        """Create a new user with retry logic"""
        user = User(id=self._next_id, name=name, email=email)
        self.users[self._next_id] = user
        self._next_id += 1
        return user
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Retrieve user by ID"""
        return self.users.get(user_id)
    
    def list_users(self, limit: int = 10) -> List[User]:
        """Get list of users with pagination"""
        return list(self.users.values())[:limit]
    
    async def async_operation(self, data: Dict) -> bool:
        """Simulate async database operation"""
        await asyncio.sleep(0.1)  # Simulate I/O delay
        return len(data) > 0

def process_data(raw_data: str) -> Dict:
    """Process raw JSON data with error handling"""
    try:
        data = json.loads(raw_data)
        
        # Data validation
        if not isinstance(data, dict):
            raise ValueError("Expected dictionary data")
        
        # Transform data
        processed = {}
        for key, value in data.items():
            if isinstance(value, str):
                processed[key.lower()] = value.strip()
            elif isinstance(value, (int, float)):
                processed[key.lower()] = value
            else:
                processed[key.lower()] = str(value)
        
        return processed
        
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return {}
    except Exception as e:
        print(f"Processing error: {e}")
        return {}

# Generator function
def fibonacci_generator(n: int):
    """Generate Fibonacci sequence up to n numbers"""
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# Context manager
class FileProcessor:
    """Context manager for file processing"""
    
    def __init__(self, filename: str, mode: str = 'r'):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()

# Lambda functions and higher-order functions
filter_even = lambda x: x % 2 == 0
square = lambda x: x ** 2

def apply_operations(numbers: List[int], operations: List) -> List[int]:
    """Apply a series of operations to numbers"""
    result = numbers[:]
    for operation in operations:
        result = list(map(operation, result))
    return result

# Main execution
if __name__ == "__main__":
    # Test the various components
    db = DatabaseManager("sqlite:///test.db")
    
    # Create some users
    user1 = db.create_user("Alice Smith", "alice@example.com")
    user2 = db.create_user("Bob Johnson", "bob@example.com")
    
    print(f"Created users: {len(db.users)}")
    
    # Test data processing
    sample_json = '{"name": "Test", "age": 25, "active": true}'
    processed = process_data(sample_json)
    print(f"Processed data: {processed}")
    
    # Test generator
    fib_numbers = list(fibonacci_generator(10))
    print(f"Fibonacci: {fib_numbers}")
    
    # Test higher-order functions
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    even_squares = apply_operations(
        list(filter(filter_even, numbers)),
        [square]
    )
    print(f"Even squares: {even_squares}")
    
    # Async example (would need to be run in async context)
    # result = asyncio.run(db.async_operation({"test": "data"}))
    # print(f"Async result: {result}")