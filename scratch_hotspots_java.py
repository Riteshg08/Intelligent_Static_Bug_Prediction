import tree_sitter_java
from tree_sitter import Language, Parser

lang = Language(tree_sitter_java.language())
parser = Parser(lang)

code = b"""
class Foo {
    void foo(int a, int b, int c, int d, int e, int f) {
        if (x = 0) {}
        for (int i = 0; i <= arr.length; i++) {}
        try {
        } catch (Exception e) {
        }
        if (str1 == str2) {}
    }
}
"""

tree = parser.parse(code)
hotspots = []
nesting_nodes = {"block", "if_statement", "for_statement", "enhanced_for_statement", "while_statement", "try_statement", "catch_clause"}

def walk(node, depth):
    if node.type in nesting_nodes:
        new_depth = depth + 1
        if new_depth == 4:
            hotspots.append({"severity": "warning", "rule_id": "deep-nesting", "message": "Deeply nested code (depth >= 4)"})
        elif new_depth == 6:
            hotspots.append({"severity": "high", "rule_id": "very-deep-nesting", "message": "Very deeply nested code (depth >= 6)"})
    else:
        new_depth = depth
        
    if node.type == "formal_parameters":
        count = sum(1 for c in node.named_children if c.type == "formal_parameter")
        if count >= 6:
            hotspots.append({"severity": "warning", "rule_id": "long-parameter-list", "message": "Long parameter list (>= 6 parameters)"})
            
    if node.type == "catch_clause":
        body = node.child_by_field_name("body")
        if body and len(body.named_children) == 0:
            hotspots.append({"severity": "warning", "rule_id": "empty-catch", "message": "Empty catch block may swallow unexpected errors"})
            
    if node.type == "binary_expression":
        op = node.child_by_field_name("operator")
        if op and op.type == "==":
            # We can't know for sure if it's String, but we can flag it.
            # "loose or wrong equality (Java String ==)" - we can check if variable name suggests string or just flag it as warning
            # It's hard to type check. We can just flag all `==`? No, that's too noisy.
            pass
            
        if op and op.type == "<=":
            right = node.child_by_field_name("right")
            if right and right.type == "field_access":
                prop = right.child_by_field_name("field")
                if prop and prop.type == "identifier" and source_code[prop.start_byte:prop.end_byte] == b"length":
                    hotspots.append({"severity": "warning", "rule_id": "loop-off-by-one", "message": "Loop condition uses <= with length, possible off-by-one error"})
                    
    if node.type == "assignment_expression":
        parent = node.parent
        while parent and parent.type == "parenthesized_expression":
            parent = parent.parent
        if parent and parent.type == "if_statement":
            hotspots.append({"severity": "high", "rule_id": "assignment-in-condition", "message": "Assignment inside a condition is likely a typo for equality"})

    for child in node.children:
        walk(child, new_depth)

source_code = code
walk(tree.root_node, 0)
print(hotspots)
