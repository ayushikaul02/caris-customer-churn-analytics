from typing import List, Set
from collections import defaultdict

class Graph:
    """Graph for customer referral networks"""
    
    def __init__(self):
        self.adjacency = defaultdict(set)
        self.nodes = set()
    
    def add_node(self, node: int):
        self.nodes.add(node)
    
    def add_edge(self, from_node: int, to_node: int):
        self.add_node(from_node)
        self.add_node(to_node)
        self.adjacency[from_node].add(to_node)
    
    def get_neighbors(self, node: int) -> Set[int]:
        return self.adjacency.get(node, set())
    
    def get_referral_chain(self, start_node: int, depth: int = 3) -> List[int]:
        visited = set()
        chain = []
        
        def dfs(node: int, current_depth: int):
            if current_depth > depth or node in visited:
                return
            visited.add(node)
            chain.append(node)
            for neighbor in self.get_neighbors(node):
                dfs(neighbor, current_depth + 1)
        
        dfs(start_node, 0)
        return chain
    
    def get_influence_score(self, node: int) -> int:
        return len(self.get_neighbors(node))
    
    def get_communities(self) -> List[List[int]]:
        if not self.nodes:
            return []
        
        visited = set()
        communities = []
        
        for node in self.nodes:
            if node not in visited:
                community = []
                queue = [node]
                visited.add(node)
                
                while queue:
                    current = queue.pop()
                    community.append(current)
                    for neighbor in self.get_neighbors(current):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                
                communities.append(community)
        
        return communities