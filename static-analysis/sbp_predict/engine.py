import json
import os
import joblib
import pandas as pd
from typing import Dict, Any, List

class Explainer:
    def explain(self, features: Dict[str, Any], importances: Dict[str, float], percentiles: Dict[str, Dict[str, float]]) -> List[str]:
        raise NotImplementedError

class MVPExplainer(Explainer):
    def explain(self, features: Dict[str, Any], importances: Dict[str, float], percentiles: Dict[str, Dict[str, float]]) -> List[str]:
        if not importances:
            return ["No feature importances available."]
            
        # Sort features by importance
        sorted_feats = sorted(importances.items(), key=lambda x: x[1], reverse=True)
        
        reasons = []
        for feat, imp in sorted_feats:
            if len(reasons) >= 3:
                break
                
            val = features.get(feat, 0)
            if feat not in percentiles:
                continue
                
            p = percentiles[feat]
            if val >= p.get('0.95', float('inf')):
                reasons.append(f"High {feat.replace('_', ' ')} ({val}, higher than 95% of norms)")
            elif val >= p.get('0.75', float('inf')):
                reasons.append(f"Above average {feat.replace('_', ' ')} ({val}, higher than 75% of norms)")
                
        if not reasons:
            reasons.append("Function is relatively standard, but combined factors indicate risk.")
            
        return reasons

class PredictionEngine:
    def __init__(self, models_dir="models"):
        self.models_dir = models_dir
        self.active_version = None
        self.metadata = None
        self.models = {}
        self.explainer = MVPExplainer()
        self._load_active()
        
    def _load_active(self):
        active_file = os.path.join(self.models_dir, "active.txt")
        if not os.path.exists(active_file):
            raise ValueError(f"No active model found in {self.models_dir}")
            
        with open(active_file, "r") as f:
            self.active_version = f.read().strip()
            
        version_dir = os.path.join(self.models_dir, self.active_version)
        with open(os.path.join(version_dir, "metadata.json"), "r") as f:
            self.metadata = json.load(f)
            
        if self.metadata.get("global_model"):
            self.models["global"] = joblib.load(os.path.join(version_dir, "model_global.joblib"))
            
        for lang in self.metadata.get("languages", {}):
            lang_info = self.metadata["languages"][lang]
            if lang_info.get("status") == "dedicated":
                self.models[lang] = joblib.load(os.path.join(version_dir, f"model_{lang}.joblib"))
                
    def predict(self, extracted_features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        
        for func in extracted_features:
            lang = func.get("language")
            features_dict = {k: v for k, v in func.items() if k in self.metadata["features"]}
            df = pd.DataFrame([features_dict], columns=self.metadata["features"]).fillna(0)
            
            model = None
            confidence_note = ""
            lang_metadata = self.metadata.get("languages", {}).get(lang, {})
            
            if lang_metadata.get("status") == "dedicated":
                model = self.models.get(lang)
                confidence_note = "Dedicated model"
            else:
                model = self.models.get("global")
                confidence_note = "Experimental language / fallback model"
                
            if not model:
                results.append({"error": "No model available"})
                continue
                
            # predict
            prob = model.predict_proba(df)[0][1]
            
            # thresholds
            thresholds = self.metadata.get("thresholds", {"low": 0.35, "medium": 0.65})
            risk_level = "Low"
            if prob >= thresholds["medium"]:
                risk_level = "High"
            elif prob >= thresholds["low"]:
                risk_level = "Medium"
                
            # explanation
            importances = {}
            if hasattr(model, "feature_importances_"):
                importances = dict(zip(self.metadata["features"], model.feature_importances_))
                
            percentiles = lang_metadata.get("percentiles", {})
            reasons = self.explainer.explain(features_dict, importances, percentiles)
            
            results.append({
                "function_name": func.get("function_name"),
                "file_path": func.get("file_path"),
                "language": lang,
                "risk_score": float(prob),
                "risk_level": risk_level,
                "model_version": self.active_version,
                "confidence_note": confidence_note,
                "explanation": reasons
            })
            
        return results
