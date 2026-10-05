from abc import ABC, abstractmethod
from typing import Set

class LanguagePlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def file_extensions(self) -> Set[str]:
        pass

    @property
    @abstractmethod
    def tree_sitter_language(self):
        pass

    @property
    @abstractmethod
    def function_query(self) -> str:
        """Tree-sitter query that finds functions/methods/constructors/lambdas"""
        pass

    @property
    @abstractmethod
    def branch_nodes(self) -> Set[str]:
        pass

    @property
    @abstractmethod
    def loop_nodes(self) -> Set[str]:
        pass

    @property
    @abstractmethod
    def nesting_nodes(self) -> Set[str]:
        pass

    @property
    @abstractmethod
    def parameter_nodes(self) -> Set[str]:
        pass

    @property
    @abstractmethod
    def local_variable_nodes(self) -> Set[str]:
        pass

    @property
    @abstractmethod
    def import_nodes(self) -> Set[str]:
        pass

    @property
    @abstractmethod
    def comment_nodes(self) -> Set[str]:
        pass

    def analyze_hotspots(self, root_node, source_code: bytes) -> list:
        hotspots = []
        nesting_nodes = self.nesting_nodes
        branch_nodes = self.branch_nodes
        param_nodes = self.parameter_nodes
        
        def walk(node, depth, current_func=None):
            new_depth = depth
            if node.type in nesting_nodes:
                new_depth = depth + 1
                if new_depth == 4:
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "deep-nesting", "message": "Deeply nested code (depth >= 4)"})
                elif new_depth == 6:
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "high", "rule_id": "very-deep-nesting", "message": "Very deeply nested code (depth >= 6)"})
                    
            if node.type in param_nodes:
                count = sum(1 for c in node.named_children)
                if count >= 6:
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "long-parameter-list", "message": "Long parameter list (>= 6 parameters)"})
            
            is_func = "function" in node.type or "method" in node.type or "constructor" in node.type
            if is_func:
                current_func = node
                length = node.end_point[0] - node.start_point[0] + 1
                if length > 30:  # heuristic
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "long-function", "message": "Function is unusually long (>95th percentile)"})
                
                branches = 0
                def count_branches(n):
                    nonlocal branches
                    if n.type in branch_nodes:
                        branches += 1
                    for c in n.children:
                        if "function" not in c.type and "method" not in c.type:
                            count_branches(c)
                count_branches(node)
                if branches >= 10:
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "many-branches", "message": f"Function has too many branches ({branches})"})
                    
            # Let subclass add custom logic for node
            self._analyze_node(node, source_code, hotspots)
            
            for child in node.children:
                walk(child, new_depth, current_func)
                
        walk(root_node, 0)
        return hotspots
        
    def _analyze_node(self, node, source_code: bytes, hotspots: list):
        pass
