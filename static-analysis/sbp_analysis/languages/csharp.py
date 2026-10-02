from typing import Set
import tree_sitter_c_sharp
from ..plugin import LanguagePlugin

class CSharpPlugin(LanguagePlugin):
    @property
    def name(self) -> str:
        return "C#"

    @property
    def file_extensions(self) -> Set[str]:
        return {".cs"}

    @property
    def tree_sitter_language(self):
        import tree_sitter
        return tree_sitter.Language(tree_sitter_c_sharp.language())

    @property
    def function_query(self) -> str:
        return """
        (method_declaration
          name: (identifier) @name) @function
        (constructor_declaration
          name: (identifier) @name) @function
        (local_function_statement
          name: (identifier) @name) @function
        """

    @property
    def branch_nodes(self) -> Set[str]:
        return {"if_statement", "else_clause", "switch_statement", "switch_expression", "conditional_expression"}

    @property
    def loop_nodes(self) -> Set[str]:
        return {"for_statement", "foreach_statement", "while_statement", "do_statement"}

    @property
    def nesting_nodes(self) -> Set[str]:
        return {"block", "if_statement", "for_statement", "foreach_statement", "while_statement", "do_statement", "try_statement", "catch_clause", "finally_clause"}

    @property
    def parameter_nodes(self) -> Set[str]:
        return {"parameter_list"}

    @property
    def local_variable_nodes(self) -> Set[str]:
        return {"local_declaration_statement"}

    @property
    def import_nodes(self) -> Set[str]:
        return {"using_directive"}

    @property
    def comment_nodes(self) -> Set[str]:
        return {"comment"}
