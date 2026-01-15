# 🔐 Aadhaar Identity Intelligence Platform

**Production-Grade Analytics Platform for Aadhaar Identity Data**

A comprehensive, AI-powered analytics platform for analyzing Aadhaar identity data patterns at micro-geographic (pincode) level, built with React, FastAPI, and Machine Learning.

[![Status](https://img.shields.io/badge/status-production-green.svg)](https://github.com)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18.3-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

---

## 🎯 **Novel Features**

### **1. Identity Velocity Index (IVI)**
Measures identity data volatility at pincode level
- **Formula:** `(Bio Updates + Demo Updates) / Enrolments × 100`
- **Interpretation:** Higher IVI = More identity changes per capita

### **2. Biometric Stress Index (BSI)**
Identifies regions with biometric authentication issues
- **Formula:** `Bio Updates / Demo Updates`
- **Interpretation:** Higher BSI = More biometric-related problems

### **3. ML-Powered State Clustering**
- Clusters states by identity behavior (Stable, High Volatility, High Stress)
- Uses K-Means + PCA for pattern discovery
- Provides actionable insights for each cluster

### **4. Real-Time Anomaly Detection**
- Isolation Forest for anomaly scoring
- Detects unusual update patterns
- Pincode-level risk assessment

### **5. Demand Forecasting**
- Prophet-based time series forecasting
- 7/30/90-day predictions
- Confidence intervals and trend analysis

---

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.10+
- Node.js 18+
- npm or yarn

### **1. Clone Repository**
```bash
git clone <repository-url>
cd Aadhaar-Identity-Intelligence-Platform
```

### **2. Backend Setup**
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Backend runs at:** `http://localhost:8000`

### **3. Frontend Setup** (New Terminal)
```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev
```

**Frontend runs at:** `http://localhost:3000`

---

## 📊 **Platform Features**

### **Dashboard Pages:**

1. **📊 Dashboard** - Executive overview with KPIs, trends, and top states
2. **🗺️ States Analysis** - All 36 states with risk classification, search, filter, sort
3. **🔀 State Clustering** - ML-based state groupings with PCA visualization
4. **⚠️ Anomaly Detection** - High-risk pincodes with anomaly scores
5. **📈 Demand Forecast** - Prophet-based predictions with confidence intervals
6. **🛡️ High Risk Areas** - Top risk pincodes with detailed metrics

### **Key Capabilities:**
- ✅ **Real-time data loading** with LRU caching
- ✅ **Color-coded risk classification** (Critical/High Risk/Stable)
- ✅ **Interactive charts** with Recharts
- ✅ **Advanced filtering & sorting**
- ✅ **Responsive design** (mobile-friendly)
- ✅ **Government-grade UI** (clean, professional)

---

## 📁 **Project Structure**

```
Aadhaar-Identity-Intelligence-Platform/
├── backend/                  # FastAPI Backend
│   ├── main.py              # API endpoints
│   ├── requirements.txt     # Python dependencies
│   └── .gitignore
│
├── frontend/                # React Frontend
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API service layer
│   │   └── index.css        # Tailwind styles
│   ├── package.json
│   ├── vite.config.js
│   └── .gitignore
│
├── src/                     # Core Python Modules
│   ├── data_pipeline.py     # Data loading & cleaning
│   ├── ml_models.py         # ML models (anomaly, clustering, forecast)
│   └── agents.py            # Agentic AI system (optional)
│
├── data/                    # Data Directory
│   ├── api_data_aadhar_biometric/
│   ├── api_data_aadhar_demographic/
│   └── api_data_aadhar_enrolment/
│
├── requirements.txt         # Main Python dependencies
├── README.md               # This file
├── LICENSE                 # Apache 2.0 License
│
├── start_backend.sh        # Backend startup script (Unix)
├── start_frontend.sh       # Frontend startup script (Unix)
├── start_platform.sh       # Full platform startup (Unix)
└── start_platform.bat      # Full platform startup (Windows)
```

---

## 🔧 **Technology Stack**

### **Backend:**
- **FastAPI** - High-performance Python API framework
- **Pandas/NumPy** - Data processing
- **Scikit-learn** - Machine learning
- **Prophet** - Time series forecasting
- **Uvicorn** - ASGI server

### **Frontend:**
- **React 18.3** - UI library
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **React Query** - Data fetching & caching
- **Axios** - HTTP client

### **Data Processing:**
- **Dynamic State Matching** - Fuzzy string matching with rapidfuzz
- **Lazy Loading** - On-demand data loading
- **LRU Caching** - Fast API responses

---

## 📈 **Data Summary**

| Metric | Count |
|--------|-------|
| **Total Biometric Updates** | 69.7M+ |
| **Total Demographic Updates** | 49.2M+ |
| **Total Enrolments** | 5.4M+ |
| **Unique Pincodes** | 19,814 |
| **States Covered** | 36 |
| **Districts** | 974 |

---

## 🎨 **API Documentation**

Once the backend is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### **Key Endpoints:**

```
GET  /api/summary           # Platform summary metrics
GET  /api/states            # All states with IVI/BSI
GET  /api/states/{name}     # State detail
GET  /api/clustering        # State clustering analysis
GET  /api/anomalies         # High-risk pincodes
GET  /api/forecast/{metric} # Demand forecasting
GET  /api/trends/daily      # Daily trends
GET  /api/trends/monthly    # Monthly trends
```

---

## 🏆 **Use Cases**

1. **UIDAI Operations** - Resource allocation for enrolment centers
2. **Policy Planning** - Identify states needing biometric alternatives
3. **Data Quality** - Detect anomalies and data integrity issues
4. **Demand Forecasting** - Predict future service demand
5. **Performance Monitoring** - Track system health metrics
6. **Risk Assessment** - Identify high-risk pincodes
7. **State Benchmarking** - Compare state performance

---

## 🚀 **Production Deployment**

### **Backend (FastAPI):**
```bash
# Production server with Gunicorn
pip install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### **Frontend (React):**
```bash
# Build for production
cd frontend
npm run build

# Serve with nginx, Apache, or any static file server
# Build output is in: frontend/dist/
```

---

## 🔐 **Environment Variables**

### **Backend (.env):**
```bash
# Optional: AI Features (NVIDIA NIM)
NVIDIA_API_KEY=nvapi-your-api-key-here

# Optional: Custom data path
DATA_PATH=/path/to/data
```

### **Frontend (.env):**
```bash
# API URL (production)
VITE_API_URL=https://your-api-domain.com
```

---

## 🧪 **Testing**

```bash
# Run all tests
pytest

# Run specific test
python test_fuzzy_matching.py
python test_system.py
```

---

## 📝 **License**

Apache License 2.0 - See [LICENSE](LICENSE) file for details.

---

## 🤝 **Contributing**

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📞 **Support**

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the documentation in `/docs` folder

---

## ✨ **Acknowledgments**

Built for Aadhaar Analytics - Combining modern web technologies with advanced machine learning for government-grade data intelligence.

**Status:** ✅ Production-Ready  
**Version:** 2.0.0  
**Last Updated:** January 2026

---

**Powered by FastAPI, React, and AI** 🚀
