from typing import Set
import tree_sitter_java
from ..plugin import LanguagePlugin

class JavaPlugin(LanguagePlugin):
    @property
    def name(self) -> str:
        return "Java"

    @property
    def file_extensions(self) -> Set[str]:
        return {".java"}

    @property
    def tree_sitter_language(self):
        import tree_sitter
        return tree_sitter.Language(tree_sitter_java.language())

    @property
    def function_query(self) -> str:
        return """
        (method_declaration
          name: (identifier) @name) @function
        (constructor_declaration
          name: (identifier) @name) @function
        """

    @property
    def branch_nodes(self) -> Set[str]:
        return {"if_statement", "switch_label", "switch_expression", "ternary_expression"}

    @property
    def loop_nodes(self) -> Set[str]:
        return {"for_statement", "enhanced_for_statement", "while_statement", "do_statement"}

    @property
    def nesting_nodes(self) -> Set[str]:
        return {"block", "if_statement", "for_statement", "enhanced_for_statement", "while_statement", "try_statement", "catch_clause"}

    @property
    def parameter_nodes(self) -> Set[str]:
        return {"formal_parameters"}

    @property
    def local_variable_nodes(self) -> Set[str]:
        return {"local_variable_declaration"}

    @property
    def import_nodes(self) -> Set[str]:
        return {"import_declaration"}

    @property
    def comment_nodes(self) -> Set[str]:
        return {"block_comment", "line_comment"}
