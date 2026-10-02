import hashlib
import logging
from typing import List, Optional, Dict
from tree_sitter import Parser
from .models import FunctionExtractionResult
from .registry import registry

logger = logging.getLogger(__name__)

# Simple in-memory cache keyed by content_hash to avoid parsing same file content twice
_parse_cache: Dict[str, List[FunctionExtractionResult]] = {}

def clear_cache():
    _parse_cache.clear()

def _compute_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

def extract_functions(file_path: str, content_bytes: bytes, language: str) -> List[FunctionExtractionResult]:
    plugin = registry.get_plugin_by_extension(f".{language.lower()}")
    if not plugin:
        plugin = registry._plugins.get(language) # fallback lookup
    if not plugin:
        logger.warning(f"No plugin found for language {language} in {file_path}")
        return []

    parser = Parser(plugin.tree_sitter_language)
    
    try:
        tree = parser.parse(content_bytes)
    except Exception as e:
        logger.warning(f"Failed to parse {file_path}: {e}")
        return []
        
    from tree_sitter import Query, QueryCursor
    query = Query(plugin.tree_sitter_language, plugin.function_query)
    cursor = QueryCursor(query)
    matches = cursor.matches(tree.root_node)
    
    results = []
    content_str = content_bytes.decode('utf-8', errors='replace')
    
    processed_nodes = set()
    for pattern_idx, captures in matches:
        func_nodes = captures.get('function', [])
        name_nodes = captures.get('name', [])
        
        if not func_nodes:
            continue
            
        node = func_nodes[0]
        if id(node) in processed_nodes:
            continue
        processed_nodes.add(id(node))
        
        name_node = name_nodes[0] if name_nodes else None
        
        func_name = ""
        if name_node:
            func_name = content_bytes[name_node.start_byte:name_node.end_byte].decode('utf-8', errors='replace')
        else:
            func_name = "<anonymous>"
            
        start_line = node.start_point[0] + 1
        end_line = node.end_point[0] + 1
        
        source_text = content_bytes[node.start_byte:node.end_byte].decode('utf-8', errors='replace')
        func_hash = _compute_hash(source_text.encode('utf-8'))
        
        qualified_name = func_name
        
        results.append(FunctionExtractionResult(
            file_path=file_path,
            language=plugin.name,
            function_name=func_name,
            qualified_name=qualified_name,
            start_line=start_line,
            end_line=end_line,
            source_text=source_text,
            content_hash=func_hash
        ))
        
    return results

def parse_file(file_path: str) -> List[FunctionExtractionResult]:
    plugin = registry.get_plugin_by_file_path(file_path)
    if not plugin:
        logger.info(f"Skipping unsupported file: {file_path}")
        return []
        
    try:
        with open(file_path, 'rb') as f:
            content_bytes = f.read()
    except Exception as e:
        logger.warning(f"Could not read {file_path}: {e}")
        return []
        
    file_hash = _compute_hash(content_bytes)
    if file_hash in _parse_cache:
        # Cache hit
        # Note: the file_path in cached results might be different if content is identical,
        # but the content is the same.
        cached_results = _parse_cache[file_hash]
        return [
            FunctionExtractionResult(
                file_path=file_path,
                language=r.language,
                function_name=r.function_name,
                qualified_name=r.qualified_name,
                start_line=r.start_line,
                end_line=r.end_line,
                source_text=r.source_text,
                content_hash=r.content_hash
            ) for r in cached_results
        ]
        
    results = extract_functions(file_path, content_bytes, plugin.name)
    _parse_cache[file_hash] = results
    return results
