# 🔐 Aadhaar Identity Intelligence Platform

A comprehensive analytics and AI-powered platform for analyzing Aadhaar identity data patterns at micro-geographic (pincode) level.

## 🎯 Novel Features (Not Done Before)

### 1. **Identity Velocity Index (IVI)**
- Measures identity data volatility at pincode level
- Formula: `(Bio Updates + Demo Updates) / Enrolments × 100`
- Higher IVI = More identity changes per capita

### 2. **Biometric Stress Index (BSI)**
- Identifies regions with biometric authentication issues
- Formula: `Bio Updates / Demo Updates`
- Higher BSI = More biometric-related problems

### 3. **State Clustering by Identity Behavior**
- Clusters states into categories: Stable, High Volatility, High Stress
- Uses ML (K-Means + PCA) for pattern discovery

### 4. **Anomaly Detection System**
- Real-time detection of unusual update patterns
- Uses Isolation Forest for anomaly scoring

### 5. **Agentic AI Analysis**
- Multi-agent system with specialized roles:
  - **Monitor Agent**: Detects anomalies and alerts
  - **Insight Agent**: Discovers patterns
  - **Policy Agent**: Generates recommendations
  - **Narrative Agent**: Creates human-readable reports

## 📊 Dashboard Pages

1. **📊 Dashboard** - Executive overview with KPIs and trends
2. **🗺️ State Analysis** - State clustering and comparison
3. **📍 Pincode Analytics** - Micro-geographic analysis with risk scoring
4. **⚠️ Anomaly Detection** - Real-time anomaly alerts
5. **📈 Forecasting** - 30-day demand predictions
6. **🤖 AI Assistant** - Interactive chat and auto-reports

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Clone/navigate to project
cd AadharAnalysis

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Optional: Enable AI Chat (NVIDIA NIM)

Uses **Moonshot Kimi K2 Thinking** - excellent for complex reasoning and analytical tasks.

1. Get your free API key from: https://build.nvidia.com/
2. Create a `.env` file in the project root:

```env
NVIDIA_API_KEY=nvapi-your-api-key-here
```

Or set it directly:
```bash
# Windows PowerShell
$env:NVIDIA_API_KEY="nvapi-your-api-key-here"

# Windows CMD
set NVIDIA_API_KEY=nvapi-your-api-key-here

# Mac/Linux
export NVIDIA_API_KEY=nvapi-your-api-key-here
```

## 📁 Project Structure

```
AadharAnalysis/
├── app.py                 # Main Streamlit dashboard
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── data/                 # Data folder
│   ├── api_data_aadhar_biometric/
│   ├── api_data_aadhar_demographic/
│   └── api_data_aadhar_enrolment/
└── src/
    ├── __init__.py
    ├── data_pipeline.py  # Data loading & processing
    ├── ml_models.py      # ML models (anomaly, clustering, forecast)
    └── agents.py         # Agentic AI system
```

## 🔬 Technical Architecture

```
┌─────────────────────────────────────────────────────┐
│              STREAMLIT WEB DASHBOARD                │
│  [Dashboard] [State] [Pincode] [Anomaly] [AI Chat]  │
└─────────────────────────────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            │    AGENTIC AI LAYER     │
            │      (LangGraph)        │
            │  Monitor → Insight →    │
            │  Policy → Narrative     │
            └─────────────────────────┘
                         │
            ┌────────────┴────────────┐
            │   ANALYTICS ENGINE      │
            │  • IVI/BSI Calculators  │
            │  • Anomaly Detection    │
            │  • State Clustering     │
            │  • Demand Forecasting   │
            └─────────────────────────┘
                         │
            ┌────────────┴────────────┐
            │    DATA PIPELINE        │
            │  • CSV Loaders          │
            │  • Data Cleaning        │
            │  • Feature Engineering  │
            └─────────────────────────┘
```

## 📈 Data Summary

| Dataset | Records | Pincodes | Coverage |
|---------|---------|----------|----------|
| Biometric | 1.86M | 19,707 | 57 States |
| Demographic | 2.07M | 19,742 | 65 States |
| Enrolment | 1.01M | 19,463 | 55 States |

## 🏆 Use Cases

1. **UIDAI Operations** - Resource allocation for enrolment centers
2. **Policy Planning** - Identify states needing biometric alternatives
3. **Data Quality** - Detect anomalies and data integrity issues
4. **Demand Forecasting** - Predict future service demand
5. **Performance Monitoring** - Track system health metrics

## 🛠️ Technologies Used

- **Python** - Core language
- **Streamlit** - Web dashboard
- **Pandas/NumPy** - Data processing
- **Scikit-learn** - ML models
- **Plotly** - Interactive visualizations
- **LangGraph** - Agentic AI orchestration
- **Prophet** - Time series forecasting (optional)

## 📝 License

MIT License - Free for academic and commercial use.

## 🤝 Contributing

Pull requests welcome! Please read the contributing guidelines first.

---

**Built for Aadhaar Analytics Competition** 🏆

