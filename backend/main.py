"""
FastAPI Backend for Aadhaar Identity Intelligence Platform
Optimized for high-performance data delivery with caching
"""
from fastapi import FastAPI, HTTPException, Query, Path as PathParam
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path
import asyncio
from functools import lru_cache
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_pipeline import get_pipeline
from ml_models import AnomalyDetector, StateClustering, DemandForecaster, IdentityLifecyclePredictor

# Initialize FastAPI
app = FastAPI(
    title="Aadhaar Identity Intelligence API",
    description="High-performance analytics API for Aadhaar data",
    version="2.0.0"
)

# CORS - Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global cache for pipeline (singleton)
_pipeline_cache = None
_analytics_cache = {}
_cache_timestamp = {}

def get_cached_pipeline():
    """Get or create pipeline instance with caching."""
    global _pipeline_cache
    if _pipeline_cache is None:
        # Use parent directory's data folder - resolve to absolute path
        data_path = (Path(__file__).parent.parent / "data").resolve()
        print(f"[INFO] Loading data from: {data_path}")
        print(f"[INFO] Data path exists: {data_path.exists()}")
        if data_path.exists():
            print(f"[INFO] Subdirectories: {list(data_path.iterdir())}")
        _pipeline_cache = get_pipeline(str(data_path))
        _pipeline_cache.load_all_data()
    return _pipeline_cache

@lru_cache(maxsize=1)
def get_analytics_cached():
    """Cache analytics computation for 5 minutes."""
    pipeline = get_cached_pipeline()
    return {
        'summary': pipeline.get_summary_stats(),
        'state_data': pipeline.get_state_analytics(),
        'pincode_data': pipeline.get_pincode_analytics(),
        'temporal': pipeline.get_temporal_analytics()
    }


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "operational",
        "service": "Aadhaar Identity Intelligence API",
        "version": "2.0.0",
        "documentation": "/docs"
    }

@app.get("/health")
async def health():
    """Detailed health check."""
    try:
        pipeline = get_cached_pipeline()
        return {
            "status": "healthy",
            "data_loaded": pipeline._bio_df is not None,
            "timestamp": time.time()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


# ============================================================================
# SUMMARY & OVERVIEW
# ============================================================================

@app.get("/api/summary")
async def get_summary():
    """
    Get executive summary statistics.
    Returns: KPIs, totals, averages, top states
    """
    try:
        analytics = get_analytics_cached()
        summary = analytics['summary']
        
        return {
            "metrics": {
                "total_bio_updates": summary['total_bio_updates'],
                "total_demo_updates": summary['total_demo_updates'],
                "total_enrolments": summary['total_enrolments'],
                "unique_pincodes": summary['unique_pincodes'],
                "unique_states": summary['unique_states'],
                "unique_districts": summary['unique_districts'],
            },
            "indices": {
                "avg_ivi": round(summary['avg_ivi'], 2),
                "avg_bsi": round(summary['avg_bsi'], 2),
            },
            "top_performers": {
                "top_state": summary['top_state'],
                "high_stress_state": summary['high_stress_state'],
            },
            "date_range": summary['date_range']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# STATE ANALYTICS
# ============================================================================

@app.get("/api/states")
async def get_all_states():
    """
    Get list of all states with basic metrics.
    Optimized for dropdown/selection.
    """
    try:
        analytics = get_analytics_cached()
        state_data = analytics['state_data']
        
        states = []
        for _, row in state_data.iterrows():
            states.append({
                "name": row['state'],
                "total_updates": int(row['total_updates']),
                "ivi": round(float(row['IVI']), 2),
                "bsi": round(float(row['BSI']), 2),
            })
        
        # Sort by total updates descending
        states.sort(key=lambda x: x['total_updates'], reverse=True)
        
        return {"states": states, "count": len(states)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/states/{state_name}")
async def get_state_detail(state_name: str):
    """
    Get detailed analytics for a specific state.
    """
    try:
        analytics = get_analytics_cached()
        state_data = analytics['state_data']
        
        state_row = state_data[state_data['state'].str.lower() == state_name.lower()]
        
        if state_row.empty:
            raise HTTPException(status_code=404, detail=f"State '{state_name}' not found")
        
        row = state_row.iloc[0]
        
        return {
            "state": row['state'],
            "biometric_updates": {
                "total": int(row['total_bio_updates']),
                "youth_5_17": int(row['bio_age_5_17']),
                "adult_17_plus": int(row['bio_age_17_']),
            },
            "demographic_updates": {
                "total": int(row['total_demo_updates']),
                "youth_5_17": int(row['demo_age_5_17']),
                "adult_17_plus": int(row['demo_age_17_']),
            },
            "enrolments": {
                "total": int(row['total_enrolments']),
                "age_0_5": int(row['age_0_5']),
                "age_5_17": int(row['age_5_17']),
                "age_18_plus": int(row['age_18_greater']),
            },
            "indices": {
                "ivi": round(float(row['IVI']), 2),
                "bsi": round(float(row['BSI']), 2),
                "youth_ratio": round(float(row['youth_ratio']) * 100, 2),
                "stability_score": round(float(row['stability_score']), 1),
            },
            "total_updates": int(row['total_updates'])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/states/compare/{state1}/{state2}")
async def compare_states(state1: str, state2: str):
    """Compare two states side-by-side."""
    try:
        s1_data = await get_state_detail(state1)
        s2_data = await get_state_detail(state2)
        
        return {
            "state1": s1_data,
            "state2": s2_data,
            "comparison": {
                "ivi_diff": s1_data['indices']['ivi'] - s2_data['indices']['ivi'],
                "bsi_diff": s1_data['indices']['bsi'] - s2_data['indices']['bsi'],
                "update_diff": s1_data['total_updates'] - s2_data['total_updates'],
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CLUSTERING
# ============================================================================

@app.get("/api/clustering")
async def get_state_clustering():
    """
    Get state clustering analysis with PCA coordinates.
    """
    try:
        analytics = get_analytics_cached()
        state_data = analytics['state_data']
        
        # Run clustering
        clusterer = StateClustering(n_clusters=4)
        clustered = clusterer.fit_predict(state_data)
        profiles = clusterer.get_cluster_profiles(clustered)
        
        # Prepare data for frontend
        clusters = []
        for _, row in clustered.iterrows():
            clusters.append({
                "state": row['state'],
                "cluster": int(row['cluster']),
                "cluster_label": row['cluster_label'],
                "pca_x": float(row['pca_x']),
                "pca_y": float(row['pca_y']),
                "total_updates": int(row['total_updates']),
                "ivi": round(float(row['IVI']), 2),
                "bsi": round(float(row['BSI']), 2),
            })
        
        # Cluster profiles
        cluster_summary = []
        for cluster_name, profile in profiles.items():
            cluster_summary.append({
                "id": int(cluster_name.split()[-1]),
                "label": profile['label'],
                "count": profile['count'],
                "avg_ivi": round(profile['avg_IVI'], 2),
                "avg_bsi": round(profile['avg_BSI'], 2),
                "states": profile['states'][:10],  # Top 10
            })
        
        return {
            "clusters": clusters,
            "profiles": cluster_summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ANOMALY DETECTION
# ============================================================================

@app.get("/api/anomalies")
async def get_anomalies(limit: int = Query(50, ge=1, le=1000)):
    """
    Get anomaly detection results.
    """
    try:
        analytics = get_analytics_cached()
        pincode_data = analytics['pincode_data']
        
        detector = AnomalyDetector(contamination=0.05)
        anomalies = detector.detect_pincode_anomalies(pincode_data)
        
        # Get anomalous pincodes
        anomalous = anomalies[anomalies['is_anomaly']].nlargest(limit, 'anomaly_score')
        
        results = []
        for _, row in anomalous.iterrows():
            results.append({
                "pincode": int(row['pincode']),
                "state": row['state'],
                "district": row['district'],
                "anomaly_score": round(float(row['anomaly_score']), 3),
                "ivi": round(float(row['identity_velocity_index']), 2),
                "bsi": round(float(row['biometric_stress_index']), 2),
                "total_updates": int(row['total_updates']),
            })
        
        summary = detector.get_anomaly_summary(anomalies)
        
        return {
            "anomalies": results,
            "summary": {
                "total_anomalies": summary['anomaly_count'],
                "anomaly_percentage": round(summary['anomaly_percentage'], 2),
                "total_pincodes": summary['total_records'],
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# FORECASTING
# ============================================================================

@app.get("/api/forecast/{metric}")
async def get_forecast(
    metric: str = PathParam(..., pattern="^(bio|demo|enrol)$"),
    days: int = Query(30, ge=7, le=90)
):
    """
    Get demand forecast for specified metric.
    Metrics: bio, demo, enrol
    """
    try:
        analytics = get_analytics_cached()
        temporal = analytics['temporal']
        daily_data = temporal['daily']
        
        # Map metric names
        metric_map = {
            'bio': 'total_bio_updates',
            'demo': 'total_demo_updates',
            'enrol': 'total_enrolments'
        }
        target_col = metric_map[metric]
        
        forecaster = DemandForecaster(forecast_days=days)
        forecast_result = forecaster.forecast_with_prophet(daily_data, target_col)
        
        return {
            "metric": metric,
            "method": forecast_result['method'],
            "historical": forecast_result['historical'][:100],  # Last 100 days
            "forecast": forecast_result['forecast'],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TEMPORAL TRENDS
# ============================================================================

@app.get("/api/trends/monthly")
async def get_monthly_trends():
    """Get monthly trend data for all metrics."""
    try:
        analytics = get_analytics_cached()
        temporal = analytics['temporal']
        
        # Convert Period to string for JSON serialization
        bio_monthly = [(str(k), int(v)) for k, v in temporal['bio_monthly'].items()]
        demo_monthly = [(str(k), int(v)) for k, v in temporal['demo_monthly'].items()]
        enrol_monthly = [(str(k), int(v)) for k, v in temporal['enrol_monthly'].items()]
        
        return {
            "biometric": bio_monthly,
            "demographic": demo_monthly,
            "enrolment": enrol_monthly,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trends/daily")
async def get_daily_trends(limit: int = Query(90, ge=7, le=365)):
    """Get daily trend data (last N days)."""
    try:
        analytics = get_analytics_cached()
        temporal = analytics['temporal']
        daily = temporal['daily'].tail(limit)
        
        trends = []
        for idx, row in daily.iterrows():
            # Date is a column, not index - handle both datetime and string
            date_val = row['date']
            if hasattr(date_val, 'strftime'):
                date_str = date_val.strftime('%Y-%m-%d')
            else:
                date_str = str(date_val)
            
            trends.append({
                "date": date_str,
                "bio_updates": int(row['total_bio_updates']),
                "demo_updates": int(row['total_demo_updates']),
                "enrolments": int(row['total_enrolments']),
                "total_activity": int(row['total_activity']),
            })
        
        return {"trends": trends, "days": len(trends)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PINCODE ANALYTICS
# ============================================================================

@app.get("/api/pincodes/high-risk")
async def get_high_risk_pincodes(limit: int = Query(100, ge=1, le=1000)):
    """Get high-risk pincodes based on update probability."""
    try:
        analytics = get_analytics_cached()
        pincode_data = analytics['pincode_data']
        
        predictor = IdentityLifecyclePredictor()
        risk_data = predictor.calculate_update_probability(pincode_data)
        high_priority = predictor.get_high_priority_pincodes(risk_data, top_n=limit)
        
        results = []
        for _, row in high_priority.iterrows():
            results.append({
                "pincode": int(row['pincode']),
                "state": row['state'],
                "district": row['district'],
                "risk_level": row['risk_level'],
                "update_probability": round(float(row['update_probability']), 3),
                "ivi": round(float(row['identity_velocity_index']), 2),
                "bsi": round(float(row['biometric_stress_index']), 2),
                "total_updates": int(row['total_updates']),
            })
        
        return {"high_risk_pincodes": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SEARCH & FILTER
# ============================================================================

@app.get("/api/search/pincode/{pincode}")
async def search_pincode(pincode: int):
    """Search for specific pincode details."""
    try:
        analytics = get_analytics_cached()
        pincode_data = analytics['pincode_data']
        
        result = pincode_data[pincode_data['pincode'] == pincode]
        
        if result.empty:
            raise HTTPException(status_code=404, detail=f"Pincode {pincode} not found")
        
        row = result.iloc[0]
        
        return {
            "pincode": int(row['pincode']),
            "state": row['state'],
            "district": row['district'],
            "bio_updates": int(row['total_bio_updates']),
            "demo_updates": int(row['total_demo_updates']),
            "enrolments": int(row['total_enrolments']),
            "ivi": round(float(row['identity_velocity_index']), 2),
            "bsi": round(float(row['biometric_stress_index']), 2),
            "youth_ratio": round(float(row['youth_update_ratio']) * 100, 2),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CACHE MANAGEMENT
# ============================================================================

@app.post("/api/cache/clear")
async def clear_cache():
    """Clear all caches (admin endpoint)."""
    global _pipeline_cache, _analytics_cache
    _pipeline_cache = None
    _analytics_cache = {}
    get_analytics_cached.cache_clear()
    
    return {"status": "cache_cleared", "timestamp": time.time()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

