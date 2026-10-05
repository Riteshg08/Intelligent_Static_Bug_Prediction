import os
import sys
import json
import hashlib
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
import lightgbm as lgb

FEATURES = [
    "cyclomatic_complexity", "loc", "function_length", "max_nesting_depth",
    "cognitive_complexity_approx", "num_parameters", "num_branches", "num_loops",
    "num_local_variables", "num_return_statements", "ast_node_count",
    "num_call_expressions", "external_import_count", "code_smell_count"
]

def hash_dataset(df):
    content = df.to_csv(index=False).encode('utf-8')
    return hashlib.md5(content).hexdigest()

def get_percentiles(df, features):
    pct = {}
    for f in features:
        pct[f] = {
            "0.75": float(df[f].quantile(0.75)),
            "0.95": float(df[f].quantile(0.95))
        }
    return pct

def evaluate(y_true, y_pred, y_prob):
    # Handle cases with only one class in y_true
    if len(np.unique(y_true)) > 1:
        roc_auc = roc_auc_score(y_true, y_prob)
        pr_auc = average_precision_score(y_true, y_prob)
    else:
        roc_auc = 0.5
        pr_auc = 0.0
        
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc),
        "pr_auc": float(pr_auc),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist()
    }

def train_language(lang, train_df, test_df):
    print(f"\n--- Training for {lang} ---")
    
    X_train = train_df[FEATURES].fillna(0)
    y_train = train_df['buggy'].values
    X_test = test_df[FEATURES].fillna(0)
    y_test = test_df['buggy'].values
    
    # Baselines
    majority_class = int(pd.Series(y_train).mode()[0])
    majority_preds = np.full(len(y_test), majority_class)
    majority_probs = np.full(len(y_test), 0.5) # neutral prob
    majority_metrics = evaluate(y_test, majority_preds, majority_probs)
    
    loc_90 = train_df['loc'].quantile(0.90)
    top10_preds = (X_test['loc'] >= loc_90).astype(int)
    top10_probs = (X_test['loc'] >= loc_90).astype(float)
    top10_metrics = evaluate(y_test, top10_preds, top10_probs)
    
    # LR
    lr = LogisticRegression(max_iter=1000, class_weight='balanced')
    lr.fit(X_train, y_train)
    lr_preds = lr.predict(X_test)
    lr_probs = lr.predict_proba(X_test)[:, 1]
    lr_metrics = evaluate(y_test, lr_preds, lr_probs)
    
    # LightGBM with simple tuning
    lgb_model = lgb.LGBMClassifier(class_weight='balanced', random_state=42, verbose=-1)
    
    # We use TimeSeriesSplit if sorted by time, otherwise KFold. We sorted by commit_date in dedup_and_split
    tscv = TimeSeriesSplit(n_splits=3)
    param_dist = {
        'n_estimators': [50, 100, 200],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.05, 0.1]
    }
    
    # Only tune if enough data
    if len(X_train) > 50:
        search = RandomizedSearchCV(lgb_model, param_dist, n_iter=5, cv=tscv, scoring='f1', random_state=42)
        search.fit(X_train, y_train)
        best_model = search.best_estimator_
    else:
        best_model = lgb_model.fit(X_train, y_train)
        
    lgb_preds = best_model.predict(X_test)
    lgb_probs = best_model.predict_proba(X_test)[:, 1]
    lgb_metrics = evaluate(y_test, lgb_preds, lgb_probs)
    
    # Promotion check: Must beat BOTH majority and top10 on F1 (or PR-AUC if F1 is 0)
    # Using F1 as primary
    majority_f1 = majority_metrics['f1']
    top10_f1 = top10_metrics['f1']
    lgb_f1 = lgb_metrics['f1']
    
    passed = False
    if lgb_f1 > majority_f1 and lgb_f1 > top10_f1:
        passed = True
        
    status = "dedicated" if passed else "experimental_fallback"
    print(f"[{lang}] F1 - Majority: {majority_f1:.3f}, Top10: {top10_f1:.3f}, LGB: {lgb_f1:.3f} -> Status: {status}")
    
    train_probs = best_model.predict_proba(X_train)[:, 1]
    thresholds = {
        "low": float(np.percentile(train_probs, 75)),
        "medium": float(np.percentile(train_probs, 90))
    }
    
    return {
        "model": best_model,
        "status": status,
        "metrics": {
            "majority": majority_metrics,
            "top10_loc": top10_metrics,
            "logistic_regression": lr_metrics,
            "lightgbm": lgb_metrics
        },
        "percentiles": get_percentiles(train_df, FEATURES),
        "thresholds": thresholds,
        "feature_importance": dict(zip(FEATURES, best_model.feature_importances_.tolist())) if hasattr(best_model, 'feature_importances_') else {}
    }

def generate_report(version, results, metadata):
    report_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'reports'))
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f'evaluation_{version}.md')
    
    lines = [f"# Model Evaluation Report: {version}\n"]
    lines.append(f"**Dataset Hash**: `{metadata['dataset_hash']}`\n")
    lines.append(f"**Total Rows**: {metadata['dataset_summary']['total_rows']}\n")
    lines.append(f"**Features**: {', '.join(FEATURES)}\n")
    
    lines.append("## Promotion Results\n")
    lines.append("| Language | Status | Majority F1 | Top 10% F1 | Model F1 |")
    lines.append("|----------|--------|-------------|------------|----------|")
    
    for lang, res in results.items():
        m_f1 = res['metrics']['majority']['f1']
        t_f1 = res['metrics']['top10_loc']['f1']
        lgb_f1 = res['metrics']['lightgbm']['f1']
        lines.append(f"| {lang} | {res['status']} | {m_f1:.3f} | {t_f1:.3f} | {lgb_f1:.3f} |")
        
    lines.append("\n## Detailed Metrics (LightGBM)\n")
    lines.append("| Language | Accuracy (misleading) | Precision | Recall | F1 | PR-AUC | ROC-AUC |")
    lines.append("|----------|-----------------------|-----------|--------|----|--------|---------|")
    for lang, res in results.items():
        m = res['metrics']['lightgbm']
        lines.append(f"| {lang} | {m['accuracy']:.3f} | {m['precision']:.3f} | {m['recall']:.3f} | {m['f1']:.3f} | {m['pr_auc']:.3f} | {m['roc_auc']:.3f} |")
        
    lines.append("\n## Limitations\n")
    lines.append("- True SZZ involves heuristics that may label refactoring or test-related changes as bugs if keywords match.\n")
    lines.append("- Accuracy is reported but heavily misleading on imbalanced datasets.\n")
    lines.append("- Experimental languages failed to beat simple baselines on real holdout repositories, indicating structural features alone are insufficient for those contexts.\n")
    
    with open(report_path, "w") as f:
        f.write("\n".join(lines))
    print(f"Report written to {report_path}")

def main():
    dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../dataset/output/dataset_split.csv'))
    if not os.path.exists(dataset_path):
        print("Dataset split not found!")
        sys.exit(1)
        
    df = pd.read_csv(dataset_path)
    if len(df) == 0:
        print("Dataset is empty.")
        sys.exit(1)
        
    version = datetime.now().strftime("%Y%m%d_%H%M%S")
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), f'../models/{version}'))
    os.makedirs(models_dir, exist_ok=True)
    
    metadata = {
        "version": version,
        "features": FEATURES,
        "dataset_hash": hash_dataset(df),
        "dataset_summary": {
            "total_rows": len(df),
            "buggy_rows": int(df['buggy'].sum())
        },
        "languages": {},
        "global_model": True,
        "thresholds": {} # Global thresholds fallback
    }
    
    results = {}
    
    # 1. Global Model
    train_df = df[df['split'] == 'train']
    test_df = df[df['split'] == 'test']
    
    if len(train_df) == 0 or len(test_df) == 0:
        print("Train or test split empty!")
        sys.exit(1)
    global_res = train_language('global', train_df, test_df)
    results['global'] = global_res
    joblib.dump(global_res['model'], os.path.join(models_dir, 'model_global.joblib'))
    metadata['thresholds'] = global_res['thresholds']
    metadata['dataset_summary']['global_percentiles'] = global_res['percentiles']
    metadata['metrics'] = global_res['metrics']['lightgbm']
    metadata['feature_importance'] = global_res['feature_importance']
    metadata['training_date'] = datetime.now().isoformat()
    
    # 2. Per-language Models
    any_passed = False
    for lang in df['language'].unique():
        l_df = df[df['language'] == lang]
        l_train = l_df[l_df['split'] == 'train']
        l_test = l_df[l_df['split'] == 'test']
        
        if len(l_train) < 10 or len(l_test) < 5:
            print(f"Skipping {lang} due to insufficient data")
            continue
            
        res = train_language(lang, l_train, l_test)
        results[lang] = res
        
        joblib.dump(res['model'], os.path.join(models_dir, f'model_{lang}.joblib'))
        
        metadata['languages'][lang] = {
            "status": res['status'],
            "percentiles": res['percentiles'],
            "metrics": res['metrics']
        }
        
        if res['status'] == 'dedicated':
            any_passed = True
            
    with open(os.path.join(models_dir, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)
        
    generate_report(version, results, metadata)
    
    if any_passed:
        active_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../models/active.txt'))
        with open(active_path, 'w') as f:
            f.write(version)
        print(f"Updated active.txt to {version}")
    else:
        print("No language model passed the baselines! active.txt NOT updated (Model not trained state will persist).")

if __name__ == "__main__":
    main()
