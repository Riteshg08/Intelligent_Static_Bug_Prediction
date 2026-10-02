from typing import Set
import tree_sitter_cpp
from ..plugin import LanguagePlugin

class CppPlugin(LanguagePlugin):
    @property
    def name(self) -> str:
        return "C++"

    @property
    def file_extensions(self) -> Set[str]:
        return {".cpp", ".cc", ".cxx", ".hpp", ".hxx"}

    @property
    def tree_sitter_language(self):
        import tree_sitter
        return tree_sitter.Language(tree_sitter_cpp.language())

    @property
    def function_query(self) -> str:
        return """
        (function_definition
          declarator: (function_declarator
            declarator: (identifier) @name)) @function
        (function_definition
          declarator: (function_declarator
            declarator: (field_identifier) @name)) @function
        (function_definition
          declarator: (function_declarator
            declarator: (qualified_identifier
              name: (identifier) @name))) @function
        """

    @property
    def branch_nodes(self) -> Set[str]:
        return {"if_statement", "else_clause", "switch_statement", "case_statement", "default_statement", "conditional_expression"}

    @property
    def loop_nodes(self) -> Set[str]:
        return {"for_statement", "for_range_loop", "while_statement", "do_statement"}

    @property
    def nesting_nodes(self) -> Set[str]:
        return {"compound_statement", "if_statement", "for_statement", "for_range_loop", "while_statement", "do_statement", "try_statement", "catch_clause"}

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
