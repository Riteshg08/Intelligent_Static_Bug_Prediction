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

    def _analyze_node(self, node, source_code: bytes, hotspots: list):
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
                        
            # always true e.g. a || true
            if op and op.type == "||":
                right = node.child_by_field_name("right")
                if right and right.type in ("string_literal", "true"):
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "always-true", "message": "Condition with literal OR is always true"})
                        
        if node.type == "assignment_expression":
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
        if node.type == "variable_declarator":
            name = node.child_by_field_name("name")
            val = node.child_by_field_name("value")
            if name and val and name.type == "identifier" and val.type == "string_literal":
                var_name = source_code[name.start_byte:name.end_byte].decode('utf-8').lower()
                if any(x in var_name for x in ["password", "secret", "key", "token"]):
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "high", "rule_id": "hardcoded-secret", "message": "Hardcoded secret detected"})
                    
        # switch fall-through
        if node.type == "switch_block":
            cases = node.named_children
            for i, case in enumerate(cases[:-1]):
                has_break = False
                for c in case.children:
                    if c.type in ("break_statement", "return_statement", "throw_statement", "yield_statement"):
                        has_break = True
                        break
                # Only a finding if it actually has statements
                if not has_break and sum(1 for c in case.children if c.is_named and c.type != "switch_label") > 0:
                    hotspots.append({"start_line": case.start_point[0] + 1, "end_line": case.end_point[0] + 1, "severity": "warning", "rule_id": "switch-fall-through", "message": "Switch case falls through without break"})
