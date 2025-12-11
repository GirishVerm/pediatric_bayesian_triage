## Pediatric Diagnosis Assistant (NAVYA)

A lightweight, ontology-backed pediatric disease diagnosis assistant. It ingests curated disease–phenotype evidence into a local SQLite database and runs an evidence-driven inference loop to suggest the most informative next symptoms and converge to a likely diagnosis.

### Highlights
- **Ontology-backed schema**: Uses HPO for phenotypes and can store SNOMED/LOINC codes.
- **Evidence-driven inference**: Posterior updates using positive likelihood ratios; dynamic selection of next questions.
- **Curated inputs**: Start with a small curated CSV dataset and expand with evidence rows.
- **Local-first**: Simple SQLite DB; easy to run and iterate.

## Repository Contents
- **`pediatric.db`**: The main database file containing the well-performing model (105/106 convergence).
- **`inference.py`**: Implements the interactive inference loop: computes posteriors, suggests next symptoms, explains terms in plain language, and applies coverage/scarcity/cluster boosts.
- **`FORMULAS_AND_METHODOLOGY.md`**: Detailed explanation of the mathematical framework (Bayesian inference, Likelihood Ratios, Information Gain).
- **`frontend/`**: Modern Python GUI frontend code.
- **`requirements.txt`**: External Python dependency pinning.

## Quick Start

### 1) Environment
- Requires **Python 3.10+**.
- Install dependencies:
```bash
pip install -r requirements.txt
```

### 2) Run Inference
- Preview recommended next symptoms (top-N):
```bash
python inference.py --preview 10
```
- Interactive CLI:
```bash
python inference.py
```

### 3) Run Frontend GUI
```bash
cd frontend
pip install -r requirements.txt
python main.py
```

## Current Status (December 2025)

### Performance Metrics
- **Total Diseases**: 162
- **Phenotypes**: 812 unique symptom terms
- **Evidence Rows**: 1,139 (all validated from published sources with PMIDs and detailed citations)
- **Convergence Rate**: ~99% in simulation tests
- **Published Sources**: Multiple guideline organizations (AAP, AHA, IDSA, ISPAD, ILAE, CDC, ECCO, CF Foundation, etc.)

## How It Works

The system operates on a transparent **Bayesian Inference** model, avoiding "black box" machine learning in favor of explainable, evidence-based probability updates.

### 1. The Knowledge Graph
The core is a directed graph linking **Diseases** to **Phenotypes** (symptoms) via **Evidence** edges.
- Each edge contains a **Likelihood Ratio (LR+)**, derived from clinical sensitivity and specificity.
- `LR+ = Sensitivity / (1 - Specificity)`
- Example: "Strawberry tongue" has a high LR+ for Kawasaki Disease, making it a strong predictor.

### 2. Probability Update (Bayes' Theorem)
When a user confirms a symptom, the probability of each disease is updated:
```
Posterior Odds = Prior Odds × LR+
```
This allows the model to dynamically shift its confidence based on observed evidence.

### 3. Smart Question Selection (Information Gain)
To avoid asking irrelevant questions, the system calculates the **Information Gain (IG)** for every possible unasked symptom.
- It asks: "Which symptom, if known, would most reduce the uncertainty (entropy) of the current diagnosis?"
- This creates an optimal "question path" unique to each patient's presentation.

### 4. Dynamic Heuristics
To handle real-world complexity, the inference engine applies transparent boosts:
- **Cluster Boost**: Increases weight if multiple symptoms affect the same organ system (e.g., Respiratory).
- **Scarcity Boost**: Helps rare diseases with few symptoms compete against common diseases.
- **Stage Boost**: Accelerates convergence when a single disease becomes the clear leader.

## Data and Sources Used

### Evidence Sources
All evidence rows are validated from published sources with specific PMIDs:
- **American Academy of Pediatrics (AAP)**: Clinical Practice Guidelines
- **Infectious Diseases Society of America (IDSA)**: Guidelines
- **World Health Organization (WHO)**: Pneumonia diagnostic criteria
- **Global Initiative for Asthma (GINA)**: Asthma diagnostic criteria
- **Rome IV Criteria**: Constipation diagnostic criteria
- **International Headache Society (IHS)**: Headache diagnostic criteria

## Notes
- This repository is for research/prototyping only and is **not** a clinical decision aid.
- Please review and validate evidence and outputs with qualified domain experts before any real-world use.
