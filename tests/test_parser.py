import pytest
import tempfile
import os
from sbp_analysis import parse_file, clear_cache, registry, LanguagePlugin
from typing import Set

def create_temp_file(content: str, suffix: str) -> str:
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(content)
    return path

@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    clear_cache()
    yield
    clear_cache()

def test_unsupported_extension():
    path = create_temp_file("hello world", ".txt")
    results = parse_file(path)
    assert len(results) == 0
    os.remove(path)

def test_empty_file():
    path = create_temp_file("", ".py")
    results = parse_file(path)
    assert len(results) == 0
    os.remove(path)

def test_syntax_error_file():
    path = create_temp_file("def foo():\n  pass\ndef unclosed(\n", ".py")
    results = parse_file(path)
    assert len(results) >= 1
    names = [r.function_name for r in results]
    assert "foo" in names
    os.remove(path)

def test_python_normal():
    code = """
def my_func():
    pass
    
class MyClass:
    def my_method(self):
        pass
        
    def nested(self):
        def inner():
            pass
"""
    path = create_temp_file(code, ".py")
    results = parse_file(path)
    assert len(results) >= 3
    names = {r.function_name for r in results}
    assert "my_func" in names
    assert "my_method" in names
    assert "nested" in names
    os.remove(path)

def test_javascript_normal():
    code = """
function add(a, b) { return a + b; }
const sub = (a, b) => a - b;
class Calc {
  mul(a, b) { return a * b; }
}
"""
    path = create_temp_file(code, ".js")
    results = parse_file(path)
    names = {r.function_name for r in results}
    assert "add" in names
    assert "mul" in names
    os.remove(path)

def test_java_normal():
    code = """
public class App {
    public App() {}
    public void run() {}
}
"""
    path = create_temp_file(code, ".java")
    results = parse_file(path)
    names = {r.function_name for r in results}
    assert "App" in names
    assert "run" in names
    os.remove(path)

def test_c_normal():
    code = """
int main() { return 0; }
void helper() {}
"""
    path = create_temp_file(code, ".c")
    results = parse_file(path)
    names = {r.function_name for r in results}
    assert "main" in names
    assert "helper" in names
    os.remove(path)

def test_cpp_normal():
    code = """
class MyClass {
public:
    void method1() {}
};
void MyClass::method2() {}
"""
    path = create_temp_file(code, ".cpp")
    results = parse_file(path)
    names = {r.function_name for r in results}
    assert "method1" in names
    assert "method2" in names
    os.remove(path)

def test_csharp_normal():
    code = """
class Program {
    static void Main() {
        void LocalFunc() {}
    }
}
"""
    path = create_temp_file(code, ".cs")
    results = parse_file(path)
    names = {r.function_name for r in results}
    assert "Main" in names
    assert "LocalFunc" in names
    os.remove(path)

def test_go_normal():
    code = """
package main
func main() {}
func (m *MyType) Method() {}
"""
    path = create_temp_file(code, ".go")
    results = parse_file(path)
    names = {r.function_name for r in results}
    assert "main" in names
    assert "Method" in names
    os.remove(path)

def test_typescript_normal():
    code = """
function add(a: number): number { return a; }
class Calc { mul() {} }
"""
    path = create_temp_file(code, ".ts")
    results = parse_file(path)
    names = {r.function_name for r in results}
    assert "add" in names
    assert "mul" in names
    os.remove(path)

def test_dummy_plugin():
    class DummyPlugin(LanguagePlugin):
        @property
        def name(self) -> str: return "Dummy"
        @property
        def file_extensions(self) -> Set[str]: return {".dummy"}
        @property
        def tree_sitter_language(self): return None
        @property
        def function_query(self) -> str: return ""
        @property
        def branch_nodes(self) -> Set[str]: return set()
        @property
        def loop_nodes(self) -> Set[str]: return set()
        @property
        def nesting_nodes(self) -> Set[str]: return set()
        @property
        def parameter_nodes(self) -> Set[str]: return set()
        @property
        def local_variable_nodes(self) -> Set[str]: return set()
        @property
        def import_nodes(self) -> Set[str]: return set()
        @property
        def comment_nodes(self) -> Set[str]: return set()

    plugin = DummyPlugin()
    registry.register(plugin)
    assert registry.get_plugin_by_extension(".dummy") is not None
