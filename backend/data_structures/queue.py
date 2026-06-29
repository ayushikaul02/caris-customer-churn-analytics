from collections import deque
from typing import Any

class Queue:
    """FIFO queue for processing data batches"""
    
    def __init__(self):
        self.queue = deque()
    
    def enqueue(self, item: Any):
        self.queue.append(item)
    
    def dequeue(self) -> Any:
        if not self.is_empty():
            return self.queue.popleft()
        return None
    
    def peek(self) -> Any:
        return self.queue[0] if not self.is_empty() else None
    
    def is_empty(self) -> bool:
        return len(self.queue) == 0
    
    def size(self) -> int:
        return len(self.queue)
    
    def clear(self):
        self.queue.clear()