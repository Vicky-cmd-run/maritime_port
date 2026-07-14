# 🚢 Maritime Port Intelligence Platform

An AI-powered maritime intelligence platform that delivers cargo forecasting, port congestion prediction, trade trend analytics, and an integrated Security Operations Center (SOC) for maritime domain awareness.

## Overview

The Maritime Port Intelligence Platform is a full-stack analytics solution designed for government agencies, maritime authorities, logistics operators, and enterprise stakeholders operating within the Indian Ocean region.

The platform combines operational intelligence and cybersecurity monitoring into a single command center, enabling users to:

- Forecast cargo volumes
- Predict port congestion risks
- Analyze import/export trade trends
- Generate operational recommendations
- Monitor cyber threats through an integrated SOC
- Maintain DPDP-aligned audit visibility
- Simulate secure inter-agency collaboration

---

## Key Features

### Cargo Forecasting
- 7-day cargo volume forecasting
- Confidence scoring
- Trend analysis (Bullish / Bearish / Neutral)
- Upper and lower forecast bounds

### Port Congestion Intelligence
- Congestion risk scoring
- Rolling z-score anomaly detection
- Port-wise risk breakdown
- 24-hour congestion outlook

### Trade Analytics
- Import/export trend analysis
- EMA smoothing
- Momentum scoring
- Trade projections

### AI Recommendation Engine
- Priority-based advisories
- Critical / High / Medium / Low recommendations
- Operational decision support

### Security Operations Center (SOC)
- MITRE ATT&CK mapped threat alerts
- Threat severity classification
- Security posture dashboard
- Compliance indicators

### Data Governance
- DPDP Act 2023 compliance indicators
- Four-tier data classification framework
- Tamper-evident audit logging
- Secure collaboration simulation

---

## Architecture

text User Browser      │      ▼ ┌───────────────────────────────┐ │ Streamlit Dashboard           │ │ Port 8501                     │ └──────────────┬────────────────┘                │                ▼ ┌───────────────────────────────┐ │ FastAPI Backend               │ │ Port 8000                     │ └──────┬───────────────┬────────┘        │               │        ▼               ▼  Forecast Engines   Security Engine        │               │        ▼               ▼  NumPy/Pandas      Audit Logs 

---

## Technology Stack

### Frontend
- Streamlit
- Plotly

### Backend
- FastAPI
- Uvicorn
- Pydantic

### Data & Analytics
- Pandas
- NumPy

### Security
- MITRE ATT&CK Mapping
- DPDP Compliance Framework
- Audit Logging
- Data Classification

---

## Project Structure

```text
maritime-port-intelligence-platform/
├── assets/                  # Logos and architecture diagram images
├── backend/                 # FastAPI app
│   └── app/
│       ├── routes/          # FastAPI API routers
│       ├── services/        # Business logic & data services
│       └── main.py          # FastAPI application entrypoint
├── data/                    # Sample data for platform testing
│   └── sample_cargo_data.csv
├── frontend/                # Streamlit app
│   ├── .streamlit/          # Theme customization configuration
│   └── app.py               # Streamlit application dashboard
├── uploads/                 # Storage for user-uploaded CSV reports
├── Dockerfile.backend       # Docker builder for the backend image
├── Dockerfile.frontend      # Docker builder for the frontend image
├── docker-compose.yml       # Docker orchestrator for multi-container run
├── .env.example             # Env template configuration
├── .gitignore               # Ignored files template
├── requirements.txt         # Common python package dependencies
├── LICENSE                  # Repository license (MIT)
└── README.md                # System documentation and manuals
```

---

## API Endpoints

### Health
```http
GET /health
```

### Upload
```http
POST /upload/
```

### Forecasting
```http
GET /forecast/cargo
GET /forecast/congestion
GET /forecast/trade
GET /forecast/recommendations
```

### Security
```http
GET /security/audit-logs
GET /security/classifications
GET /security/threat-alerts
GET /security/system-status
GET /security/collaboration-status
```

---

## Deployment & Execution

### Option 1: Run with Docker Compose (Recommended)

To spin up the entire multi-container environment (FastAPI Backend + Streamlit Frontend) in one command:

1. **Start Services:**
   ```bash
   docker-compose up --build
   ```
2. **Access the Applications:**
   - **Frontend Dashboard:** [http://localhost:8501](http://localhost:8501)
   - **Backend API Documentation (Swagger Docs):** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Backend API Root:** [http://localhost:8000](http://localhost:8000)

---

### Option 2: Local Installation (Without Docker)

#### 1. Setup Virtual Environment
```bash
python3 -m venv venv311
source venv311/bin/activate
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Run FastAPI Backend
```bash
uvicorn backend.app.main:app --reload --port 8000
```
- **Backend API:** [http://localhost:8000](http://localhost:8000)
- **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

#### 4. Run Streamlit Frontend
In a new terminal window (with the virtual environment activated):
```bash
streamlit run frontend/app.py
```
- **Dashboard UI:** [http://localhost:8501](http://localhost:8501)

---

## Security Highlights

- MITRE ATT&CK aligned threat intelligence
- DPDP Act 2023 compliance indicators
- Four-level data classification
- Tamper-evident audit trail
- Secure collaboration framework
- Input validation for uploads
- No hardcoded secrets

---

## Future Enhancements

- PostgreSQL integration
- JWT Authentication
- Redis caching
- Kubernetes deployment
- Real AIS vessel tracking integration
- Real-world customs and trade APIs
- Advanced ML forecasting models

---

## Use Cases

- Port Operations Centers
- Maritime Security Agencies
- Government Maritime Departments
- Logistics Operators
- Supply Chain Intelligence Teams
- Trade Monitoring Authorities

---

## License

Released under the MIT License.

---

## Author

Dweep Solanki

Cybersecurity Professional | Maritime Intelligence | AI & Analytics | Security Operations