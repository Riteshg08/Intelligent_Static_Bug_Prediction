# Intelligent Static Bug Prediction

A language-agnostic system that reads source code in many programming languages without executing it, extracts static metrics per function, uses a trained ML model to predict the probability that each function is bug-prone, classifies risk, explains why, and shows results in a web dashboard.

## Overview
This system uses a language plugin architecture. The core pipeline is language-independent. Each language is a small plugin providing Tree-sitter grammars and metric settings.

## Getting Started
See the [User Guide](docs/user-guide.md).
