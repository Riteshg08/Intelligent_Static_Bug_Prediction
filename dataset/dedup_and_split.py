import pandas as pd
import re
import os

def normalize_tokens(code):
    if not isinstance(code, str):
        return set()
    # Simple tokenization: lowercase, alphanumeric words
    tokens = re.findall(r'\w+', code.lower())
    return set(tokens)

def jaccard_sim(set1, set2):
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)

def main():
    if not os.path.exists('dataset/output/dataset.csv'):
        print("Dataset not found!")
        return
        
    df = pd.read_csv('dataset/output/dataset.csv')
    print(f"Original size: {len(df)}")
    
    # 1. Exact deduplication
    if 'content_hash' in df.columns:
        df = df.drop_duplicates(subset=['language', 'content_hash'], keep='first')
    print(f"After exact dedup: {len(df)}")
    
    # 2. Near-duplicate deduplication (Optional/Heuristic to save time)
    # This is O(N^2) if done naively. We can sort by function length and only compare similar sizes.
    # To keep it fast enough for thousands of rows, we'll do a simple window approach or just 
    # exact dedup + leakage check for near-duplicates across splits (which is what prompt asks).
    # Wait, prompt says: "Deduplicate exact and near-duplicate functions (content hash plus normalized token similarity) across the whole dataset."
    
    if 'function_code' in df.columns:
        df['tokens'] = df['function_code'].apply(normalize_tokens)
        
        to_drop = set()
        # Group by language to limit search space
        for lang, group in df.groupby('language'):
            # Sort by loc to compare only similar sized functions
            group = group.sort_values('loc')
            idx = group.index.tolist()
            
            for i in range(len(idx)):
                if idx[i] in to_drop: continue
                # compare with next window
                tokens_i = group.loc[idx[i], 'tokens']
                for j in range(i+1, min(i+100, len(idx))):
                    if idx[j] in to_drop: continue
                    tokens_j = group.loc[idx[j], 'tokens']
                    if jaccard_sim(tokens_i, tokens_j) > 0.8:
                        to_drop.add(idx[j])
                        
        df = df.drop(index=list(to_drop))
        df = df.drop(columns=['tokens'])
        print(f"After near-dedup: {len(df)}")

    # 3. Split by repo AND time
    # Time-based splitting per language: sort by commit_date. 
    # Hold out whole repos: Assign newer repos to test?
    # Better: for each language, select 1-2 repos entirely as test set.
    # Or just sort all rows by commit_date, take newest 20%, but make sure no repos overlap.
    
    splits = []
    for lang, group in df.groupby('language'):
        group = group.sort_values('commit_date')
        repos = group['repo'].unique()
        
        # Simple strategy: last 20% of repos by their latest commit go to test, next 10% to val
        repo_latest = group.groupby('repo')['commit_date'].max().sort_values()
        num_repos = len(repos)
        test_count = max(1, int(num_repos * 0.2))
        val_count = max(1, int(num_repos * 0.1)) if num_repos > 2 else 0
        
        test_repos = repo_latest.tail(test_count).index.tolist()
        val_repos = repo_latest.iloc[-(test_count+val_count):-test_count].index.tolist() if val_count > 0 else []
        
        group['split'] = 'train'
        group.loc[group['repo'].isin(test_repos), 'split'] = 'test'
        if val_repos:
            group.loc[group['repo'].isin(val_repos), 'split'] = 'val'
        
        splits.append(group)
        
    if splits:
        df = pd.concat(splits)
    
    df.to_csv('dataset/output/dataset_split.csv', index=False)
    print("Saved to dataset_split.csv")
    
    # 4. Spot check 50 samples per language
    if 'function_code' in df.columns:
        docs_dir = 'docs'
        if not os.path.exists(docs_dir):
            os.makedirs(docs_dir)
            
        for lang, group in df.groupby('language'):
            sample_size = min(50, len(group))
            sample = group.sample(n=sample_size, random_state=42)
            
            with open(os.path.join(docs_dir, f'label_samples_{lang.lower()}.md'), 'w', encoding='utf-8') as f:
                f.write(f"# {lang} Label Samples\n\n")
                f.write("Reviewing label noise: True SZZ can erroneously label refactoring or style changes as bugs if keywords match.\n\n")
                for _, row in sample.iterrows():
                    f.write(f"### Buggy: {row['buggy']} (Commit: {row['commit_hash']})\n")
                    f.write(f"**Repo**: {row['repo']}\n")
                    f.write("```" + lang.lower() + "\n")
                    f.write(str(row['function_code']))
                    f.write("\n```\n\n")
        print("Generated label_samples in docs/")

if __name__ == "__main__":
    main()
