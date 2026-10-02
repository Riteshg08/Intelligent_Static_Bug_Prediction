# Adding a Language

This guide explains how to add a new language to the Intelligent Static Bug Prediction system.
The system is designed with a plugin architecture, meaning the core analysis engine is entirely language-agnostic. To add a new language (e.g., Rust), you only need to create a single plugin file and register it.

## Step-by-Step Guide

### 1. Install Tree-sitter Grammar
First, you need the tree-sitter grammar for your language. For Rust, you would add `tree-sitter-rust` to the dependencies in `pyproject.toml`.

### 2. Create the Plugin Class
Create a new file in `static-analysis/sbp_analysis/languages/` (e.g., `rust.py`).
Implement the `LanguagePlugin` interface from `sbp_analysis.plugin`.

Example (`rust.py`):
```python
from typing import Set
import tree_sitter_rust
from ..plugin import LanguagePlugin

class RustPlugin(LanguagePlugin):
    @property
    def name(self) -> str:
        return "Rust"

    @property
    def file_extensions(self) -> Set[str]:
        return {".rs"}

    @property
    def tree_sitter_language(self):
        import tree_sitter
        return tree_sitter.Language(tree_sitter_rust.language(), "rust")

    @property
    def function_query(self) -> str:
        return '''
        (function_item
          name: (identifier) @name) @function
        '''

    @property
    def branch_nodes(self) -> Set[str]:
        return {"if_expression", "match_expression"}

    @property
    def loop_nodes(self) -> Set[str]:
        return {"loop_expression", "while_expression", "for_expression"}

    @property
    def nesting_nodes(self) -> Set[str]:
        return {"block", "if_expression", "loop_expression"}

    @property
    def parameter_nodes(self) -> Set[str]:
        return {"parameters"}

    @property
    def local_variable_nodes(self) -> Set[str]:
        return {"let_declaration"}

    @property
    def import_nodes(self) -> Set[str]:
        return {"use_declaration"}

    @property
    def comment_nodes(self) -> Set[str]:
        return {"line_comment", "block_comment"}
```

### 3. Register the Plugin
Open `static-analysis/sbp_analysis/registry.py` and register your new plugin in the `_register_default_plugins` method.

```python
from .languages.rust import RustPlugin

class LanguageRegistry:
    ...
    def _register_default_plugins(self):
        ...
        self.register(RustPlugin())
```

### 4. Test It
Add a small test snippet to `tests/test_parser.py` to ensure your tree-sitter query correctly extracts functions and doesn't crash on invalid code.

Done! The rest of the pipeline (feature extraction, ML prediction, UI) will automatically support the new language.
