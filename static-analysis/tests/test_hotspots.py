import pytest
from tree_sitter import Parser, Language
import tree_sitter_python
import tree_sitter_javascript
import tree_sitter_java

from sbp_analysis.languages.python import PythonPlugin
from sbp_analysis.languages.javascript import JavaScriptPlugin
from sbp_analysis.languages.java import JavaPlugin

def test_python_mutable_default():
    lang = Language(tree_sitter_python.language())
    parser = Parser(lang)
    code = b"def foo(a=[]):\n    pass"
    tree = parser.parse(code)
    
    plugin = PythonPlugin()
    hotspots = plugin.analyze_hotspots(tree.root_node, code)
    assert len(hotspots) == 1
    assert hotspots[0]['rule_id'] == 'mutable-default'
    assert hotspots[0]['severity'] == 'high'

def test_javascript_deep_nesting():
    lang = Language(tree_sitter_javascript.language())
    parser = Parser(lang)
    code = b"function a() { if(1) { if(2) { if(3) { if(4) { console.log(1); } } } } }"
    tree = parser.parse(code)
    
    plugin = JavaScriptPlugin()
    hotspots = plugin.analyze_hotspots(tree.root_node, code)
    assert any(h['rule_id'] == 'deep-nesting' for h in hotspots)

def test_java_loop_off_by_one():
    lang = Language(tree_sitter_java.language())
    parser = Parser(lang)
    code = b"class A { void b() { for(int i = 0; i <= arr.length; i++) {} } }"
    tree = parser.parse(code)
    
    plugin = JavaPlugin()
    hotspots = plugin.analyze_hotspots(tree.root_node, code)
    assert len(hotspots) == 1
    assert hotspots[0]['rule_id'] == 'loop-off-by-one'
    assert hotspots[0]['severity'] == 'warning'
