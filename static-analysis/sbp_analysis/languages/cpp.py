from typing import Set
import tree_sitter_cpp
from ..plugin import LanguagePlugin

class CppPlugin(LanguagePlugin):
    @property
    def name(self) -> str:
        return "C++"

    @property
    def file_extensions(self) -> Set[str]:
        return {".cpp", ".cc", ".cxx", ".hpp", ".hxx"}

    @property
    def tree_sitter_language(self):
        import tree_sitter
        return tree_sitter.Language(tree_sitter_cpp.language())

    @property
    def function_query(self) -> str:
        return """
        (function_definition
          declarator: (function_declarator
            declarator: (identifier) @name)) @function
        (function_definition
          declarator: (function_declarator
            declarator: (field_identifier) @name)) @function
        (function_definition
          declarator: (function_declarator
            declarator: (qualified_identifier
              name: (identifier) @name))) @function
        """

    @property
    def branch_nodes(self) -> Set[str]:
        return {"if_statement", "else_clause", "switch_statement", "case_statement", "default_statement", "conditional_expression"}

    @property
    def loop_nodes(self) -> Set[str]:
        return {"for_statement", "for_range_loop", "while_statement", "do_statement"}

    @property
    def nesting_nodes(self) -> Set[str]:
        return {"compound_statement", "if_statement", "for_statement", "for_range_loop", "while_statement", "do_statement", "try_statement", "catch_clause"}

    @property
    def parameter_nodes(self) -> Set[str]:
        return {"parameter_list"}

    @property
    def local_variable_nodes(self) -> Set[str]:
        return {"declaration"}

    @property
    def import_nodes(self) -> Set[str]:
        return {"preproc_include"}

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
            # always true e.g. a || "literal"
            if op and op.type == "||":
                right = node.child_by_field_name("right")
                if right and right.type in ("string_literal", "number_literal", "true"):
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
        if node.type == "init_declarator":
            name = node.child_by_field_name("declarator")
            val = node.child_by_field_name("value")
            if name and val and val.type == "string_literal":
                var_name = source_code[name.start_byte:name.end_byte].decode('utf-8').lower()
                if any(x in var_name for x in ["password", "secret", "key", "token"]):
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "high", "rule_id": "hardcoded-secret", "message": "Hardcoded secret detected"})
                    
        # switch fall-through
        if node.type == "switch_statement":
            body = node.child_by_field_name("body")
            if body and body.type == "compound_statement":
                # simplistic approximation for C++ fall-through
                cases = [c for c in body.named_children if c.type in ("case_statement", "default_statement")]
                for case in cases[:-1]:
                    has_break = False
                    for c in case.children:
                        if c.type in ("break_statement", "return_statement"):
                            has_break = True
                    if not has_break and len(case.named_children) > 1:
                        hotspots.append({"start_line": case.start_point[0] + 1, "end_line": case.end_point[0] + 1, "severity": "warning", "rule_id": "switch-fall-through", "message": "Switch case falls through without break"})
