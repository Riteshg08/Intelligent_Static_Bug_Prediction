import os
import yaml
import re
import pandas as pd
from datetime import datetime
from pydriller import Repository, Git
from sbp_analysis.parser import parse_file
from sbp_analysis.features import extract_features
import tempfile
import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Very simple heuristics for MVP
BUG_KEYWORDS = ["fix", "bug", "issue", "resolve", "close"]

def is_bug_fix(commit_msg):
    msg = commit_msg.lower()
    return any(keyword in msg for keyword in BUG_KEYWORDS)

def collect_from_repo(repo_path: str, lang: str, repo_name: str, max_commits=20):
    git = Git(repo_path)
    
    # 1. Find bug-fix commits
    logger.info(f"Analyzing {repo_name} for bug fixes...")
    
    # We will just traverse the last 200 commits to be fast for the pilot
    buggy_functions = []
    clean_functions = []
    
    # For clean functions, we will just sample from HEAD
    logger.info("Sampling clean functions from HEAD")
    # To properly sample, we parse all files at HEAD, get features
    # Then we filter out ones that we know were buggy. For MVP we'll just sample them.
    # In a full run, we'd check if they were touched by a bug fix in the window.
    for root, _, files in os.walk(repo_path):
        if ".git" in root or "node_modules" in root: continue
        for file in files:
            file_path = os.path.join(root, file)
            # Only process files matching the language loosely (for MVP we trust the parser to skip unsupported)
            funcs = parse_file(file_path)
            if funcs:
                with open(file_path, 'rb') as f:
                    content = f.read()
                for func in funcs:
                    if func.language != lang: continue
                    feat = extract_features(func, content, 0)
                    feat['repo'] = repo_name
                    feat['language'] = func.language
                    feat['file'] = file_path.replace(repo_path, "")
                    feat['function'] = func.function_name
                    feat['commit'] = git.get_head().hash
                    feat['timestamp'] = git.get_head().committer_date.timestamp()
                    feat['label'] = 0
                    clean_functions.append(feat)
                    
    # Cap clean functions
    random.shuffle(clean_functions)
    clean_functions = clean_functions[:200]
    
    # Now SZZ for buggy functions
    commits_analyzed = 0
    bug_commits = 0
    
    # pydriller Repository iterates commits from oldest to newest by default
    # To be fast, let's just get the commits list and take the last N
    commits = list(Repository(repo_path).traverse_commits())
    commits.reverse()
    
    for commit in commits:
        if commits_analyzed >= 200 or bug_commits >= max_commits:
            break
        commits_analyzed += 1
        
        if is_bug_fix(commit.msg):
            bug_commits += 1
            for modified_file in commit.modified_files:
                if modified_file.change_type.name != 'MODIFY':
                    continue
                if not modified_file.filename.endswith(('.py', '.js', '.ts', '.java', '.c', '.cpp', '.cs', '.go')):
                    continue
                
                # find buggy commit (SZZ)
                deleted_lines = [line[0] for line in modified_file.diff_parsed['deleted']]
                if not deleted_lines:
                    continue
                    
                # get blame for the deleted lines using the commit before the fix
                if not commit.parents:
                    continue
                parent_commit = commit.parents[0]
                
                # We need to blame the deleted lines on the parent commit
                try:
                    blame = git.get_commits_last_modified_lines(parent_commit, modified_file.old_path, deleted_lines)
                except Exception as e:
                    logger.debug(f"Blame failed: {e}")
                    continue
                    
                buggy_commits = set(blame.values())
                
                # For each buggy commit, checkout and parse the function
                for bc_hash in buggy_commits:
                    try:
                        bc = git.get_commit(bc_hash)
                        # We don't checkout physically to avoid messing up the working tree
                        # Instead we just get the file content at that commit
                        source_code = bc.repo.git.show(f"{bc_hash}:{modified_file.old_path}")
                    except Exception:
                        continue
                        
                    # Write to temp file to parse
                    fd, tmp_path = tempfile.mkstemp(suffix="."+modified_file.filename.split('.')[-1])
                    with os.fdopen(fd, 'w', encoding='utf-8') as f:
                        f.write(source_code)
                        
                    funcs = parse_file(tmp_path)
                    
                    with open(tmp_path, 'rb') as f:
                        content_bytes = f.read()
                        
                    for func in funcs:
                        if func.language != lang: continue
                        # To be precise we should check if the deleted line falls in func bounds.
                        # For MVP, we'll assume the functions in this buggy file were bug-prone.
                        # We'll just take the first one or all
                        feat = extract_features(func, content_bytes, 0)
                        feat['repo'] = repo_name
                        feat['language'] = func.language
                        feat['file'] = modified_file.old_path
                        feat['function'] = func.function_name
                        feat['commit'] = bc_hash
                        feat['timestamp'] = bc.committer_date.timestamp()
                        feat['label'] = 1
                        buggy_functions.append(feat)
                        
                    os.remove(tmp_path)
                    
    logger.info(f"Collected {len(buggy_functions)} buggy functions and {len(clean_functions)} clean functions from {repo_name}")
    return buggy_functions + clean_functions

def main():
    with open('dataset/repos.yaml', 'r') as f:
        repos = yaml.safe_load(f)
        
    all_data = []
    
    for lang, repo_list in repos.items():
        for repo in repo_list:
            repo_name = repo['name']
            repo_path = os.path.join('dataset/clones', lang, repo_name)
            
            if os.path.exists(repo_path):
                data = collect_from_repo(repo_path, lang, repo_name)
                all_data.extend(data)
                
    df = pd.DataFrame(all_data)
    
    # Deduplicate (naive for MVP: by repo, file, function, label)
    # Actually, we should deduplicate by content_hash or similar.
    # But for MVP, drop duplicates
    df = df.drop_duplicates(subset=['repo', 'language', 'file', 'function', 'label'])
    
    # Splits by time and repo
    # 80/20 train/test based on timestamp per repo
    splits = []
    for (repo, lang), group in df.groupby(['repo', 'language']):
        group = group.sort_values('timestamp')
        split_idx = int(len(group) * 0.8)
        group['split'] = 'train'
        group.iloc[split_idx:, group.columns.get_loc('split')] = 'test'
        splits.append(group)
        
    if splits:
        df = pd.concat(splits)
    else:
        df['split'] = 'train'
        
    # Save
    os.makedirs('dataset/output', exist_ok=True)
    df.to_csv('dataset/output/dataset.csv', index=False)
    
    print("\n--- Collection Summary ---")
    print(df['language'].value_counts())
    print("\nLabel Distribution:")
    print(df.groupby('language')['label'].value_counts())
    
    # Export 50 sample
    sample = df.groupby('language').sample(min(50, len(df)), replace=True).drop_duplicates()
    sample.to_markdown('dataset/output/sample_50.md', index=False)

if __name__ == "__main__":
    main()
