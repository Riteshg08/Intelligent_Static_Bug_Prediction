import os
import re
import yaml
import tempfile
import pandas as pd
from datetime import datetime
from pydriller import Repository
import sys

# Import our feature extractor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../static-analysis')))
from sbp_analysis.cli import analyze_directory

# Ensure plugins are complete (they just parse AST)
def extract_features(code: str, language: str, file_path: str = "temp"):
    # Since existing extractors expect a file_path, we write code to a temp file
    # and call the extractor.
    ext = {"Python": ".py", "JavaScript": ".js", "TypeScript": ".ts", "Java": ".java", "Go": ".go"}.get(language, ".txt")
    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_path = os.path.join(tmpdirname, f"temp{ext}")
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(code)
            
        try:
            df, _, _ = analyze_directory(tmpdirname)
            if not df.empty:
                return df.to_dict('records')
        except Exception as e:
            pass
    return []

def is_bug_fix(msg):
    msg = msg.lower()
    if 'merge' in msg: return False
    if 'refactor' in msg: return False
    if 'test' in msg and 'fix' not in msg: return False
    if 'doc' in msg and 'fix' not in msg: return False
    
    keywords = ['fix', 'bug', 'issue #', 'resolves #', 'closes #']
    for kw in keywords:
        if kw in msg:
            return True
    return False

def is_valid_file(filename, language):
    exts = {
        "Python": [".py"],
        "JavaScript": [".js", ".jsx"],
        "TypeScript": [".ts", ".tsx"],
        "Java": [".java"],
        "Go": [".go"]
    }
    valid_exts = exts.get(language, [])
    return any(filename.endswith(e) for e in valid_exts)

def main():
    repo_file = os.path.join(os.path.dirname(__file__), 'repos.yaml')
    with open(repo_file, 'r') as f:
        repos = yaml.safe_load(f)
        
    dataset = []
    
    clones_dir = os.path.join(os.path.dirname(__file__), 'clones')
    if not os.path.exists(clones_dir):
        os.makedirs(clones_dir)
        
    # Process up to 500 commits per repo to keep it manageable but real
    for lang, urls in repos.items():
        if lang not in ['Python', 'JavaScript', 'TypeScript', 'Java', 'Go']:
            continue
            
        print(f"Processing {lang} repositories...")
        for url in urls:
            repo_name = url.split('/')[-1].replace('.git', '')
            repo_path = os.path.join(clones_dir, repo_name)
            
            if not os.path.exists(repo_path):
                print(f"Cloning {url} into {repo_path} (depth 1000)...")
                os.system(f"git clone --depth 1000 {url} {repo_path}")
                
            print(f"Mining {repo_name}...")
            try:
                # We want SZZ
                count = 0
                for commit in Repository(repo_path, order='reverse').traverse_commits():
                    if count >= 300: # Limit per repo to speed up
                        break
                        
                    if is_bug_fix(commit.msg):
                        for m in commit.modified_files:
                            if m.source_code_before and is_valid_file(m.filename, lang):
                                # It's a bug fix. The file before the commit was buggy.
                                buggy_funcs = extract_features(m.source_code_before, lang)
                                
                                # Which function was buggy?
                                changed_lines = [l[0] for l in m.diff_parsed.get('deleted', [])]
                                if not changed_lines:
                                    changed_lines = [l[0] for l in m.diff_parsed.get('added', [])]
                                    
                                for func in buggy_funcs:
                                    func_start = func.get('start_line', 0)
                                    func_end = func.get('end_line', 99999)
                                    
                                    # check if changed lines overlap with this function
                                    if any(func_start <= line <= func_end for line in changed_lines):
                                        # This function was modified in a bug fix -> it's buggy
                                        func['buggy'] = 1
                                        func['commit_hash'] = commit.hash
                                        func['commit_date'] = commit.committer_date.isoformat()
                                        func['repo'] = repo_name
                                        func['language'] = lang
                                        dataset.append(func)
                                        count += 1
                                    else:
                                        # Function not touched by bug fix -> sample as clean
                                        if count % 2 == 0: # 1:1 or 1:2 ratio
                                            func['buggy'] = 0
                                            func['commit_hash'] = commit.hash
                                            func['commit_date'] = commit.committer_date.isoformat()
                                            func['repo'] = repo_name
                                            func['language'] = lang
                                            dataset.append(func)
                                            count += 1
                                            
            except Exception as e:
                print(f"Error processing {repo_name}: {e}")
                
    out_dir = os.path.join(os.path.dirname(__file__), 'output')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    df = pd.DataFrame(dataset)
    if not df.empty:
        df.to_csv(os.path.join(out_dir, 'dataset.csv'), index=False)
        print(f"Extracted {len(df)} rows.")
        print(df['buggy'].value_counts())
    else:
        print("No data extracted.")

if __name__ == "__main__":
    main()
