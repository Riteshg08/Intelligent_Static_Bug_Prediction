from typing import Set
import tree_sitter_go
from ..plugin import LanguagePlugin

class GoPlugin(LanguagePlugin):
    @property
    def name(self) -> str:
        return "Go"

    @property
    def file_extensions(self) -> Set[str]:
        return {".go"}

    @property
    def tree_sitter_language(self):
        import tree_sitter
        return tree_sitter.Language(tree_sitter_go.language())

    @property
    def function_query(self) -> str:
        return """
        (function_declaration
          name: (identifier) @name) @function
        (method_declaration
          name: (field_identifier) @name) @function
        (func_literal) @function
        """

    @property
    def branch_nodes(self) -> Set[str]:
        return {"if_statement", "expression_switch_statement", "type_switch_statement", "select_statement"}

    @property
    def loop_nodes(self) -> Set[str]:
        return {"for_statement"}

    @property
    def nesting_nodes(self) -> Set[str]:
        return {"if_statement", "for_statement", "expression_case", "type_case", "communication_case"}

    @property
    def parameter_nodes(self) -> Set[str]:
        return {"parameter_list"}

    @property
    def local_variable_nodes(self) -> Set[str]:
        return {"short_var_declaration", "var_declaration"}

    @property
    def import_nodes(self) -> Set[str]:
        return {"import_spec"}

    @property
    def comment_nodes(self) -> Set[str]:
        return {"comment"}

    def _analyze_node(self, node, source_code: bytes, hotspots: list):
        if node.type == "binary_expression":
            op = node.child_by_field_name("operator")
            # always true e.g. a || "literal"
            if op and op.type == "||":
                right = node.child_by_field_name("right")
                if right and right.type in ("interpreted_string_literal", "raw_string_literal", "int_literal", "true"):
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "always-true", "message": "Condition with literal OR is always true"})

        if node.type == "assignment_statement":
            parent = node.parent
            while parent and parent.type == "parenthesized_expression":
                parent = parent.parent
            if parent and parent.type == "if_statement":
                hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "high", "rule_id": "assignment-in-condition", "message": "Assignment inside a condition is likely a typo for equality"})

        # noop comparison e.g. cost == 0;
        if node.type == "expression_statement":
            if node.named_children and node.named_children[0].type == "binary_expression":
                op = node.named_children[0].child_by_field_name("operator")
                if op and op.type in ("==", "!=", ">", "<", ">=", "<="):
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "noop-comparison", "message": "Comparison used as a statement has no effect"})
                    
        # hardcoded secrets
        if node.type in ("short_var_declaration", "var_spec"):
            left = node.named_children[0]
            right = node.named_children[-1]
            if left and right and left.type in ("identifier_list", "identifier") and right.type in ("expression_list", "interpreted_string_literal", "raw_string_literal"):
                var_name = source_code[left.start_byte:left.end_byte].decode('utf-8').lower()
                if any(x in var_name for x in ["password", "secret", "key", "token"]):
                    if right.type in ("interpreted_string_literal", "raw_string_literal") or (right.type == "expression_list" and any("string" in c.type for c in right.named_children)):
                        hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "high", "rule_id": "hardcoded-secret", "message": "Hardcoded secret detected"})
