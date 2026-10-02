import pandas as pd
import numpy as np
import os
import json
import joblib
from datetime import datetime
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from lightgbm import LGBMClassifier

def evaluate(y_true, y_pred, y_prob):
    try:
        roc_auc = roc_auc_score(y_true, y_prob)
        pr_auc = average_precision_score(y_true, y_prob)
    except:
        roc_auc = 0.5
        pr_auc = 0.0
    return {
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1': f1_score(y_true, y_pred, zero_division=0),
        'roc_auc': roc_auc,
        'pr_auc': pr_auc,
        'confusion_matrix': confusion_matrix(y_true, y_pred).tolist() if len(set(y_true)) > 1 else []
    }

def train_and_evaluate(df_train, df_test, features, label_col='label'):
    X_train = df_train[features].fillna(0)
    y_train = df_train[label_col]
    X_test = df_test[features].fillna(0)
    y_test = df_test[label_col]
    
    # Needs at least 2 classes in train and test for meaningful evaluation
    if len(y_train.unique()) < 2 or len(y_test.unique()) < 2:
        return None, None, None
        
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Baselines
    majority_class = y_train.mode()[0]
    baseline_pred = [majority_class] * len(y_test)
    baseline_prob = [1.0 if majority_class == 1 else 0.0] * len(y_test)
    metrics_majority = evaluate(y_test, baseline_pred, baseline_prob)
    
    # Logistic Regression
    lr = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
    lr.fit(X_train_scaled, y_train)
    lr_pred = lr.predict(X_test_scaled)
    lr_prob = lr.predict_proba(X_test_scaled)[:, 1]
    metrics_lr = evaluate(y_test, lr_pred, lr_prob)
    
    # LightGBM
    lgbm = LGBMClassifier(class_weight='balanced', random_state=42, n_estimators=100)
    lgbm.fit(X_train, y_train)
    lgbm_pred = lgbm.predict(X_test)
    lgbm_prob = lgbm.predict_proba(X_test)[:, 1]
    metrics_lgbm = evaluate(y_test, lgbm_pred, lgbm_prob)
    
    # Feature importances
    importances = dict(zip(features, lgbm.feature_importances_))
    
    results = {
        'majority': metrics_majority,
        'logistic_regression': metrics_lr,
        'lightgbm': metrics_lgbm,
        'importances': importances
    }
    
    return lgbm, results, scaler

def main():
    if not os.path.exists('dataset/output/dataset.csv'):
        print("Dataset not found!")
        return
        
    df = pd.read_csv('dataset/output/dataset.csv')
    df_train = df[df['split'] == 'train'].copy()
    df_test = df[df['split'] == 'test'].copy()
    
    features = [
        "cyclomatic_complexity", "loc", "function_length", "max_nesting_depth", 
        "cognitive_complexity_approx", "num_parameters", "num_branches", 
        "num_loops", "num_local_variables", "num_return_statements", 
        "ast_node_count", "num_call_expressions", "external_import_count", 
        "code_smell_count", "duplicate_code_ratio"
    ]
    
    os.makedirs('models', exist_ok=True)
    os.makedirs('ml/reports', exist_ok=True)
    version = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_dir = f"models/{version}"
    os.makedirs(model_dir, exist_ok=True)
    
    report_content = f"# Model Evaluation Report ({version})\n\n"
    
    # Strategy A: Global Model
    print("Training Global Model...")
    global_model, global_results, _ = train_and_evaluate(df_train, df_test, features)
    
    metadata = {
        "version": version,
        "date": version,
        "features": features,
        "languages": {},
        "global_model": True,
        "thresholds": {"low": 0.35, "medium": 0.65}
    }
    
    if global_results:
        joblib.dump(global_model, f"{model_dir}/model_global.joblib")
        metadata['global_metrics'] = global_results['lightgbm']
        report_content += "## Global Model\n"
        report_content += f"- **F1:** {global_results['lightgbm']['f1']:.3f}\n"
        report_content += f"- **PR-AUC:** {global_results['lightgbm']['pr_auc']:.3f}\n\n"
    
    # Strategy B: Per-Language Models
    for lang in df['language'].unique():
        print(f"Training Model for {lang}...")
        df_lang_train = df_train[df_train['language'] == lang]
        df_lang_test = df_test[df_test['language'] == lang]
        
        lang_model, lang_results, _ = train_and_evaluate(df_lang_train, df_lang_test, features)
        
        if lang_results:
            joblib.dump(lang_model, f"{model_dir}/model_{lang}.joblib")
            
            # Percentiles for explanation
            percentiles = {}
            for feat in features:
                percentiles[feat] = df_lang_train[feat].describe(percentiles=[.25, .5, .75, .90, .95]).to_dict()
                
            metadata['languages'][lang] = {
                "status": "dedicated",
                "metrics": lang_results['lightgbm'],
                "percentiles": percentiles
            }
            report_content += f"## {lang} Model\n"
            report_content += f"- **F1:** {lang_results['lightgbm']['f1']:.3f}\n"
            report_content += f"- **PR-AUC:** {lang_results['lightgbm']['pr_auc']:.3f}\n\n"
        else:
            metadata['languages'][lang] = {
                "status": "experimental_fallback"
            }
            report_content += f"## {lang} Model\n"
            report_content += "Not enough data (using global fallback).\n\n"
            
    with open(f"{model_dir}/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
        
    # Active pointer
    with open("models/active.txt", "w") as f:
        f.write(version)
        
    with open(f"ml/reports/evaluation_{version}.md", "w") as f:
        f.write(report_content)
        
    print(f"Models saved to {model_dir}")

if __name__ == "__main__":
    main()
