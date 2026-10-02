import pandas as pd
import os

def main():
    if not os.path.exists('dataset/output/dataset.csv'):
        print("Dataset not found!")
        return
        
    df = pd.read_csv('dataset/output/dataset.csv')
    
    print("Class balance per language:")
    print(df.groupby(['language', 'label']).size().unstack(fill_value=0))
    
    # Leakage check: Same function (by name and file and repo) in multiple splits
    # Actually, we should check by content hash or at least name/file.
    # For MVP, let's use repo + file + function as identifier
    df['id'] = df['repo'] + "::" + df['file'] + "::" + df['function']
    
    # See if any ID has multiple splits
    splits_per_id = df.groupby('id')['split'].nunique()
    leaked_ids = splits_per_id[splits_per_id > 1]
    
    if len(leaked_ids) > 0:
        print(f"\nWARNING: Found {len(leaked_ids)} leaked functions across splits!")
        print("Example leaks:")
        print(df[df['id'].isin(leaked_ids.head().index)][['id', 'split', 'label']])
    else:
        print("\nLeakage check passed! No functions cross split boundaries.")

if __name__ == "__main__":
    main()
