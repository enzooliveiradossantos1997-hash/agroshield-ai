# AgroShield AI — Executive Dashboard

Production interface and decision-support console for grain bin managers, agricultural engineers, and institutional auditing.

## Features
- **Live NOAA Mesoscale Telemetry:** Real-time temperature, relative humidity, dew point, and 48h freeze minimum for major US Corn Belt hubs (Story County, IA; McLean County, IL; York County, NE; etc.).
- **ASAE D245.5 Agrophysical Engine:** Live calculation of Equilibrium Moisture Content (EMC) via Modified Henderson-Thompson.
- **Automated Relay Control Diagnostics:** Visual display of fan relay states (`FAN_RELAY_LOCKOUT`, `FAN_RELAY_ON_STAGE_1`, `FAN_RELAY_ON_STAGE_2`, `FAN_RELAY_OFF`).
- **CBOT / USDA Financial ROI Audit:** Real-time computation of asset valuation and economic loss mitigation in US Dollars ($).

## Running Locally
```bash
streamlit run src/dashboard/app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.
