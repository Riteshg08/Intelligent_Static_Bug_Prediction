# Architecture

The system pipeline is designed to be language-independent at its core, relying on small plugins for language-specific functionality.

## Pipeline
1. Source Code -> Language Detection
2. Parsing (AST via language plugin)
3. Feature Extraction
4. Static Analysis
5. ML Model
6. Bug Probability
7. Risk Classification + Explanation
8. Developer Report
