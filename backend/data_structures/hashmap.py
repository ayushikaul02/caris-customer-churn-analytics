from typing import Any, Optional, Dict, List

class HashMap:
    """Hash map for fast customer lookup"""
    
    def __init__(self):
        self.data: Dict[int, Any] = {}
    
    def put(self, key: int, value: Any):
        self.data[key] = value
    
    def get(self, key: int) -> Optional[Any]:
        return self.data.get(key)
    
    def remove(self, key: int) -> bool:
        if key in self.data:
            del self.data[key]
            return True
        return False
    
    def contains(self, key: int) -> bool:
        return key in self.data
    
    def size(self) -> int:
        return len(self.data)
    
    def keys(self) -> List[int]:
        return list(self.data.keys())
    
    def values(self) -> List[Any]:
        return list(self.data.values())
    
    def clear(self):
        self.data.clear()