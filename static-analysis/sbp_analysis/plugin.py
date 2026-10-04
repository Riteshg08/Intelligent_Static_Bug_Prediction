from abc import ABC, abstractmethod
from typing import Set

class LanguagePlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def file_extensions(self) -> Set[str]:
        pass

    @property
    @abstractmethod
    def tree_sitter_language(self):
        pass

    @property
    @abstractmethod
    def function_query(self) -> str:
        """Tree-sitter query that finds functions/methods/constructors/lambdas"""
        pass

    @property
    @abstractmethod
    def branch_nodes(self) -> Set[str]:
        pass

    @property
    @abstractmethod
    def loop_nodes(self) -> Set[str]:
        pass

    @property
    @abstractmethod
    def nesting_nodes(self) -> Set[str]:
        pass

    @property
    @abstractmethod
    def parameter_nodes(self) -> Set[str]:
        pass

    @property
    @abstractmethod
    def local_variable_nodes(self) -> Set[str]:
        pass

    @property
    @abstractmethod
    def import_nodes(self) -> Set[str]:
        pass

    @property
    @abstractmethod
    def comment_nodes(self) -> Set[str]:
        pass

    def analyze_hotspots(self, root_node, source_code: bytes) -> list:
        """Return a list of dicts with keys: start_line, end_line, severity, rule_id, message."""
        return []
