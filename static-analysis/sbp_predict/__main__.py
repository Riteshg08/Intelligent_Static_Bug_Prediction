import argparse
from sbp_predict.engine import PredictionEngine
from sbp_analysis.cli import analyze_directory
from sbp_analysis.parser import parse_file
from sbp_analysis.features import extract_features
import os

def main():
    parser = argparse.ArgumentParser(description="Predict bug probability")
    parser.add_argument("path", help="Path to file or directory")
    args = parser.parse_args()
    
    engine = PredictionEngine()
    
    if os.path.isdir(args.path):
        df = analyze_directory(args.path)
        features = df.to_dict('records')
    else:
        funcs = parse_file(args.path)
        with open(args.path, 'rb') as f:
            content = f.read()
            
        features = []
        for func in funcs:
            f = extract_features(func, content, 0)
            f['file_path'] = args.path
            f['function_name'] = func.function_name
            features.append(f)
            
    if not features:
        print("No functions found.")
        return
        
    results = engine.predict(features)
    
    # Sort by risk descending
    results.sort(key=lambda x: x.get('risk_score', 0), reverse=True)
    
    for r in results:
        print(f"File: {r['file_path']}  Language: {r['language']}  Risk Score: {int(r['risk_score']*100)}%  Risk Level: {r['risk_level']}")
        print(f"Potentially bug-prone function: {r['function_name']}")
        print(f"Main reasons: {', '.join(r['explanation'])}")
        print(f"Note: {r['confidence_note']}")
        print("-" * 50)

if __name__ == "__main__":
    main()
