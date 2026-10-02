from typing import Set
import tree_sitter_c
from ..plugin import LanguagePlugin

class CPlugin(LanguagePlugin):
    @property
    def name(self) -> str:
        return "C"

    @property
    def file_extensions(self) -> Set[str]:
        return {".c", ".h"}

    @property
    def tree_sitter_language(self):
        import tree_sitter
        return tree_sitter.Language(tree_sitter_c.language())

    @property
    def function_query(self) -> str:
        return """
        (function_definition
          declarator: (function_declarator
            declarator: (identifier) @name)) @function
        """

    @property
    def branch_nodes(self) -> Set[str]:
        return {"if_statement", "else_clause", "switch_statement", "case_statement", "default_statement"}

    @property
    def loop_nodes(self) -> Set[str]:
        return {"for_statement", "while_statement", "do_statement"}

    @property
    def nesting_nodes(self) -> Set[str]:
        return {"compound_statement", "if_statement", "for_statement", "while_statement", "do_statement"}

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
