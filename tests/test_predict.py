import pytest
import os
import joblib
import json
import pandas as pd
from sbp_predict.engine import PredictionEngine
import tempfile
import shutil

class MockModel:
    def __init__(self, is_risky):
        self.is_risky = is_risky
        self.feature_importances_ = [0.8, 0.2]
        
    def predict_proba(self, X):
        # Return high prob if loc > 30 else low prob
        probs = []
        for _, row in X.iterrows():
            if row['loc'] > 30:
                probs.append([0.1, 0.9])
            else:
                probs.append([0.9, 0.1])
        return probs

@pytest.fixture
def mock_models_dir():
    # Setup mock models
    tmp_dir = tempfile.mkdtemp()
    
    version = "test_v1"
    os.makedirs(os.path.join(tmp_dir, version))
    
    with open(os.path.join(tmp_dir, "active.txt"), "w") as f:
        f.write(version)
        
    features = ["loc", "num_parameters"]
    metadata = {
        "version": version,
        "features": features,
        "global_model": True,
        "languages": {
            "Python": {
                "status": "dedicated",
                "percentiles": {
                    "loc": {"0.75": 10, "0.95": 50},
                    "num_parameters": {"0.75": 2, "0.95": 5}
                }
            },
            "Ruby": {
                "status": "experimental_fallback"
            }
        },
        "thresholds": {"low": 0.35, "medium": 0.65}
    }
    
    with open(os.path.join(tmp_dir, version, "metadata.json"), "w") as f:
        json.dump(metadata, f)
            
    joblib.dump(MockModel(True), os.path.join(tmp_dir, version, "model_global.joblib"))
    joblib.dump(MockModel(False), os.path.join(tmp_dir, version, "model_Python.joblib"))
    
    yield tmp_dir
    
    shutil.rmtree(tmp_dir)

def test_prediction_engine(mock_models_dir):
    engine = PredictionEngine(models_dir=mock_models_dir)
    
    features = [
        {"function_name": "risky_py", "file_path": "a.py", "language": "Python", "loc": 55, "num_parameters": 6},
        {"function_name": "simple_py", "file_path": "b.py", "language": "Python", "loc": 5, "num_parameters": 1},
        {"function_name": "unsupported", "file_path": "c.rb", "language": "Ruby", "loc": 40, "num_parameters": 1}
    ]
    
    results = engine.predict(features)
    
    # Check risky python
    assert results[0]['risk_level'] == 'High'
    assert results[0]['confidence_note'] == 'Dedicated model'
    assert 'higher than 95%' in results[0]['explanation'][0]
    
    # Check simple python
    assert results[1]['risk_level'] == 'Low'
    
    # Check fallback language
    assert results[2]['risk_level'] == 'High'
    assert 'fallback model' in results[2]['confidence_note'].lower()
