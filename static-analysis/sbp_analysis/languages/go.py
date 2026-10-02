from typing import Set
import tree_sitter_go
from ..plugin import LanguagePlugin

class GoPlugin(LanguagePlugin):
    @property
    def name(self) -> str:
        return "Go"

    @property
    def file_extensions(self) -> Set[str]:
        return {".go"}

    @property
    def tree_sitter_language(self):
        import tree_sitter
        return tree_sitter.Language(tree_sitter_go.language())

    @property
    def function_query(self) -> str:
        return """
        (function_declaration
          name: (identifier) @name) @function
        (method_declaration
          name: (field_identifier) @name) @function
        (func_literal) @function
        """

    @property
    def branch_nodes(self) -> Set[str]:
        return {"if_statement", "expression_switch_statement", "type_switch_statement", "select_statement"}

    @property
    def loop_nodes(self) -> Set[str]:
        return {"for_statement"}

    @property
    def nesting_nodes(self) -> Set[str]:
        return {"block", "if_statement", "for_statement", "expression_case", "type_case", "communication_case"}

    @property
    def parameter_nodes(self) -> Set[str]:
        return {"parameter_list"}

    @property
    def local_variable_nodes(self) -> Set[str]:
        return {"short_var_declaration", "var_declaration"}

    @property
    def import_nodes(self) -> Set[str]:
        return {"import_spec"}

    @property
    def comment_nodes(self) -> Set[str]:
        return {"comment"}
