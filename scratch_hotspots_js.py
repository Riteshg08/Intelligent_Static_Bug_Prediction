import tree_sitter_javascript
from tree_sitter import Language, Parser

lang = Language(tree_sitter_javascript.language())
parser = Parser(lang)

code = b"""
function foo(a,b,c,d,e,f) {
    if (x = 0) {}
    for (let i = 0; i <= arr.length; i++) {}
    try {
    } catch (e) {
    }
    if (x == null) {}
}
"""

tree = parser.parse(code)
hotspots = []
nesting_nodes = {"statement_block", "if_statement", "for_statement", "while_statement", "try_statement", "catch_clause"}

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
        count = sum(1 for c in node.named_children)
        if count >= 6:
            hotspots.append({"severity": "warning", "rule_id": "long-parameter-list", "message": "Long parameter list (>= 6 parameters)"})
            
    if node.type == "catch_clause":
        body = node.child_by_field_name("body")
        if body and len(body.named_children) == 0:
            hotspots.append({"severity": "warning", "rule_id": "empty-catch", "message": "Empty catch block may swallow unexpected errors"})
            
    if node.type == "binary_expression":
        op = node.child_by_field_name("operator")
        if op and op.type in ("==", "!="):
            hotspots.append({"severity": "warning", "rule_id": "loose-equality", "message": "Use strict equality (=== or !==) instead of loose equality"})
        
        if op and op.type == "<=":
            right = node.child_by_field_name("right")
            if right and right.type == "member_expression":
                prop = right.child_by_field_name("property")
                if prop and prop.type == "property_identifier" and source_code[prop.start_byte:prop.end_byte] == b"length":
                    hotspots.append({"severity": "warning", "rule_id": "loop-off-by-one", "message": "Loop condition uses <= with length, possible off-by-one error"})
                    
    if node.type == "assignment_expression":
        parent = node.parent
        while parent and parent.type == "parenthesized_expression":
            parent = parent.parent
        if parent and parent.type == "if_statement" and parent.child_by_field_name("condition") == node:
            hotspots.append({"severity": "high", "rule_id": "assignment-in-condition", "message": "Assignment inside a condition is likely a typo for equality"})

    for child in node.children:
        walk(child, new_depth)

source_code = code
walk(tree.root_node, 0)
print(hotspots)
