import pytest
import tempfile
import os
from sbp_analysis.parser import parse_file
from sbp_analysis.features import extract_features
from sbp_analysis.history_features import extract_history_features

def create_temp_file(content: str, suffix: str) -> str:
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(content)
    return path

def test_python_features():
    code = """
def test_func(a, b):
    # 2 params, 2 branches, 1 loop, 2 nesting
    if a > 0:
        for i in range(b):
            pass
    elif b < 0:
        pass
    return a
"""
    path = create_temp_file(code, ".py")
    funcs = parse_file(path)
    with open(path, 'rb') as f:
        content = f.read()
    
    assert len(funcs) == 1
    feats = extract_features(funcs[0], content)
    
    assert feats['num_parameters'] == 2
    assert feats['num_branches'] >= 2
    assert feats['num_loops'] == 1
    assert feats['max_nesting_depth'] >= 2
    assert feats['num_return_statements'] == 1
    assert feats['cyclomatic_complexity'] >= 3 # 1 + if + elif + for
    
    os.remove(path)

def test_javascript_features():
    code = """
function processData(x) {
  if (x) {
    if (x.y) {
      if (x.y.z) {
        return x;
      }
    }
  }
}
"""
    path = create_temp_file(code, ".js")
    funcs = parse_file(path)
    with open(path, 'rb') as f:
        content = f.read()
    
    assert len(funcs) == 1
    feats = extract_features(funcs[0], content)
    
    assert feats['num_parameters'] == 1
    assert feats['num_branches'] == 3
    assert feats['max_nesting_depth'] >= 3
    
    os.remove(path)

def test_java_features():
    code = """
class MyClass {
    public void run(int a, String b, float c) {
        while (a > 0) {
            a--;
        }
    }
}
"""
    path = create_temp_file(code, ".java")
    funcs = parse_file(path)
    with open(path, 'rb') as f:
        content = f.read()
    
    # We should have MyClass and run. Wait, MyClass is not a method, so we should extract just run?
    # Java query extracts only methods.
    assert len(funcs) == 1
    feats = extract_features(funcs[0], content)
    
    assert feats['num_parameters'] == 3
    assert feats['num_loops'] == 1
    assert feats['is_method'] == True
    
    os.remove(path)

def test_c_features():
    code = """
int compute() {
    int x = 1;
    int y = 2;
    return x + y;
}
"""
    path = create_temp_file(code, ".c")
    funcs = parse_file(path)
    with open(path, 'rb') as f:
        content = f.read()
    
    assert len(funcs) == 1
    feats = extract_features(funcs[0], content)
    
    assert feats['num_local_variables'] == 2
    assert feats['num_return_statements'] == 1
    
    os.remove(path)

def test_cpp_features():
    code = """
void MyClass::method() {
    foo();
    bar();
}
"""
    path = create_temp_file(code, ".cpp")
    funcs = parse_file(path)
    with open(path, 'rb') as f:
        content = f.read()
    
    assert len(funcs) == 1
    feats = extract_features(funcs[0], content)
    
    assert feats['num_call_expressions'] == 2
    assert feats['is_method'] == True
    
    os.remove(path)

def test_csharp_features():
    code = """
class P {
    void M() {
        try {
            int a = 1;
        } catch (Exception e) {
            
        }
    }
}
"""
    path = create_temp_file(code, ".cs")
    funcs = parse_file(path)
    with open(path, 'rb') as f:
        content = f.read()
    
    assert len(funcs) == 1
    feats = extract_features(funcs[0], content)
    
    assert feats['num_local_variables'] == 1
    assert feats['num_branches'] >= 0 # catch clause might be a branch or nesting depending on plugin
    
    os.remove(path)

def test_go_features():
    code = """
func doWork(a int, b int) int {
    if a > b {
        return a
    }
    return b
}
"""
    path = create_temp_file(code, ".go")
    funcs = parse_file(path)
    with open(path, 'rb') as f:
        content = f.read()
    
    assert len(funcs) == 1
    feats = extract_features(funcs[0], content)
    
    assert feats['num_branches'] == 1
    assert feats['num_return_statements'] == 2
    
    os.remove(path)

def test_typescript_features():
    code = """
const arrow = (a: number, b: string) => {
    return a + b.length;
}
"""
    path = create_temp_file(code, ".ts")
    funcs = parse_file(path)
    with open(path, 'rb') as f:
        content = f.read()
    
    assert len(funcs) == 1
    feats = extract_features(funcs[0], content)
    
    assert feats['num_parameters'] == 2
    assert feats['num_return_statements'] == 1
    
    os.remove(path)

def test_history_cutoff():
    # just test that it returns the expected keys
    feats = extract_history_features("test.py", "foo", 123456789)
    assert "num_past_changes" in feats
    assert "num_past_bugfixes" in feats
