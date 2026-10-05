import json
import os
import joblib
import pandas as pd
from typing import Dict, Any, List

class Explainer:
    def explain(self, features: Dict[str, Any], importances: Dict[str, float], percentiles: Dict[str, Dict[str, float]], lang: str) -> List[str]:
        raise NotImplementedError

class MVPExplainer(Explainer):
    def explain(self, features: Dict[str, Any], importances: Dict[str, float], percentiles: Dict[str, Dict[str, float]], lang: str) -> List[str]:
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
            name = feat.replace('_', ' ').capitalize()
            if val >= p.get('0.95', float('inf')):
                reasons.append(f"{name} {val}, higher than 95% of {lang} functions")
            elif val >= p.get('0.75', float('inf')):
                reasons.append(f"{name} {val}, higher than 75% of {lang} functions")
                
        if not reasons:
            reasons.append("No specific structural factors stand out statistically.")
            
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
            raise RuntimeError(f"Model not trained (no active.txt in {self.models_dir})")
            
        with open(active_file, "r") as f:
            self.active_version = f.read().strip()
            
        version_dir = os.path.join(self.models_dir, self.active_version)
        meta_path = os.path.join(version_dir, "metadata.json")
        if not os.path.exists(meta_path):
            raise RuntimeError(f"Model not trained (missing metadata.json in {version_dir})")
            
        with open(meta_path, "r") as f:
            self.metadata = json.load(f)
            
        if self.metadata.get("global_model"):
            gm_path = os.path.join(version_dir, "model_global.joblib")
            if not os.path.exists(gm_path):
                raise RuntimeError("Model not trained (missing model_global.joblib)")
            self.models["global"] = joblib.load(gm_path)
            
        for lang in self.metadata.get("languages", {}):
            lang_info = self.metadata["languages"][lang]
            if lang_info.get("status") == "dedicated":
                lm_path = os.path.join(version_dir, f"model_{lang}.joblib")
                if not os.path.exists(lm_path):
                    raise RuntimeError(f"Model not trained (missing dedicated model for {lang})")
                self.models[lang] = joblib.load(lm_path)
                
    def predict(self, extracted_features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not extracted_features:
            return []
            
        lang = extracted_features[0].get("language", "Unknown")
        
        # Batch all features for the file
        feature_dicts = []
        for func in extracted_features:
            features_dict = {k: v for k, v in func.items() if k in self.metadata["features"]}
            feature_dicts.append(features_dict)
            
        df = pd.DataFrame(feature_dicts, columns=self.metadata["features"]).fillna(0)
        
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
            return [{"error": "No model available"} for _ in extracted_features]
            
        probs = model.predict_proba(df)[:, 1]
        
        thresholds = self.metadata.get("thresholds", {"low": 0.35, "medium": 0.65})
        importances = {}
        if hasattr(model, "feature_importances_"):
            importances = dict(zip(self.metadata["features"], model.feature_importances_))
            
        percentiles = lang_metadata.get("percentiles", {})
        
        results = []
        for i, func in enumerate(extracted_features):
            prob = probs[i]
            risk_level = "Low"
            if prob >= thresholds["medium"]:
                risk_level = "High"
            elif prob >= thresholds["low"]:
                risk_level = "Medium"
                
            reasons = self.explainer.explain(feature_dicts[i], importances, percentiles, lang)
            
            results.append({
                "function_name": func.get("function_name"),
                "file_path": func.get("file_path"),
                "start_line": func.get("start_line"),
                "end_line": func.get("end_line"),
                "language": lang,
                "risk_score": float(prob),
                "risk_level": risk_level,
                "model_version": self.active_version,
                "confidence_note": confidence_note,
                "explanation": reasons
            })
            
        return results
