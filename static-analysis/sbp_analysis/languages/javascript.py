from typing import Set
import tree_sitter_javascript
from ..plugin import LanguagePlugin

class JavaScriptPlugin(LanguagePlugin):
    @property
    def name(self) -> str:
        return "JavaScript"

    @property
    def file_extensions(self) -> Set[str]:
        return {".js", ".jsx", ".mjs", ".cjs"}

    @property
    def tree_sitter_language(self):
        import tree_sitter
        return tree_sitter.Language(tree_sitter_javascript.language())

    @property
    def function_query(self) -> str:
        return """
        (function_declaration
          name: (identifier) @name) @function
        (generator_function_declaration
          name: (identifier) @name) @function
        (method_definition
          name: (property_identifier) @name) @function
        (variable_declarator
          name: (identifier) @name
          value: (arrow_function)) @function
        (variable_declarator
          name: (identifier) @name
          value: (function_expression)) @function
        (assignment_expression
          left: (_) @name
          right: (function_expression)) @function
        (assignment_expression
          left: (_) @name
          right: (arrow_function)) @function
        """

    @property
    def branch_nodes(self) -> Set[str]:
        return {"if_statement", "else_clause", "switch_statement", "switch_case", "switch_default", "ternary_expression"}

    @property
    def loop_nodes(self) -> Set[str]:
        return {"for_statement", "for_in_statement", "while_statement", "do_statement"}

    @property
    def nesting_nodes(self) -> Set[str]:
        return {"if_statement", "for_statement", "while_statement", "try_statement", "catch_clause", "switch_statement", "do_statement"}

    @property
    def parameter_nodes(self) -> Set[str]:
        return {"formal_parameters"}

    @property
    def local_variable_nodes(self) -> Set[str]:
        return {"variable_declaration", "lexical_declaration"}

    @property
    def import_nodes(self) -> Set[str]:
        return {"import_statement"}

    @property
    def comment_nodes(self) -> Set[str]:
        return {"comment"}

    def _analyze_node(self, node, source_code: bytes, hotspots: list):
        if node.type == "catch_clause":
            body = node.child_by_field_name("body")
            if body and len(body.named_children) == 0:
                hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "empty-catch", "message": "Empty catch block may swallow unexpected errors"})
                
        if node.type == "binary_expression":
            op = node.child_by_field_name("operator")
            if op and op.type in ("==", "!="):
                hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "loose-equality", "message": "Use strict equality (=== or !==) instead of loose equality"})
            
            if op and op.type == "<=":
                right = node.child_by_field_name("right")
                if right and right.type == "member_expression":
                    prop = right.child_by_field_name("property")
                    if prop and prop.type == "property_identifier" and source_code[prop.start_byte:prop.end_byte] == b"length":
                        hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "loop-off-by-one", "message": "Loop condition uses <= with length, possible off-by-one error"})
            
            # always true e.g. a || "literal"
            if op and op.type == "||":
                right = node.child_by_field_name("right")
                if right and right.type in ("string", "number", "true"):
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
                if op and op.type in ("==", "===", "!=", "!==", ">", "<", ">=", "<="):
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "noop-comparison", "message": "Comparison used as a statement has no effect"})
                    
        # hardcoded secrets
        if node.type == "variable_declarator":
            name = node.child_by_field_name("name")
            val = node.child_by_field_name("value")
            if name and val and name.type == "identifier" and val.type == "string":
                var_name = source_code[name.start_byte:name.end_byte].decode('utf-8').lower()
                if any(x in var_name for x in ["password", "secret", "key", "token"]):
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "high", "rule_id": "hardcoded-secret", "message": "Hardcoded secret detected"})
                    
        # eval / exec
        if node.type == "call_expression":
            func = node.child_by_field_name("function")
            if func and func.type == "identifier":
                name = source_code[func.start_byte:func.end_byte].decode('utf-8')
                if name == "eval":
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "high", "rule_id": "insecure-eval", "message": "Insecure use of eval() function"})
