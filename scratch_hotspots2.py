import tree_sitter_python
from tree_sitter import Language, Parser

lang = Language(tree_sitter_python.language())
parser = Parser(lang)

code = b"""
def foo(x=[]):
    if x == None:
        pass
    try:
        pass
    except:
        pass
"""

tree = parser.parse(code)
hotspots = []
nesting_nodes = {"if_statement", "elif_clause", "else_clause", "match_statement", "conditional_expression", "for_statement", "while_statement", "try_statement", "with_statement"}

def walk(node, depth):
    if node.type in nesting_nodes:
        new_depth = depth + 1
        if new_depth == 4:
            hotspots.append({"severity": "warning", "rule_id": "deep-nesting", "message": "Deeply nested code (depth >= 4)"})
        elif new_depth == 6:
            hotspots.append({"severity": "high", "rule_id": "very-deep-nesting", "message": "Very deeply nested code (depth >= 6)"})
    else:
        new_depth = depth
        
    if node.type == "parameters":
        count = sum(1 for c in node.named_children)
        if count >= 6:
            hotspots.append({"severity": "warning", "rule_id": "long-parameter-list", "message": "Long parameter list (>= 6 parameters)"})
    
    if node.type == "except_clause":
        has_type = any(c.is_named and c.type != 'block' for c in node.children)
        if not has_type:
            hotspots.append({"severity": "warning", "rule_id": "bare-except", "message": "Bare except clause may swallow unexpected errors"})
        for c in node.named_children:
            if c.type == "block" and len(c.named_children) == 1 and c.named_children[0].type == "pass_statement":
                hotspots.append({"severity": "warning", "rule_id": "empty-except", "message": "Empty error handler"})
                
    if node.type == "comparison_operator":
        for c in node.children:
            if c.type == "none":
                ops = [x.type for x in node.children if not x.is_named]
                if "==" in ops or "!=" in ops:
                    hotspots.append({"severity": "warning", "rule_id": "wrong-equality", "message": "Use 'is' or 'is not' for None comparison"})

    if node.type == "default_parameter":
        val = node.named_children[-1]
        if val.type in ("list", "dictionary", "set"):
            hotspots.append({"severity": "high", "rule_id": "mutable-default", "message": "Mutable default argument is shared across calls"})

    for child in node.children:
        walk(child, new_depth)

walk(tree.root_node, 0)
print(hotspots)
