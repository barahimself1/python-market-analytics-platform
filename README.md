# Python Market Analytics Research Platform

Interactive Python and Streamlit research platform for studying prediction market calibration, return behavior, and out of sample persistence.

## Overview

I built this project to answer a simple research question:

**Do prediction market prices and market conditions contain relationships that persist on later data, or do they only look strong in the same sample where they were discovered?**

The full research workflow covers **2,139 unique resolved Kalshi market tickers**. I used a chronological research sample of **1,497 markets** and a later test sample of **642 markets** so that results could be evaluated on unseen future observations rather than a randomly mixed split.

The public repository focuses on the research and visualization layer. It intentionally excludes private credentials, account data, and live execution logic.

## What the project does

* Loads and validates structured prediction market data
* Compares price implied probabilities with observed outcomes
* Measures calibration by probability bucket
* Examines return distributions
* Explores direction, entry price, ATR, normalized distance, and time to expiry
* Preserves chronological ordering for research and later test evaluation
* Provides an interactive Streamlit interface

## Dataset

Full research dataset:

* 2,139 unique resolved tickers
* 1,497 observations in the research period
* 642 observations in the later test period

This repository includes a small synthetic sample dataset so the public app can run without publishing the full research archive.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Tools

Python  
pandas  
NumPy  
Streamlit  
Plotly

## Validation philosophy

Random train test splits can create unrealistic evaluation when observations are time ordered. This project therefore uses chronological separation between the research period and the later test period.

A relationship is treated as more interesting when it remains directionally consistent on later data rather than only appearing inside the discovery sample.

## Public repository note

This repository is a portfolio version of a larger research system. It does not include API credentials, account identifiers, live order submission code, private execution logic, or proprietary strategy rules.

The included sample data is synthetic and is provided only so the interface can be reproduced.

## Author

Bara Mbaye  
Mechanical Engineering, University of Georgia  
Expected May 2028
