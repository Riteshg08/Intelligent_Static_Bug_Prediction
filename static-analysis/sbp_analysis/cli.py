import argparse
import pandas as pd
import os
import glob
from .parser import parse_file
from .features import extract_features
from .registry import registry
from tree_sitter import Parser, Query, QueryCursor

def analyze_directory(directory: str) -> pd.DataFrame:
    results = []
    
    skipped = 0
    parsed = 0
    
    for root, _, files in os.walk(directory):
        if "node_modules" in root or ".git" in root or ".venv" in root:
            continue
        for file in files:
            file_path = os.path.join(root, file)
            plugin = registry.get_plugin_by_file_path(file_path)
            if not plugin:
                skipped += 1
                continue
                
            try:
                with open(file_path, 'rb') as f:
                    content_bytes = f.read()
                    
                # Count file imports
                parser = Parser(plugin.tree_sitter_language)
                tree = parser.parse(content_bytes)
                import_nodes = plugin.import_nodes
                import_count = 0
                def count_imports(node):
                    nonlocal import_count
                    if node.type in import_nodes:
                        import_count += 1
                    for child in node.children:
                        count_imports(child)
                count_imports(tree.root_node)
                
                funcs = parse_file(file_path)
                parsed += 1
                for func in funcs:
                    feats = extract_features(func, content_bytes, import_count)
                    # Add identifiers
                    feats['file_path'] = file_path
                    feats['function_name'] = func.function_name
                    results.append(feats)
            except Exception as e:
                skipped += 1
                
    print(f"Parsed {parsed} files. Skipped {skipped} files.")
    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description="Extract features from a directory.")
    parser.add_argument("path", help="Path to directory or file")
    parser.add_argument("--out", required=True, help="Output CSV file")
    
    args = parser.parse_args()
    
    if os.path.isdir(args.path):
        df = analyze_directory(args.path)
    else:
        # Single file
        funcs = parse_file(args.path)
        with open(args.path, 'rb') as f:
            content_bytes = f.read()
        feats = []
        for func in funcs:
            f = extract_features(func, content_bytes, 0)
            f['file_path'] = args.path
            f['function_name'] = func.function_name
            feats.append(f)
        df = pd.DataFrame(feats)
        
    df.to_csv(args.out, index=False)
    print(f"Saved {len(df)} functions to {args.out}")

if __name__ == "__main__":
    main()
