from typing import List, Optional, Dict

class TrieNode:
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_end: bool = False
        self.data: Optional[Dict] = None

class Trie:
    """Trie for fast customer search and autocomplete"""
    
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word: str, data: Optional[Dict] = None):
        current = self.root
        for char in word.lower():
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]
        current.is_end = True
        current.data = data
    
    def search(self, word: str) -> Optional[Dict]:
        current = self.root
        for char in word.lower():
            if char not in current.children:
                return None
            current = current.children[char]
        return current.data if current.is_end else None
    
    def starts_with(self, prefix: str) -> List[str]:
        current = self.root
        for char in prefix.lower():
            if char not in current.children:
                return []
            current = current.children[char]
        
        results = []
        self._collect_words(current, prefix, results)
        return results
    
    def _collect_words(self, node: TrieNode, prefix: str, results: List[str]):
        if node.is_end:
            results.append(prefix)
        for char, child in node.children.items():
            self._collect_words(child, prefix + char, results)
    
    def search_with_data(self, prefix: str) -> List[Dict]:
        current = self.root
        for char in prefix.lower():
            if char not in current.children:
                return []
            current = current.children[char]
        
        results = []
        self._collect_data(current, prefix, results)
        return results
    
    def _collect_data(self, node: TrieNode, prefix: str, results: List[Dict]):
        if node.is_end and node.data:
            results.append(node.data)
        for char, child in node.children.items():
            self._collect_data(child, prefix + char, results)