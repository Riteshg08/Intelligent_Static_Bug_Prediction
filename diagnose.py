import os
import sys

sys.path.insert(0, os.path.abspath('static-analysis'))
sys.path.insert(0, os.path.abspath('ml'))

from sbp_analysis.cli import analyze_directory
from sbp_predict.engine import PredictionEngine

df, hotspots = analyze_directory('storage/projects/1')

engine = PredictionEngine(models_dir="models")

print(f"Total functions analyzed: {len(df)}")
for feat in df.to_dict('records'):
    # Run prediction
    res = engine.predict([feat])
    if res:
        p = res[0]
        print("-" * 40)
        print(f"Function: {feat['function_name']} in {feat['file_path']}")
        print(f"Language: {feat['language']}")
        print(f"LOC: {feat['loc']}, Complexity: {feat.get('cyclomatic_complexity')}, Nesting: {feat['max_nesting_depth']}, Params: {feat['num_parameters']}, Branches: {feat['num_branches']}")
        print(f"Explanation: {p.get('explanation')}")
        print(f"Risk Score (raw probability): {p['risk_score']:.4f}")
        print(f"Risk Level: {p['risk_level']}")
