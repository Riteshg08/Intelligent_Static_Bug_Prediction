import tree_sitter_python
from tree_sitter import Language, Parser, Query

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
query_str = """
(except_clause !type) @bare_except
(default_parameter value: [(list) (dictionary)]) @mutable_default
(comparison_operator right: (none)) @eq_none
"""
query = Query(lang, query_str)
for match, _ in query.matches(tree.root_node):
    print(match)
