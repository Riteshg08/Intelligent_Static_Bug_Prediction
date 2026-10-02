import os
import logging
from typing import Dict, Optional, Type
from .plugin import LanguagePlugin
from .languages.python import PythonPlugin
from .languages.javascript import JavaScriptPlugin
from .languages.typescript import TypeScriptPlugin
from .languages.java import JavaPlugin
from .languages.c import CPlugin
from .languages.cpp import CppPlugin
from .languages.csharp import CSharpPlugin
from .languages.go import GoPlugin

logger = logging.getLogger(__name__)

class LanguageRegistry:
    def __init__(self):
        self._plugins: Dict[str, LanguagePlugin] = {}
        self._extension_map: Dict[str, LanguagePlugin] = {}
        self._register_default_plugins()

    def _register_default_plugins(self):
        self.register(PythonPlugin())
        self.register(JavaScriptPlugin())
        self.register(TypeScriptPlugin())
        self.register(JavaPlugin())
        self.register(CPlugin())
        self.register(CppPlugin())
        self.register(CSharpPlugin())
        self.register(GoPlugin())

    def register(self, plugin: LanguagePlugin):
        self._plugins[plugin.name] = plugin
        for ext in plugin.file_extensions:
            self._extension_map[ext] = plugin

    def get_plugin_by_extension(self, extension: str) -> Optional[LanguagePlugin]:
        return self._extension_map.get(extension)

    def get_plugin_by_file_path(self, file_path: str) -> Optional[LanguagePlugin]:
        _, ext = os.path.splitext(file_path)
        if ext:
            plugin = self.get_plugin_by_extension(ext)
            if plugin:
                return plugin
            
        # Fallback to shebang check if no extension matched
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('#!'):
                    if 'python' in first_line:
                        return self._plugins.get('Python')
                    if 'node' in first_line:
                        return self._plugins.get('JavaScript')
        except Exception:
            pass
        return None

registry = LanguageRegistry()
