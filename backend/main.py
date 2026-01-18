"""
FastAPI Backend for Aadhaar Identity Intelligence Platform
Optimized for high-performance data delivery with caching
"""

import asyncio
import json
import os
import sys
import time
import uuid
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

# Production-grade conversation storage using SQLite
from conversation_db import get_conversation_db
from fastapi import FastAPI, HTTPException, Query
from fastapi import Path as PathParam
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from redis_cache import cache_with_redis, redis_cache

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
    print(f"[INFO] Loaded .env from: {env_path}")
    print(f"[INFO] NVIDIA_API_KEY present: {bool(os.getenv('NVIDIA_API_KEY'))}")
except ImportError:
    print(
        "[WARNING] python-dotenv not installed, environment variables must be set manually"
    )

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_pipeline import AadhaarDataPipeline
from ml_models import (
    AnomalyDetector,
    DemandForecaster,
    IdentityLifecyclePredictor,
    StateClustering,
)

# Initialize FastAPI
app = FastAPI(
    title="Aadhaar Identity Intelligence API",
    description="High-performance analytics API for Aadhaar data",
    version="2.0.0",
)

# CORS - Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


MAX_HISTORY = 20  # Keep last 20 messages per session


@lru_cache(maxsize=4)
def get_pipeline_for_request(year: int | None = None, month: int | None = None):
    """Get pipeline instance for specific timeframe with caching."""
    # Use parent directory's data folder - resolve to absolute path
    data_path = (Path(__file__).parent.parent / "data").resolve()

    # Create new instance to avoid state pollution in singleton
    pipeline = AadhaarDataPipeline(str(data_path))

    # If no date provided, find latest available to avoid loading everything by default
    if year is None and month is None:
        available = pipeline.get_available_months()
        if available:
            # Default to latest
            latest_year, latest_month = available[0]
            print(f"[INFO] Defaulting to latest data: {latest_year}-{latest_month:02d}")
            pipeline.load_all_data(latest_year, latest_month)
            return pipeline

    print(f"[INFO] Loading data for Year={year}, Month={month}")
    pipeline.load_all_data(year, month)
    return pipeline


@cache_with_redis(ttl_seconds=300, prefix="analytics")
def get_analytics_cached(year: int | None = None, month: int | None = None):
    """Cache analytics computation for different timeframes using Redis."""
    pipeline = get_pipeline_for_request(year, month)
    return {
        "summary": pipeline.get_summary_stats(year, month),
        "state_data": pipeline.get_state_analytics(year, month),
        "pincode_data": pipeline.get_pincode_analytics(year, month),
        "temporal": pipeline.get_temporal_analytics(year, month),
    }


@app.get("/api/available-dates")
async def get_available_dates():
    """Get list of available Year-Month combinations for filtering."""
    try:
        data_path = (Path(__file__).parent.parent / "data").resolve()
        pipeline = AadhaarDataPipeline(str(data_path))
        dates = pipeline.get_available_months()
        # Convert to list of dicts for JSON
        return {
            "dates": [{"year": y, "month": m} for y, m in dates],
            "latest": {"year": dates[0][0], "month": dates[0][1]} if dates else None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        "documentation": "/docs",
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    try:
        pipeline = get_pipeline_for_request()
        return {
            "status": "healthy",
            "data_loaded": pipeline._bio_df is not None,
            "timestamp": time.time(),
        }
    except Exception as e:
        return JSONResponse(
            status_code=503, content={"status": "unhealthy", "error": str(e)}
        )


# ============================================================================
# SUMMARY & OVERVIEW
# ============================================================================


@app.get("/api/summary")
async def get_summary(
    year: Optional[int] = Query(None), month: Optional[int] = Query(None)
):
    """
    Get executive summary statistics.
    Returns: KPIs, totals, averages, top states
    """
    try:
        analytics = get_analytics_cached(year, month)
        summary = analytics["summary"]

        return {
            "metrics": {
                "total_bio_updates": summary["total_bio_updates"],
                "total_demo_updates": summary["total_demo_updates"],
                "total_enrolments": summary["total_enrolments"],
                "unique_pincodes": summary["unique_pincodes"],
                "unique_states": summary["unique_states"],
                "unique_districts": summary["unique_districts"],
            },
            "indices": {
                "avg_ivi": round(summary["avg_ivi"], 2),
                "avg_bsi": round(summary["avg_bsi"], 2),
            },
            "top_performers": {
                "top_state": summary["top_state"],
                "high_stress_state": summary["high_stress_state"],
            },
            "date_range": summary["date_range"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# STATE ANALYTICS
# ============================================================================


@app.get("/api/states")
async def get_all_states(
    year: Optional[int] = Query(None), month: Optional[int] = Query(None)
):
    """
    Get list of all states with basic metrics.
    Optimized for dropdown/selection.
    """
    try:
        analytics = get_analytics_cached(year, month)
        state_data = analytics["state_data"]

        states = []
        for _, row in state_data.iterrows():
            states.append(
                {
                    "name": row["state"],
                    "total_updates": int(row["total_updates"]),
                    "ivi": round(float(row["IVI"]), 2),
                    "bsi": round(float(row["BSI"]), 2),
                }
            )

        # Sort by total updates descending
        states.sort(key=lambda x: x["total_updates"], reverse=True)

        return {"states": states, "count": len(states)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/states/{state_name}")
async def get_state_detail(
    state_name: str,
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
):
    """
    Get detailed analytics for a specific state.
    """
    try:
        analytics = get_analytics_cached(year, month)
        state_data = analytics["state_data"]

        state_row = state_data[state_data["state"].str.lower() == state_name.lower()]

        if state_row.empty:
            raise HTTPException(
                status_code=404, detail=f"State '{state_name}' not found"
            )

        row = state_row.iloc[0]

        return {
            "state": row["state"],
            "biometric_updates": {
                "total": int(row["total_bio_updates"]),
                "youth_5_17": int(row["bio_age_5_17"]),
                "adult_17_plus": int(row["bio_age_17_"]),
            },
            "demographic_updates": {
                "total": int(row["total_demo_updates"]),
                "youth_5_17": int(row["demo_age_5_17"]),
                "adult_17_plus": int(row["demo_age_17_"]),
            },
            "enrolments": {
                "total": int(row["total_enrolments"]),
                "age_0_5": int(row["age_0_5"]),
                "age_5_17": int(row["age_5_17"]),
                "age_18_plus": int(row["age_18_greater"]),
            },
            "indices": {
                "ivi": round(float(row["IVI"]), 2),
                "bsi": round(float(row["BSI"]), 2),
                "youth_ratio": round(float(row["youth_ratio"]) * 100, 2),
                "stability_score": round(float(row["stability_score"]), 1),
            },
            "total_updates": int(row["total_updates"]),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/states/compare/{state1}/{state2}")
async def compare_states(
    state1: str,
    state2: str,
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
):
    """Compare two states side-by-side."""
    try:
        s1_data = await get_state_detail(state1, year, month)
        s2_data = await get_state_detail(state2, year, month)

        return {
            "state1": s1_data,
            "state2": s2_data,
            "comparison": {
                "ivi_diff": s1_data["indices"]["ivi"] - s2_data["indices"]["ivi"],
                "bsi_diff": s1_data["indices"]["bsi"] - s2_data["indices"]["bsi"],
                "update_diff": s1_data["total_updates"] - s2_data["total_updates"],
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CLUSTERING
# ============================================================================


@app.get("/api/clustering")
async def get_state_clustering(
    year: Optional[int] = Query(None), month: Optional[int] = Query(None)
):
    """
    Get state clustering analysis with PCA coordinates.
    """
    try:
        analytics = get_analytics_cached(year, month)
        state_data = analytics["state_data"]

        # Run clustering
        clusterer = StateClustering(n_clusters=4)
        clustered = clusterer.fit_predict(state_data)
        profiles = clusterer.get_cluster_profiles(clustered)

        # Prepare data for frontend
        clusters = []
        for _, row in clustered.iterrows():
            clusters.append(
                {
                    "state": row["state"],
                    "cluster": int(row["cluster"]),
                    "cluster_label": row["cluster_label"],
                    "pca_x": float(row["pca_x"]),
                    "pca_y": float(row["pca_y"]),
                    "total_updates": int(row["total_updates"]),
                    "ivi": round(float(row["IVI"]), 2),
                    "bsi": round(float(row["BSI"]), 2),
                }
            )

        # Cluster profiles
        cluster_summary = []
        for cluster_name, profile in profiles.items():
            cluster_summary.append(
                {
                    "id": int(cluster_name.split()[-1]),
                    "label": profile["label"],
                    "count": profile["count"],
                    "avg_ivi": round(profile["avg_IVI"], 2),
                    "avg_bsi": round(profile["avg_BSI"], 2),
                    "states": profile["states"][:10],  # Top 10
                }
            )

        return {"clusters": clusters, "profiles": cluster_summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ANOMALY DETECTION
# ============================================================================


@app.get("/api/anomalies")
async def get_anomalies(
    limit: int = Query(50, ge=1, le=1000),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
):
    """
    Get anomaly detection results.
    """
    try:
        analytics = get_analytics_cached(year, month)
        pincode_data = analytics["pincode_data"]

        detector = AnomalyDetector(contamination=0.05)
        anomalies = detector.detect_pincode_anomalies(pincode_data)

        # Get anomalous pincodes
        anomalous = anomalies[anomalies["is_anomaly"]].nlargest(limit, "anomaly_score")

        results = []
        for _, row in anomalous.iterrows():
            results.append(
                {
                    "pincode": int(row["pincode"]),
                    "state": row["state"],
                    "district": row["district"],
                    "anomaly_score": round(float(row["anomaly_score"]), 3),
                    "ivi": round(float(row["identity_velocity_index"]), 2),
                    "bsi": round(float(row["biometric_stress_index"]), 2),
                    "total_updates": int(row["total_updates"]),
                }
            )

        summary = detector.get_anomaly_summary(anomalies)

        return {
            "anomalies": results,
            "summary": {
                "total_anomalies": summary["anomaly_count"],
                "anomaly_percentage": round(summary["anomaly_percentage"], 2),
                "total_pincodes": summary["total_records"],
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# FORECASTING
# ============================================================================


@app.get("/api/forecast/{metric}")
async def get_forecast(
    metric: str = PathParam(..., pattern="^(bio|demo|enrol)$"),
    days: int = Query(30, ge=7, le=90),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
):
    """
    Get demand forecast for specified metric.
    Metrics: bio, demo, enrol
    """
    try:
        analytics = get_analytics_cached(year, month)
        temporal = analytics["temporal"]
        daily_data = temporal["daily"]

        # Map metric names
        metric_map = {
            "bio": "total_bio_updates",
            "demo": "total_demo_updates",
            "enrol": "total_enrolments",
        }
        target_col = metric_map[metric]

        forecaster = DemandForecaster(forecast_days=days)
        forecast_result = forecaster.forecast_with_prophet(daily_data, target_col)

        return {
            "metric": metric,
            "method": forecast_result["method"],
            "historical": forecast_result["historical"][:100],  # Last 100 days
            "forecast": forecast_result["forecast"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TEMPORAL TRENDS
# ============================================================================


@app.get("/api/trends/monthly")
async def get_monthly_trends(
    year: Optional[int] = Query(None), month: Optional[int] = Query(None)
):
    """Get monthly trend data for all metrics."""
    try:
        analytics = get_analytics_cached(year, month)
        temporal = analytics["temporal"]

        # Convert Period to string for JSON serialization
        bio_monthly = [(str(k), int(v)) for k, v in temporal["bio_monthly"].items()]
        demo_monthly = [(str(k), int(v)) for k, v in temporal["demo_monthly"].items()]
        enrol_monthly = [(str(k), int(v)) for k, v in temporal["enrol_monthly"].items()]

        return {
            "biometric": bio_monthly,
            "demographic": demo_monthly,
            "enrolment": enrol_monthly,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trends/daily")
async def get_daily_trends(
    limit: int = Query(90, ge=7, le=365),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
):
    """Get daily trend data (last N days)."""
    try:
        analytics = get_analytics_cached(year, month)
        temporal = analytics["temporal"]
        daily = temporal["daily"].tail(limit)

        trends = []
        for idx, row in daily.iterrows():
            # Date is a column, not index - handle both datetime and string
            date_val = row["date"]
            if hasattr(date_val, "strftime"):
                date_str = date_val.strftime("%Y-%m-%d")
            else:
                date_str = str(date_val)

            trends.append(
                {
                    "date": date_str,
                    "bio_updates": int(row["total_bio_updates"]),
                    "demo_updates": int(row["total_demo_updates"]),
                    "enrolments": int(row["total_enrolments"]),
                    "total_activity": int(row["total_activity"]),
                }
            )

        return {"trends": trends, "days": len(trends)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PINCODE ANALYTICS
# ============================================================================


@app.get("/api/pincodes/high-risk")
async def get_high_risk_pincodes(
    limit: int = Query(100, ge=1, le=1000),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
):
    """Get high-risk pincodes based on update probability."""
    try:
        analytics = get_analytics_cached(year, month)
        pincode_data = analytics["pincode_data"]

        predictor = IdentityLifecyclePredictor()
        risk_data = predictor.calculate_update_probability(pincode_data)
        high_priority = predictor.get_high_priority_pincodes(risk_data, top_n=limit)

        results = []
        for _, row in high_priority.iterrows():
            results.append(
                {
                    "pincode": int(row["pincode"]),
                    "state": row["state"],
                    "district": row["district"],
                    "risk_level": row["risk_level"],
                    "update_probability": round(float(row["update_probability"]), 3),
                    "ivi": round(float(row["identity_velocity_index"]), 2),
                    "bsi": round(float(row["biometric_stress_index"]), 2),
                    "total_updates": int(row["total_updates"]),
                }
            )

        return {"high_risk_pincodes": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SEARCH & FILTER
# ============================================================================


@app.get("/api/search/pincode/{pincode}")
async def search_pincode(
    pincode: int, year: Optional[int] = Query(None), month: Optional[int] = Query(None)
):
    """Search for specific pincode details."""
    try:
        analytics = get_analytics_cached(year, month)
        pincode_data = analytics["pincode_data"]

        result = pincode_data[pincode_data["pincode"] == pincode]

        if result.empty:
            raise HTTPException(status_code=404, detail=f"Pincode {pincode} not found")

        row = result.iloc[0]

        return {
            "pincode": int(row["pincode"]),
            "state": row["state"],
            "district": row["district"],
            "bio_updates": int(row["total_bio_updates"]),
            "demo_updates": int(row["total_demo_updates"]),
            "enrolments": int(row["total_enrolments"]),
            "ivi": round(float(row["identity_velocity_index"]), 2),
            "bsi": round(float(row["biometric_stress_index"]), 2),
            "youth_ratio": round(float(row["youth_update_ratio"]) * 100, 2),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CACHE MANAGEMENT
# ============================================================================

# ============================================================================
# AI CHAT ENDPOINT
# ============================================================================


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    stream: bool = True


class ChatMessage(BaseModel):
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = []


# Removed manual casual detection - let the LLM decide how to respond


async def stream_agent_response(
    agent_system, message: str, context: Dict[str, Any], history: List[Dict[str, str]]
):
    """Stream agent response with Chain-of-Thought."""
    try:
        # Add conversation history to context
        context["conversation_history"] = history[-10:]  # Last 10 messages
        print(
            f"[DEBUG BACKEND] Passing {len(context['conversation_history'])} messages to agent"
        )
        for i, msg in enumerate(context["conversation_history"]):
            print(
                f"[DEBUG BACKEND] History[{i}]: {msg['role']} - {msg['content'][:50]}..."
            )

        # Send thinking indicator
        yield f"data: {json.dumps({'type': 'thinking', 'content': 'Analyzing your question...'})}\n\n"
        await asyncio.sleep(0.1)

        # Get response with trace
        response, trace = agent_system.chat_with_agent(
            message, context, return_trace=True
        )

        # Stream trace steps (Chain-of-Thought)
        for step in trace:
            step_type = step.get("step", "unknown")

            if step_type == "TOOL_CALL":
                tool_name = step.get("tool", "unknown")
                args = step.get("args", {})
                yield f"data: {json.dumps({'type': 'tool_call', 'tool': tool_name, 'args': args})}\n\n"
                await asyncio.sleep(0.1)

            elif step_type == "TOOL_RESPONSE":
                tool_name = step.get("tool", "unknown")
                result = step.get("result", "")
                yield f"data: {json.dumps({'type': 'tool_result', 'tool': tool_name, 'result': result})}\n\n"
                await asyncio.sleep(0.1)

            elif step_type == "AI_RESPONSE":
                thinking = step.get("content", "")
                yield f"data: {json.dumps({'type': 'thinking', 'content': thinking})}\n\n"
                await asyncio.sleep(0.1)

        # Stream final response in chunks
        words = response.split()
        chunk_size = 5
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i : i + chunk_size])
            yield f"data: {json.dumps({'type': 'response', 'content': chunk + ' '})}\n\n"
            await asyncio.sleep(0.05)

        # Send completion
        yield f"data: {json.dumps({'type': 'done', 'full_response': response})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


@app.post("/api/ai/chat")
async def ai_chat(request: ChatRequest):
    """
    AI-powered chat assistant for Aadhaar data analysis.
    Uses NVIDIA NIM API with LangGraph agents, conversation memory, and streaming.
    Supports Chain-of-Thought display for complex queries.
    """
    try:
        # Import agents module
        from agents import LANGGRAPH_AVAILABLE, NVIDIA_AVAILABLE, AadhaarAgentSystem

        # Check if AI is available
        if not NVIDIA_AVAILABLE:
            return {
                "response": "❌ AI service is not available. NVIDIA AI Endpoints package is not installed.\n\nTo enable AI features, install: pip install langchain-nvidia-ai-endpoints",
                "status": "unavailable",
            }

        if not LANGGRAPH_AVAILABLE:
            return {
                "response": "❌ AI service is not available. LangGraph package is not installed.\n\nTo enable AI features, install: pip install langgraph langchain-core",
                "status": "unavailable",
            }

        # Check for API key
        api_key = os.getenv("NVIDIA_API_KEY")
        if not api_key:
            return {
                "response": "❌ NVIDIA API key is not configured.\n\nTo enable AI features:\n1. Get a free API key from https://build.nvidia.com/\n2. Set it in your .env file: NVIDIA_API_KEY=your-key-here\n3. Restart the backend",
                "status": "no_api_key",
            }

        # Generate or use provided session ID
        session_id = request.session_id or str(uuid.uuid4())

        # Get conversation database
        db = get_conversation_db()

        # Initialize agent system with data context
        pipeline = get_pipeline_for_request()
        analytics = get_analytics_cached()

        # Initialize agent with NVIDIA API key
        agent_system = AadhaarAgentSystem(nvidia_api_key=api_key)

        # Prepare context for agents
        context = {
            "summary_stats": analytics["summary"],
            "state_analytics": analytics["state_data"],
            "pincode_data": analytics["pincode_data"],
        }

        agent_system.set_context(context, pipeline)

        # If streaming disabled, return immediately
        if not request.stream:
            # Save user message to database
            db.add_message(session_id, "user", request.message)

            # Get fresh context for agent (without current message)
            context_history = db.get_recent_context(
                session_id, max_messages=MAX_HISTORY - 1
            )
            context["conversation_history"] = context_history

            response = agent_system.chat(request.message)

            # Save assistant response to database
            db.add_message(session_id, "assistant", response)

            return {"response": response, "session_id": session_id, "status": "success"}

        # For streaming requests, let LLM decide complexity and stream with Chain-of-Thought
        async def generate():
            full_response = ""

            # Get conversation context BEFORE adding current message
            context_history = db.get_recent_context(
                session_id, max_messages=MAX_HISTORY
            )
            context["conversation_history"] = context_history

            # Stream the response
            async for chunk in stream_agent_response(
                agent_system, request.message, context, context_history
            ):
                yield chunk
                # Extract full response from done event
                if '"type": "done"' in chunk:
                    try:
                        data = json.loads(chunk.replace("data: ", ""))
                        full_response = data.get("full_response", "")
                    except Exception:
                        pass

            # Save user message and assistant response to database
            db.add_message(session_id, "user", request.message)
            if full_response:
                db.add_message(session_id, "assistant", full_response)

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Session-ID": session_id,
            },
        )

    except Exception as e:
        print(f"[ERROR] AI Chat Error: {str(e)}")
        import traceback

        traceback.print_exc()

        return {
            "response": f"❌ An error occurred: {str(e)}\n\nPlease check the backend logs for details.",
            "status": "error",
        }


@app.get("/api/ai/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get conversation history for a session from database."""
    db = get_conversation_db()
    history = db.get_conversation_history(session_id)
    return {"session_id": session_id, "history": history, "message_count": len(history)}


@app.delete("/api/ai/history/{session_id}")
async def clear_chat_history(session_id: str):
    """Clear conversation history for a session from database."""
    db = get_conversation_db()
    db.clear_session(session_id)
    return {"status": "success", "message": "History cleared"}


@app.get("/api/ai/sessions")
async def get_active_sessions():
    """Get all active sessions."""
    db = get_conversation_db()
    sessions = db.get_all_sessions(active_only=True, days=7)
    return {"sessions": sessions, "count": len(sessions)}


@app.post("/api/ai/cleanup")
async def cleanup_old_sessions(days: int = 30):
    """Clean up sessions older than specified days."""
    db = get_conversation_db()
    deleted = db.cleanup_old_sessions(days)
    return {"status": "success", "deleted_sessions": deleted}


@app.post("/api/cache/clear")
async def clear_cache():
    """Clear all caches (admin endpoint)."""
    get_pipeline_for_request.cache_clear()

    # Clear Redis keys with 'analytics' prefix
    cleared_count = redis_cache.clear_pattern("analytics:*")

    return {
        "status": "cache_cleared",
        "timestamp": time.time(),
        "redis_keys_cleared": cleared_count,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
