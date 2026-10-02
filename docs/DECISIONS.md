# Architectural Decisions

## Pipeline Architecture
1. Source Code
2. Language Detection
3. Parsing (AST via language plugin)
4. Feature Extraction
5. Static Analysis
6. ML Model
7. Bug Probability
8. Risk Classification + Explanation
9. Developer Report

## Other Decisions
- Using language plugins to make the core system language-independent.
- Features are extracted based on node types provided by the language plugins.
