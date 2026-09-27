# AgroShield AI — Climate Risk & Grain Storage Preservation Engine

<p align="center">
  <img src="https://img.shields.io/badge/Food%20Security-Critical%20Infrastructure-green?style=for-the-badge">
  <img src="https://img.shields.io/badge/Machine%20Learning-Random%20Forest%20Ensemble-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/Jurisdiction-Iowa%20Corn%20Belt-orange?style=for-the-badge">
  <img src="https://img.shields.io/badge/Build-Passing-brightgreen?style=for-the-badge">
</p>

> **Autonomous predictive system designed to prevent post-harvest grain spoilage, thermal shock condensation, and mycotoxin loss across United States storage bins.**  
> Developed and Engineered by **Enzo Oliveira dos Santos**.

---

## 🌾 The National Problem (US Critical Infrastructure)

The **Cybersecurity and Infrastructure Security Agency (CISA)** and the **Department of Homeland Security (DHS)** classify the **Food and Agriculture Sector** as Critical Infrastructure. 

In the Midwest (Iowa, Illinois, Nebraska), extreme weather swings in autumn and winter cause **internal condensation** in grain bins:
* Warm grain (20°C+) creates rising moisture plumes that hit freezing corrugated steel roofs.
* Water condenses and drips onto the top surface, triggering rapid **crusting, fungal growth (*Aspergillus*), and mycotoxin contamination**.
* Unmanaged fan aeration in humid weather forces water into dry grain, destroying market value.

**AgroShield AI** provides an autonomous bridge between agrophysical principles and machine learning to predict risks 72 hours in advance and automate aeration decision support.

---

## 🏛️ System Architecture

```
                  NOAA Climate Ingestion (Iowa GHCN)
                                  │
                                  ▼
           ┌──────────────────────────────────────────────┐
           │      Equilibrium Moisture Content (EMC)      │
           │         Henderson-Thompson Equation          │
           │              (ASAE D245.5)                   │
           └──────────────────────┬───────────────────────┘
                                  │
                                  ▼
           ┌──────────────────────────────────────────────┐
           │        Machine Learning Risk Classifier      │
           │         Scikit-Learn Ensemble (RF)           │
           │       98.44% Accuracy · 0.9807 F1-Score      │
           └──────────────────────┬───────────────────────┘
                                  │
                                  ▼
           ┌──────────────────────────────────────────────┐
           │          FastAPI Resilient Microservice      │
           │  Pydantic Boundary Guard + Graceful Fallback │
           └──────────────────────┬───────────────────────┘
                                  │
          ┌───────────────────────┴───────────────────────┐
          ▼                                               ▼
[Automated Aeration Relays]                  [Agronomic Decision Dashboard]
```

---

## 📐 Mathematical Formulation (Henderson-Thompson)

The agrophysical core evaluates the Equilibrium Moisture Content ($M_{\text{dry}}$) between ambient air and grain mass:

$$M_{\text{dry}} = \left[ \frac{-\ln(1 - \text{RH})}{K \cdot (T + C)} \right]^{\frac{1}{N}}$$

* **Corn (Dent Yellow):** $K = 8.6541 \times 10^{-5}, \quad C = 49.810, \quad N = 1.8634$
* **Soybeans:** $K = 1.1172 \times 10^{-4}, \quad C = 91.560, \quad N = 1.7010$

If outside $\text{EMC} > M_{\text{grain}} + 0.8\%$, fan operation is locked to prevent re-wetting dry grain.

---

## 📊 Benchmark Results

| Metric | Result | Standard / Method |
| :--- | :---: | :--- |
| **Test Accuracy** | **98.44%** | Stratified Holdout (640 samples) |
| **F1-Score (Macro)** | **0.9807** | Multi-class (Safe / Aerate / Critical) |
| **5-Fold Cross Validation** | **0.9803 $\pm$ 0.0112** | 5-Fold Stratified CV |
| **Top Feature** | **Moisture % (45.2%)** | Gini Feature Importance |
| **Second Feature** | **Thermal Gradient (25.8%)** | Headspace Condensation Driver |

---

## 🚀 Quickstart & Execution

### 1. Installation
```bash
git clone https://github.com/enzooliveiradossantos1997-hash/agroshield-ai.git
cd agroshield-ai
pip install -r requirements.txt
```

### 2. Run the Automated Test Suite (Unittest)
```bash
python -m unittest tests/test_api_runner.py -v
```
*Expected: 8/8 tests pass with 100% OK.*

### 3. Start the API Server
```bash
uvicorn src.api.main:app --reload --port 8000
```
Open interactive Swagger documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 4. Interactive Jupyter Notebooks
Explore the analytical methodology:
* `notebooks/01-EDA.ipynb` — Iowa telemetry distribution & ASAE standards.
* `notebooks/02-Modeling.ipynb` — Scikit-Learn training, ROC curves, and confusion matrix.
* `notebooks/03-Results.ipynb` — Financial savings simulation ($60,000+ per 250k-bu bin).

---

## 📑 Technical Whitepaper

Read the complete engineering and agronomic specification for immigration or institutional review:  
👉 [docs/whitepaper_grain_loss_mitigation.md](docs/whitepaper_grain_loss_mitigation.md)

---

## 👤 Author & Architecture

**Enzo Oliveira dos Santos**  
* Graduate in Agribusiness Management
* Master of Science Candidate in Software Engineering
* Contact: enzooliveiradossantos1997@gmail.com
* GitHub: [@enzooliveiradossantos1997-hash](https://github.com/enzooliveiradossantos1997-hash)

---

© 2026 AgroShield AI · All rights reserved.
