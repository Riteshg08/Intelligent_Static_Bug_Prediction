from typing import Set
import tree_sitter_typescript
from ..plugin import LanguagePlugin

class TypeScriptPlugin(LanguagePlugin):
    @property
    def name(self) -> str:
        return "TypeScript"

    @property
    def file_extensions(self) -> Set[str]:
        return {".ts", ".tsx"}

    @property
    def tree_sitter_language(self):
        import tree_sitter
        return tree_sitter.Language(tree_sitter_typescript.language_typescript())

    @property
    def function_query(self) -> str:
        return """
        (function_declaration
          name: (identifier) @name) @function
        (generator_function_declaration
          name: (identifier) @name) @function
        (method_definition
          name: (property_identifier) @name) @function
        (variable_declarator
          name: (identifier) @name
          value: (arrow_function)) @function
        (variable_declarator
          name: (identifier) @name
          value: (function_expression)) @function
        """

    @property
    def branch_nodes(self) -> Set[str]:
        return {"if_statement", "else_clause", "switch_statement", "switch_case", "switch_default", "ternary_expression"}

    @property
    def loop_nodes(self) -> Set[str]:
        return {"for_statement", "for_in_statement", "while_statement", "do_statement"}

    @property
    def nesting_nodes(self) -> Set[str]:
        return {"statement_block", "if_statement", "for_statement", "while_statement", "try_statement", "catch_clause"}

    @property
    def parameter_nodes(self) -> Set[str]:
        return {"formal_parameters"}

    @property
    def local_variable_nodes(self) -> Set[str]:
        return {"variable_declaration", "lexical_declaration"}

    @property
    def import_nodes(self) -> Set[str]:
        return {"import_statement"}

    @property
    def comment_nodes(self) -> Set[str]:
        return {"comment"}
