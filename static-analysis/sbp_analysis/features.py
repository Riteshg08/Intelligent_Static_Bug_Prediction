import lizard
import logging
from typing import Dict, Any, List
from .models import FunctionExtractionResult
from .registry import registry
from tree_sitter import Parser, Node

logger = logging.getLogger(__name__)

def walk_tree(node: Node, callback):
    callback(node)
    for child in node.children:
        walk_tree(child, callback)

def extract_features(func: FunctionExtractionResult, file_content: bytes, file_imports: int = 0) -> Dict[str, Any]:
    plugin = registry.get_plugin_by_extension(f".{func.language.lower()}")
    if not plugin:
        plugin = registry._plugins.get(func.language)
        
    # Lizard metrics
    cc = 1
    loc = func.end_line - func.start_line + 1
    num_params_lizard = 0
    try:
        # lizard needs a language hint if possible, or just file path
        lizard_res = lizard.analyze_file.analyze_source_code(func.file_path, func.source_text)
        if lizard_res.function_list:
            lf = lizard_res.function_list[0]
            cc = lf.cyclomatic_complexity
            loc = lf.nloc
            num_params_lizard = lf.parameter_count
    except Exception as e:
        logger.debug(f"Lizard failed for {func.function_name}: {e}")

    # Tree-sitter structural metrics
    num_branches = 0
    num_loops = 0
    num_params_ts = 0
    num_local_vars = 0
    ast_node_count = 0
    num_call_expressions = 0
    num_return_statements = 0
    max_nesting_depth = 0
    
    # We parse just the function snippet
    if plugin:
        parser = Parser(plugin.tree_sitter_language)
        tree = parser.parse(func.source_text.encode('utf-8'))
        
        # State for walk
        state = {
            'branches': 0, 'loops': 0, 'params': 0, 'local_vars': 0,
            'nodes': 0, 'calls': 0, 'returns': 0,
            'current_depth': 0, 'max_depth': 0
        }
        
        branch_nodes = plugin.branch_nodes
        loop_nodes = plugin.loop_nodes
        param_nodes = plugin.parameter_nodes
        local_var_nodes = plugin.local_variable_nodes
        nesting_nodes = plugin.nesting_nodes
        
        def visit(node: Node, depth: int):
            if not node.is_named:
                for child in node.children:
                    visit(child, depth)
                return
                
            state['nodes'] += 1
            node_type = node.type
            
            if node_type in branch_nodes:
                state['branches'] += 1
            if node_type in loop_nodes:
                state['loops'] += 1
            if node_type in param_nodes:
                state['params'] += 1
            if node_type in local_var_nodes:
                state['local_vars'] += 1
            if node_type == "call_expression" or "call" in node_type:
                state['calls'] += 1
            if "return" in node_type:
                state['returns'] += 1
                
            new_depth = depth
            if node_type in nesting_nodes:
                new_depth += 1
                if new_depth > state['max_depth']:
                    state['max_depth'] = new_depth
                    
            for child in node.children:
                visit(child, new_depth)
                
        visit(tree.root_node, 0)
        
        num_branches = state['branches']
        num_loops = state['loops']
        num_params_ts = state['params']
        num_local_vars = state['local_vars']
        ast_node_count = state['nodes']
        num_call_expressions = state['calls']
        num_return_statements = state['returns']
        max_nesting_depth = state['max_depth']

    # Combine params
    num_parameters = max(num_params_lizard, num_params_ts)
    
    # Code smell count (simple heuristics)
    code_smell_count = 0
    if num_parameters > 5:
        code_smell_count += 1
    if loc > 100:
        code_smell_count += 1
    if max_nesting_depth > 4:
        code_smell_count += 1
    if cc > 10:
        code_smell_count += 1

    return {
        "cyclomatic_complexity": cc,
        "loc": loc,
        "function_length": func.end_line - func.start_line + 1,
        "max_nesting_depth": max_nesting_depth,
        "cognitive_complexity_approx": cc + max_nesting_depth, # simplified
        "num_parameters": num_parameters,
        "num_branches": num_branches,
        "num_loops": num_loops,
        "num_local_variables": num_local_vars,
        "num_return_statements": num_return_statements,
        "ast_node_count": ast_node_count,
        "num_call_expressions": num_call_expressions,
        "external_import_count": file_imports,
        "code_smell_count": code_smell_count,
        "duplicate_code_ratio": 0.0, # Will be computed globally if needed, MVP = 0
        "language": func.language,
        "is_method": "." in func.qualified_name or "::" in func.qualified_name or func.language in ["Java", "C#"] or "::" in func.source_text.split("(")[0],
        "content_hash": __import__('hashlib').md5(func.source_text.encode('utf-8')).hexdigest(),
        "function_code": func.source_text
    }
