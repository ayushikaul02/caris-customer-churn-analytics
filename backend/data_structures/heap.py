import heapq
from typing import List, Tuple, Any

class PriorityQueue:
    """Min-heap implementation for ranking customers by risk score"""
    
    def __init__(self):
        self.heap = []
    
    def push(self, item: Any, priority: float):
        heapq.heappush(self.heap, (priority, item))
    
    def pop(self) -> Tuple[float, Any]:
        return heapq.heappop(self.heap)
    
    def peek(self) -> Tuple[float, Any]:
        return self.heap[0] if self.heap else None
    
    def top_n(self, n: int) -> List[Any]:
        return [item for _, item in heapq.nsmallest(n, self.heap)]
    
    def size(self) -> int:
        return len(self.heap)
    
    def is_empty(self) -> bool:
        return len(self.heap) == 0
    
    def clear(self):
        self.heap.clear()