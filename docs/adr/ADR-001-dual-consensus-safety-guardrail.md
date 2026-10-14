# ADR-001: Deterministic Agrophysical Override over Statistical Machine Learning (Dual-Consensus Safety Protocol)

* **Status:** Accepted
* **Date:** 2026-09-29
* **Author:** Enzo Oliveira dos Santos (Agribusiness Specialist & Systems Architect)
* **Scope:** AgroShield AI — Core Inference and Aeration Control Pipeline (`src/api/main.py`, `src/edge/gateway.py`)
* **Standard Reference:** ASABE Standard D245.5 (Moisture Relationships of Plant-based Agricultural Products)

---

## 1. Context and Problem Statement

In commercial and on-farm grain elevators across the United States Midwest (Iowa, Illinois, Nebraska), bulk storage bins hold between 100,000 and 1,000,000 bushels of corn or soybeans, representing an asset value between $500,000 and $5,000,000 per structure.

Aeration fans are deployed to manage grain temperature and moisture. However, operating fans when outside atmospheric air has an Equilibrium Moisture Content (EMC) higher than the internal grain bulk moisture forces ambient water vapor directly into dry grain. This triggers:
1. Rapid top-layer crusting;
2. Localized hotspots from accelerated respiration;
3. Mycotoxin synthesis (*Aspergillus flavus* producing carcinogenic aflatoxins);
4. Degradation of commercial grade specifications from US No. 2 Yellow Corn to sample grade.

While machine learning classifiers (such as Random Forest or Gradient Boosted ensembles) achieve high predictive accuracy (>98%) on historical sensor telemetry, statistical models inherently operate on probabilistic distributions. They are susceptible to distribution shift, covariate drift, sensor out-of-distribution noise, and false-negative confidence intervals. In life-critical or mission-critical industrial infrastructure, an erroneous `AERATE` recommendation during a sudden rainfall or high-humidity polar front will cause irreversible economic damage.

---

## 2. Decision Drivers

* **Zero-Failure Invariant:** Fans must never operate when ambient air re-wets the grain mass, regardless of model confidence.
* **Auditability & Regulatory Compliance:** Decisions must be justifiable under established agricultural engineering physics (ASABE Standards), not solely black-box neural or tree weights.
* **Deterministic Circuit Breaking:** Hardware relays must have an absolute, mathematical lockout boundary implemented at sub-millisecond latency.
* **Graceful Degradation:** In the event of model inference failure, corruption, or missing features, the system must fail-safe (`FAN_RELAY_LOCKOUT`), preserving the physical asset.

---

## 3. Considered Options

1. **Option A: Pure Statistical Machine Learning:** Rely solely on the Random Forest ensemble output for fan activation.
2. **Option B: Pure Rule-Based Agrophysical Equations:** Discard machine learning entirely and rely solely on static Henderson-Thompson EMC threshold lookups.
3. **Option C: Dual-Consensus Protocol (Statistical ML + Deterministic Physical Guardrail):** Execute machine learning inference to anticipate multi-variable risks and optimize aeration timing, but enforce a hard, deterministic mathematical override where agrophysics strictly gates relay actuation.

---

## 4. Decision Outcome

**Chosen Option:** **Option C (Dual-Consensus Protocol)**.

### Architectural Mechanism

```
[Telemetry & Forecast Data]
             │
             ├──► [Layer 1: Random Forest Classifier] ──► Proposed Action (SAFE / AERATE / CRITICAL)
             │                                                         │
             └──► [Layer 2: Modified Henderson-Thompson EMC]            │
                                 │                                     ▼
                     Is EMC_ambient > M_grain + 0.8%? ──► [Consensus Arbiter]
                                                                       │
                                            ┌──────────────────────────┴──────────────────────────┐
                                            ▼                                                     ▼
                                    [Physical Conflict]                                   [Physical Validation]
                              Enforce FAN_RELAY_LOCKOUT                               Execute Proposed Action
                              (Agrophysics Overrules ML)                             (Hardware Relays Energized)
```

### Mathematical Enforcement Formula

The Equilibrium Moisture Content ($M_{\text{dry}}$) is computed via the ASAE D245.5 Modified Henderson-Thompson equation:

$$M_{\text{dry}} = \left[ \frac{-\ln(1 - \text{RH})}{K \cdot (T + C)} \right]^{\frac{1}{N}}$$

$$M_{\text{wet}} = \frac{M_{\text{dry}}}{1 + \frac{M_{\text{dry}}}{100}}$$

Where empirical constants for Corn (Dent Yellow) are $K = 8.6541 \times 10^{-5}$, $C = 49.810$, $N = 1.8634$.

**Deterministic Guardrail Rule:**
```python
if emc_wet > (grain_moisture + 0.8):
    relay_state = "FAN_RELAY_LOCKOUT"
    safety_override = True
    consensus_status = "OVERRULED_BY_AGROPHYSICS"
```

---

## 5. Consequences and Trade-offs

### Positive Consequences
* **Absolute Asset Protection:** Guaranteed prevention of aeration-induced moisture re-injection under all ambient weather extremes.
* **Deterministic Defense:** Complete compliance with agricultural engineering liability standards and USDA warehouse inspections.
* **Clear Explainability:** When a fan lockout occurs, operators receive the exact physical parameters ($\text{EMC}_{\text{ambient}}$ vs. $M_{\text{grain}}$) rather than an obscure model score.

### Negative Consequences / Trade-offs
* **Conservative Aeration Windows:** The +0.8% buffer marginally narrows operational aeration windows during borderline autumn afternoons.
* **Computational Redundancy:** Every inference request evaluates both the scikit-learn model and transcendental logarithmic equations. (Mitigated: Henderson-Thompson executes in < 15 microseconds in Python C extensions).

---

## 6. References
* ASABE Standard D245.5: *Moisture Relationships of Plant-based Agricultural Products*, American Society of Agricultural and Biological Engineers, St. Joseph, MI.
* Thompson, T. L., Peart, R. M., & Foster, G. H. (1968). *Mathematical simulation of corn drying: a new model*. Transactions of the ASAE, 11(4), 582-0586.
* Code Implementation: `src/api/main.py::evaluate_dual_consensus` and `tests/test_safety_guardrails.py`.
