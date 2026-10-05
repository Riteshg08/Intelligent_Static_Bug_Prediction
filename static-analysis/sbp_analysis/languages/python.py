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

    def _analyze_node(self, node, source_code: bytes, hotspots: list):
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
                
        # Check loop-off-by-one: range(len(x) + 1)
        if node.type == "call":
            func_node = node.named_children[0] if node.named_children else None
            if func_node and func_node.type == "identifier" and source_code[func_node.start_byte:func_node.end_byte] == b"range":
                args = node.named_children[1] if len(node.named_children) > 1 else None
                if args and args.type == "argument_list":
                    for arg in args.named_children:
                        if arg.type == "binary_operator":
                            op = arg.child_by_field_name("operator")
                            if op and op.type == "+":
                                left = arg.child_by_field_name("left")
                                right = arg.child_by_field_name("right")
                                if left and left.type == "call" and left.named_children and left.named_children[0].type == "identifier" and source_code[left.named_children[0].start_byte:left.named_children[0].end_byte] == b"len":
                                    if right and right.type == "integer" and source_code[right.start_byte:right.end_byte] == b"1":
                                        hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "loop-off-by-one", "message": "Possible off-by-one error with range(len(...) + 1)"})

        # Check noop comparison
        if node.type == "expression_statement":
            if node.named_children and node.named_children[0].type == "comparison_operator":
                hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "noop-comparison", "message": "Comparison used as a statement has no effect"})

        # Check always true
        if node.type == "boolean_operator":
            op = [c.type for c in node.children if not c.is_named]
            if "or" in op:
                right = node.child_by_field_name("right")
                if right and right.type in ("string", "integer", "true"):
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "warning", "rule_id": "always-true", "message": "Condition with literal OR is always true"})

        # Check unclosed resource
        if node.type == "assignment":
            right = node.named_children[-1] if node.named_children else None
            if right and right.type == "call":
                func_node = right.named_children[0] if right.named_children else None
                if func_node and func_node.type == "identifier" and source_code[func_node.start_byte:func_node.end_byte] == b"open":
                    # Check if inside a with statement
                    is_with = False
                    p = node.parent
                    while p:
                        if p.type == "with_statement":
                            is_with = True
                            break
                        p = p.parent
                    if not is_with:
                        # Verify if close is called on the variable in the same scope
                        left = node.named_children[0]
                        if left and left.type == "identifier":
                            var_name = source_code[left.start_byte:left.end_byte]
                            has_close = False
                            p = node.parent
                            while p and p.type not in ("module", "function_definition", "class_definition"):
                                p = p.parent
                            if p:
                                def check_close(n):
                                    nonlocal has_close
                                    if has_close: return
                                    if n.type == "call":
                                        fn = n.named_children[0] if n.named_children else None
                                        if fn and fn.type == "attribute":
                                            obj = fn.child_by_field_name("object")
                                            attr = fn.child_by_field_name("attribute")
                                            if obj and attr and obj.type == "identifier" and source_code[obj.start_byte:obj.end_byte] == var_name:
                                                if source_code[attr.start_byte:attr.end_byte] == b"close":
                                                    has_close = True
                                    for c in n.children:
                                        check_close(c)
                                check_close(p)
                                if not has_close:
                                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "high", "rule_id": "unclosed-resource", "message": "Resource opened but not closed (consider using 'with' statement)"})

        # Check for eval() and others
        if node.type == "call":
            func_node = node.named_children[0] if node.named_children else None
            if func_node and func_node.type == "identifier":
                func_name = source_code[func_node.start_byte:func_node.end_byte].decode('utf-8')
                if func_name == "eval":
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "high", "rule_id": "insecure-eval", "message": "Insecure use of eval() function"})
                elif func_name in ("exec", "system", "popen"):
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "high", "rule_id": "command-injection", "message": "Possible command execution vulnerability"})

        # Check for SQL injection patterns
        if node.type == "call":
            func_node = node.named_children[0] if node.named_children else None
            if func_node and func_node.type == "attribute":
                attr_name_node = func_node.named_children[-1] if func_node.named_children else None
                if attr_name_node and attr_name_node.type == "identifier":
                    attr_name = source_code[attr_name_node.start_byte:attr_name_node.end_byte].decode('utf-8')
                    if attr_name == "execute":
                        args_node = node.named_children[1] if len(node.named_children) > 1 else None
                        if args_node and args_node.type == "argument_list":
                            if len(args_node.named_children) > 0:
                                first_arg = args_node.named_children[0]
                                if first_arg.type in ("string", "binary_operator"):
                                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "high", "rule_id": "sql-injection", "message": "Possible SQL injection: Unsanitized query string"})
                                elif first_arg.type == "identifier":
                                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "high", "rule_id": "sql-injection", "message": "Possible SQL injection: Variable used as query string"})

        # Check for hardcoded secrets
        if node.type == "assignment":
            left = node.named_children[0] if node.named_children else None
            right = node.named_children[-1] if node.named_children else None
            if left and right and left.type == "identifier" and right.type == "string":
                var_name = source_code[left.start_byte:left.end_byte].decode('utf-8').lower()
                if any(x in var_name for x in ["password", "secret", "key", "token"]):
                    hotspots.append({"start_line": node.start_point[0] + 1, "end_line": node.end_point[0] + 1, "severity": "high", "rule_id": "hardcoded-secret", "message": "Hardcoded secret detected"})
