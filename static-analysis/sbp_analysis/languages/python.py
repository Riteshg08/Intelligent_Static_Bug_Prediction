from typing import Set
import tree_sitter_python
from ..plugin import LanguagePlugin

class PythonPlugin(LanguagePlugin):
    @property
    def name(self) -> str:
        return "Python"

    @property
    def file_extensions(self) -> Set[str]:
        return {".py", ".pyw"}

    @property
    def tree_sitter_language(self):
        import tree_sitter
        return tree_sitter.Language(tree_sitter_python.language())

    @property
    def function_query(self) -> str:
        return """
        (function_definition
          name: (identifier) @name) @function
        """

    @property
    def branch_nodes(self) -> Set[str]:
        return {"if_statement", "elif_clause", "else_clause", "match_statement", "conditional_expression"}

    @property
    def loop_nodes(self) -> Set[str]:
        return {"for_statement", "while_statement"}

    @property
    def nesting_nodes(self) -> Set[str]:
        return self.branch_nodes | self.loop_nodes | {"try_statement", "with_statement"}

    @property
    def parameter_nodes(self) -> Set[str]:
        return {"parameters"}

    @property
    def local_variable_nodes(self) -> Set[str]:
        return {"assignment"}

    @property
    def import_nodes(self) -> Set[str]:
        return {"import_statement", "import_from_statement"}

    @property
    def comment_nodes(self) -> Set[str]:
        return {"comment"}

    def analyze_hotspots(self, root_node, source_code: bytes) -> list:
        hotspots = []
        nesting_nodes = self.nesting_nodes

        def walk(node, depth):
            if node.type in nesting_nodes:
                new_depth = depth + 1
                if new_depth == 4:
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "deep-nesting", "message": "Deeply nested code (depth >= 4)"})
                elif new_depth == 6:
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "high", "rule_id": "very-deep-nesting", "message": "Very deeply nested code (depth >= 6)"})
            else:
                new_depth = depth
                
            if node.type == "parameters":
                count = sum(1 for c in node.named_children)
                if count >= 6:
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "long-parameter-list", "message": "Long parameter list (>= 6 parameters)"})
            
            if node.type == "except_clause":
                has_type = any(c.is_named and c.type != 'block' for c in node.children)
                if not has_type:
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "bare-except", "message": "Bare except clause may swallow unexpected errors"})
                for c in node.named_children:
                    if c.type == "block" and len(c.named_children) == 1 and c.named_children[0].type == "pass_statement":
                        hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "empty-except", "message": "Empty error handler"})
                        
            if node.type == "comparison_operator":
                for c in node.children:
                    if c.type == "none":
                        ops = [x.type for x in node.children if not x.is_named]
                        if "==" in ops or "!=" in ops:
                            hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "wrong-equality", "message": "Use 'is' or 'is not' for None comparison"})

            if node.type == "default_parameter":
                val = node.named_children[-1]
                if val.type in ("list", "dictionary", "set"):
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "high", "rule_id": "mutable-default", "message": "Mutable default argument is shared across calls"})
                    
            if node.type == "function_definition":
                length = node.end_point[0] - node.start_point[0] + 1
                if length > 21.45:
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "long-function", "message": "Function is unusually long (>95th percentile)"})

            for child in node.children:
                walk(child, new_depth)

        walk(root_node, 0)
        return hotspots
