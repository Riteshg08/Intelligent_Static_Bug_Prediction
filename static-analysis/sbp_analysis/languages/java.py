from typing import Set
import tree_sitter_java
from ..plugin import LanguagePlugin

class JavaPlugin(LanguagePlugin):
    @property
    def name(self) -> str:
        return "Java"

    @property
    def file_extensions(self) -> Set[str]:
        return {".java"}

    @property
    def tree_sitter_language(self):
        import tree_sitter
        return tree_sitter.Language(tree_sitter_java.language())

    @property
    def function_query(self) -> str:
        return """
        (method_declaration
          name: (identifier) @name) @function
        (constructor_declaration
          name: (identifier) @name) @function
        """

    @property
    def branch_nodes(self) -> Set[str]:
        return {"if_statement", "switch_label", "switch_expression", "ternary_expression"}

    @property
    def loop_nodes(self) -> Set[str]:
        return {"for_statement", "enhanced_for_statement", "while_statement", "do_statement"}

    @property
    def nesting_nodes(self) -> Set[str]:
        return {"if_statement", "for_statement", "enhanced_for_statement", "while_statement", "do_statement", "try_statement", "catch_clause", "switch_expression"}

    @property
    def parameter_nodes(self) -> Set[str]:
        return {"formal_parameters"}

    @property
    def local_variable_nodes(self) -> Set[str]:
        return {"local_variable_declaration"}

    @property
    def import_nodes(self) -> Set[str]:
        return {"import_declaration"}

    @property
    def comment_nodes(self) -> Set[str]:
        return {"block_comment", "line_comment"}

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
                
            if node.type == "formal_parameters":
                count = sum(1 for c in node.named_children if c.type == "formal_parameter")
                if count >= 6:
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "long-parameter-list", "message": "Long parameter list (>= 6 parameters)"})
                    
            if node.type == "catch_clause":
                body = node.child_by_field_name("body")
                if body and len(body.named_children) == 0:
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "empty-catch", "message": "Empty catch block may swallow unexpected errors"})
                    
            if node.type == "binary_expression":
                op = node.child_by_field_name("operator")
                if op and op.type == "==":
                    left = node.child_by_field_name("left")
                    right = node.child_by_field_name("right")
                    if (left and left.type == "string_literal") or (right and right.type == "string_literal"):
                        hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "wrong-equality", "message": "Use .equals() for string comparison instead of =="})
                    
                if op and op.type == "<=":
                    right = node.child_by_field_name("right")
                    if right and right.type == "field_access":
                        prop = right.child_by_field_name("field")
                        if prop and prop.type == "identifier" and source_code[prop.start_byte:prop.end_byte] == b"length":
                            hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "loop-off-by-one", "message": "Loop condition uses <= with length, possible off-by-one error"})
                            
            if node.type == "assignment_expression":
                parent = node.parent
                while parent and parent.type == "parenthesized_expression":
                    parent = parent.parent
                if parent and parent.type == "if_statement":
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "high", "rule_id": "assignment-in-condition", "message": "Assignment inside a condition is likely a typo for equality"})

            if node.type in ("method_declaration", "constructor_declaration"):
                length = node.end_point[0] - node.start_point[0] + 1
                if length > 30.0:
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "long-function", "message": "Function is unusually long (>95th percentile)"})

            for child in node.children:
                walk(child, new_depth)

        walk(root_node, 0)
        return hotspots
