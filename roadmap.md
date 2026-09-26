# AgroShield AI – Roadmap

## Phase 1 – Data and Baseline Model
- [ ] Collect public climate data (NOAA, INMET, etc.) and store in `data/raw/`.
- [ ] Build cleaning pipeline and save processed data in `data/processed/`.
- [ ] Exploratory Data Analysis (EDA) in `notebooks/01-EDA.ipynb`.
- [ ] Train a first baseline ML model for climate risk prediction.
- [ ] Save trained model artifacts in `src/models/`.

## Phase 2 – API and Integration
- [ ] Create FastAPI endpoints to expose predictions.
- [ ] Implement healthcheck and basic status endpoints.
- [ ] Connect model loading and prediction to the API.

## Phase 3 – Dashboard and User Experience
- [ ] Design first version of a web dashboard (React/Next.js) in `src/dashboard/`.
- [ ] Visualize regional risk indicators, forecast curves, and alerts.
- [ ] Add simple authentication (optional).

## Phase 4 – Advanced Features
- [ ] Add economic impact estimation (loss in USD per hectare).
- [ ] Implement alert system (e-mail, WhatsApp/Telegram integration).
- [ ] Prepare whitepaper and technical documentation in `docs/` for EB-2 NIW evidence.
