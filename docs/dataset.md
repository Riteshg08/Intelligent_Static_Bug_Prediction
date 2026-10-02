# Dataset Collection

The dataset collection pipeline identifies functions that have been fixed in the past (buggy) and those that haven't (clean).

## SZZ Approach
1. It looks for bug-fixing commits by matching keywords like "fix", "bug", "issue".
2. It takes the deleted lines from the fix and runs `git blame` to find the buggy commit that introduced them.
3. The function covering those lines in the buggy commit is extracted and labeled `1` (buggy).
4. Functions not touched by fixes are sampled as `0` (clean).
5. All are processed by the feature extractor.
6. The dataset is deduplicated and split by repo AND time (oldest 80% train, newest 20% test).

## Structure
- `dataset.csv`: Main dataset with labels and features.
- `repos.yaml`: Configured list of repos.
