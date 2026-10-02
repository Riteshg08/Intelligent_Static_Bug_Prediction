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
