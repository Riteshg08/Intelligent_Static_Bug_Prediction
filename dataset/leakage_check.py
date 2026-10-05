import pandas as pd
import re
import os

def normalize_tokens(code):
    if not isinstance(code, str):
        return set()
    tokens = re.findall(r'\w+', code.lower())
    return set(tokens)

def jaccard_sim(set1, set2):
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)

def main():
    if not os.path.exists('dataset/output/dataset_split.csv'):
        print("Dataset not found!")
        return
        
    df = pd.read_csv('dataset/output/dataset_split.csv')
    
    print("Class balance per language and split:")
    print(df.groupby(['language', 'split', 'buggy']).size().unstack(fill_value=0))
    
    # 1. Content Hash Overlap
    if 'content_hash' in df.columns:
        train_hashes = set(df[df['split'] == 'train']['content_hash'])
        test_hashes = set(df[df['split'] == 'test']['content_hash'])
        overlap = train_hashes & test_hashes
        if overlap:
            print(f"FAILED: Found {len(overlap)} exact content hashes in both train and test!")
            exit(1)
        else:
            print("Passed exact hash leakage check.")
            
    # 2. Near-duplicate overlap
    if 'function_code' in df.columns:
        df['tokens'] = df['function_code'].apply(normalize_tokens)
        
        leak_count = 0
        for lang, group in df.groupby('language'):
            train_tokens = group[group['split'] == 'train']['tokens'].tolist()
            test_tokens = group[group['split'] == 'test']['tokens'].tolist()
            
            # Simple check: test against train. 
            for tt in test_tokens:
                for tr in train_tokens:
                    if jaccard_sim(tt, tr) > 0.8:
                        leak_count += 1
                        break # count once per test sample
                        
        if leak_count > 0:
            print(f"FAILED: Found {leak_count} near-duplicates leaking across train/test splits!")
            exit(1)
        else:
            print("Passed near-duplicate leakage check.")
            
    # 3. Repo overlap
    train_repos = set(df[df['split'] == 'train']['repo'])
    test_repos = set(df[df['split'] == 'test']['repo'])
    val_repos = set(df[df['split'] == 'val']['repo']) if 'val' in df['split'].values else set()
    
    overlap_repos_test = train_repos & test_repos
    overlap_repos_val = train_repos & val_repos
    overlap_repos_val_test = val_repos & test_repos
    
    if overlap_repos_test or overlap_repos_val or overlap_repos_val_test:
        print(f"FAILED: Repos overlapping between splits!")
        exit(1)
    else:
        print("Passed repository isolation check.")
        
    print("\nALL LEAKAGE CHECKS PASSED.")

if __name__ == "__main__":
    main()
