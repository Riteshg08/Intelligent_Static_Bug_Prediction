# Model Ranking Diagnosis Report

## 1. Feature Order/Names Mismatch & Missing Features
- **Findings:** Feature extraction correctly extracts all features specified in `metadata.json`. The order in the `PredictionEngine`'s `pd.DataFrame([features_dict], columns=self.metadata["features"])` ensures order matches the training exactly. Missing features are consistently filled with `0` via `.fillna(0)` in both training (`train.py`) and prediction (`engine.py`).
- **Conclusion:** No feature mismatch or missing/NaN propagation bug was found.

## 2. Feature Normalization & Prediction Discrepancy
- **Findings:** `train.py` applied `StandardScaler` to train the Logistic Regression baseline, but passed unscaled `X_train` to LightGBM. The `PredictionEngine` also correctly uses unscaled data for LightGBM predictions. 
- **Conclusion:** No scaling mismatch.

## 3. Tree-sitter Plugin Extraction Bugs (JS, TS, Go, Java)
- **Findings:** By hand-counting `test_project.zip/orderProcessor.js`, we found that the nesting depth for `processOrder` was incorrectly calculated as `16` (actual is `7`). This was due to double-counting in JS/TS/Java/Go plugins: the `nesting_nodes` list incorrectly included `statement_block` (or `block` in Java/Go) alongside statements like `if_statement` and `for_statement`. Since an `if` statement typically contains a block child, every nested block was counting twice. Additionally, the JS/TS function queries failed to capture functions declared via assignment expressions (e.g., `exports.method = function()`), leading to missing function data.
- **Fixes Applied:** 
  - Removed `statement_block` (JS/TS) and `block` (Java/Go) from the `nesting_nodes` lists.
  - Added `assignment_expression` matchers to `javascript.py` and `typescript.py` tree-sitter queries.

## 4. Dataset Size, Class Balance, & Label Quality
- **Findings:** The initial dataset (`dataset.csv`) contained only 253 functions in total (Python: 150 safe / 15 bug; JavaScript: 79 safe / 9 bug), which is a very small pilot size. More critically, the SZZ implementation in `collect_dataset.py` was checking out the buggy commit `bc_hash` but checking against `deleted_lines` line numbers that belong to the `parent_commit`. It also previously fell back to labeling *every single function* in a buggy file as a bug, producing heavily noisy labels (a file with 50 clean functions and 1 buggy function produced 51 positive labels). This severely confused the model and caused predictions to flatline into the 0.4-0.6 range. 
- **Fixes Applied:** 
  - Refactored `collect_dataset.py` to extract functions directly from the `parent_commit`.
  - Enforced strict bounds checking so a function is only labeled as buggy if it explicitly contains the deleted line (`func.start_line <= line <= func.end_line`).
  - Increased `max_commits` limit to 500 and `commits_analyzed` to 2000 to gather a reasonably sized dataset.

## 5. Model Probabilities & Thresholds
- **Findings:** Because of the extremely noisy labels in the pilot dataset and small dataset size, LightGBM underfitted aggressively to avoid false positives. This led to a near-constant output probability (clustered around 0.4 to 0.6). Thus, tiny simple functions were sometimes arbitrarily scored higher than heavily nested ones.
- **Fixes Applied:** With the fixed AST nesting metric and strictly bounded buggy labels, the retrained model cleanly separates complex functions from simple ones without needing hard-coded rules. Small languages lacking data fall back to the global model, which is flagged appropriately with an experimental tag in the API.

## Conclusion
The model has been retrained on the cleaner, larger dataset. Running against `test_project.zip` confirms that large, deeply nested, and highly complex functions correctly out-rank tiny, simple functions.
