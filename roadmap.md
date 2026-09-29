# AgroShield AI — Engineering Roadmap & Milestones

Autonomous predictive system for grain storage preservation, post-harvest spoilage mitigation, and condensation prevention across the US Corn Belt.

---

## ✅ Phase 1 – Agrophysics, Data & Machine Learning Core (COMPLETED)
- [x] Integrate ASAE D245.5 Modified Henderson-Thompson Equilibrium Moisture Content (EMC) equation.
- [x] Train Scikit-Learn Random Forest Ensemble model on Midwest climate & telemetry data (98.44% Accuracy, 0.9807 F1-Score).
- [x] Serialize model artifacts and metrics (`spoilage_model.joblib`, `model_metrics.json`).
- [x] Exploratory Data Analysis & Validation in `notebooks/`.

## ✅ Phase 2 – Production Microservice & Real-Time Ingestion (COMPLETED)
- [x] FastAPI microservice with strict Pydantic physical boundary validation.
- [x] Graceful degradation architecture: deterministic agrophysical fallback if ML model fails.
- [x] **Live NOAA/NWS Ingestion Service (`src/services/weather_service.py`):** Real-time weather observations for Iowa, Illinois, Nebraska, Minnesota with in-memory TTL caching.
- [x] **Autonomous Advisory & Relay Engine:** Real-time generation of aeration commands (`FAN_RELAY_LOCKOUT`, `FAN_RELAY_ON_STAGE_1`, `FAN_RELAY_ON_STAGE_2`, `FAN_RELAY_OFF`).
- [x] **Observability:** Prometheus metrics instrumentation (`/metrics`) tracking latency, risk levels, and relay activations.
- [x] Multi-stage hardened `Dockerfile` (non-root security compliance) and `docker-compose.yml`.
- [x] Comprehensive test suite (23/23 automated tests passing).

## 🚀 Phase 3 – Edge Computing & Offline-First Resiliency (CURRENT SPRINT)
- [ ] Lightweight Edge Decision Engine (microcontroller / local gateway support for remote silos without internet).
- [ ] Telemetry ingestion over MQTT / WebSockets for continuous bin cable monitoring.
- [ ] Circuit breaker simulation and chaos engineering tests (network partition resilience).

## 📊 Phase 4 – Executive Financial ROI Dashboard & US Market Expansion
- [ ] Interactive Web Dashboard for elevator & farm managers (simulating monetary savings per 250k-bu bin).
- [ ] USDA ERS & CBOT commodity pricing integration (live corn and soybean loss calculations).
- [ ] Immigration & Institutional Dossier (`docs/whitepaper_grain_loss_mitigation.md`) aligned with *Matter of Dhanasar* (EB-2 NIW).
