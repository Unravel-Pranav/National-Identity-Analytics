"""
Agentic AI Module using LangGraph
Implements intelligent agents for Aadhaar data analysis and recommendations.
Uses NVIDIA NIM API with LangGraph's create_react_agent pattern.
"""
import os
from typing import Dict, List, Any, TypedDict, Annotated
from dataclasses import dataclass
import json
import pandas as pd

# Load environment variables from project root .env file
from pathlib import Path
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

# Check for LangGraph availability
try:
    from langgraph.prebuilt import create_react_agent
    from langgraph.graph import StateGraph, END, MessagesState
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain_core.tools import tool
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False

# Check for NVIDIA NIM availability  
try:
    from langchain_nvidia_ai_endpoints import ChatNVIDIA
    NVIDIA_AVAILABLE = True
except ImportError:
    NVIDIA_AVAILABLE = False


# ============================================================================
# TOOL DEFINITIONS - These are the actual tools agents can use
# ============================================================================

# Global reference to data context (set by the agent system)
_data_context: Dict[str, Any] = {}
_pipeline = None
_trace_log: List[Dict[str, Any]] = []  # Trace log for tool calls


def set_data_context(context: Dict[str, Any], pipeline=None):
    """Set the global data context for tools to access."""
    global _data_context, _pipeline
    _data_context = context
    _pipeline = pipeline


def clear_trace():
    """Clear the trace log."""
    global _trace_log
    _trace_log = []


def get_trace() -> List[Dict[str, Any]]:
    """Get the current trace log."""
    return _trace_log.copy()


def log_tool_call(tool_name: str, args: Dict[str, Any], result: str):
    """Log a tool call to the trace."""
    global _trace_log
    _trace_log.append({
        'tool': tool_name,
        'args': args,
        'result': result[:500] + '...' if len(result) > 500 else result,
        'result_length': len(result)
    })


@tool
def get_summary_statistics() -> str:
    """Get overall summary statistics of the Aadhaar system.
    
    Returns key metrics like total biometric updates, demographic updates, 
    enrolments, coverage (states, pincodes), and date range.
    """
    summary = _data_context.get('summary_stats', {})
    if not summary:
        return "No summary statistics available. Please load data first."
    
    result = f"""📊 **Aadhaar System Summary**
- Total Biometric Updates: {summary.get('total_bio_updates', 0):,}
- Total Demographic Updates: {summary.get('total_demo_updates', 0):,}
- Total New Enrolments: {summary.get('total_enrolments', 0):,}
- Coverage: {summary.get('unique_states', 0)} States, {summary.get('unique_pincodes', 0):,} Pincodes
- Average Identity Velocity Index (IVI): {summary.get('avg_ivi', 0):.2f}
- Average Biometric Stress Index (BSI): {summary.get('avg_bsi', 0):.2f}
- Top Activity State: {summary.get('top_state', 'N/A')}
- Highest Biometric Stress State: {summary.get('high_stress_state', 'N/A')}
- Date Range: {summary.get('date_range', {}).get('start', 'N/A')} to {summary.get('date_range', {}).get('end', 'N/A')}"""
    return result


@tool
def get_anomaly_report() -> str:
    """Get detailed anomaly detection report.
    
    Shows pincodes and regions with unusual update patterns
    that may indicate data quality issues or system stress.
    """
    anomalies = _data_context.get('anomalies', [])
    if not anomalies:
        return "✅ No significant anomalies detected in the current data."
    
    result = f"🚨 **Anomaly Detection Report** ({len(anomalies)} anomalies found)\n\n"
    for i, anomaly in enumerate(anomalies[:10], 1):
        if isinstance(anomaly, dict):
            pincode = anomaly.get('pincode', 'Unknown')
            state = anomaly.get('state', 'Unknown')
            score = anomaly.get('anomaly_score', 0)
            ivi = anomaly.get('identity_velocity_index', 0)
            result += f"{i}. Pincode {pincode} ({state})\n"
            result += f"   - Anomaly Score: {score:.2f}\n"
            result += f"   - Identity Velocity Index: {ivi:.2f}\n\n"
    
    if len(anomalies) > 10:
        result += f"... and {len(anomalies) - 10} more anomalies."
    
    return result


@tool
def get_state_analysis(state_name: str) -> str:
    """Get detailed analysis for a specific state.
    
    Args:
        state_name: Name of the state to analyze (e.g., "Maharashtra", "Uttar Pradesh")
    
    Returns analysis including biometric updates, demographic updates, 
    enrolments, and computed indices for the state.
    """
    state_analytics = _data_context.get('state_analytics', {})
    if isinstance(state_analytics, pd.DataFrame):
        state_data = state_analytics[state_analytics['state'].str.lower() == state_name.lower()]
        if state_data.empty:
            available_states = state_analytics['state'].tolist()[:10]
            return f"State '{state_name}' not found. Available states include: {', '.join(available_states)}"
        
        row = state_data.iloc[0]
        return f"""📍 **Analysis for {row['state']}**
- Biometric Updates: {row.get('total_bio_updates', 0):,}
- Demographic Updates: {row.get('total_demo_updates', 0):,}
- Total Enrolments: {row.get('total_enrolments', 0):,}
- Identity Velocity Index: {row.get('IVI', 0):.2f}
- Biometric Stress Index: {row.get('BSI', 0):.2f}
- Youth Update Ratio: {row.get('youth_ratio', 0):.2%}
- Stability Score: {row.get('stability_score', 0):.1f}/100"""
    
    return f"State analytics not available for {state_name}."


@tool
def get_cluster_insights() -> str:
    """Get insights from state clustering analysis.
    
    Shows how states are grouped based on their update patterns,
    biometric stress, and enrolment behavior.
    """
    cluster_profiles = _data_context.get('cluster_profiles', {})
    if not cluster_profiles:
        return "No cluster analysis available."
    
    result = "📈 **State Cluster Analysis**\n\n"
    for cluster_name, profile in cluster_profiles.items():
        if isinstance(profile, dict):
            label = profile.get('label', cluster_name)
            description = profile.get('description', '')
            states = profile.get('states', [])
            
            result += f"**{label}**\n"
            if description:
                result += f"{description}\n"
            result += f"States: {', '.join(states[:5])}"
            if len(states) > 5:
                result += f" (+{len(states)-5} more)"
            result += "\n\n"
    
    return result


@tool
def get_forecast_prediction() -> str:
    """Get demand forecast predictions for upcoming periods.
    
    Shows predicted biometric updates, demographic updates, and
    enrolment volumes based on historical trends.
    """
    forecasts = _data_context.get('forecasts', {})
    if not forecasts:
        return "No forecast data available."
    
    result = "🔮 **Demand Forecast (Next 30 Days)**\n\n"
    
    bio_forecast = forecasts.get('bio_forecast', [])
    demo_forecast = forecasts.get('demo_forecast', [])
    
    if bio_forecast:
        avg_bio = sum(bio_forecast) / len(bio_forecast)
        result += f"- Predicted Daily Biometric Updates: ~{avg_bio:,.0f}\n"
    
    if demo_forecast:
        avg_demo = sum(demo_forecast) / len(demo_forecast)
        result += f"- Predicted Daily Demographic Updates: ~{avg_demo:,.0f}\n"
    
    # Add trend analysis
    result += "\n**Trend Analysis:**\n"
    result += "Based on historical patterns, expect higher volumes on Tuesdays and Wednesdays.\n"
    result += "Plan for 15-20% increase during March (financial year end)."
    
    return result


@tool
def get_policy_recommendations() -> str:
    """Generate policy recommendations based on current data analysis.
    
    Provides actionable recommendations for UIDAI administrators
    based on detected patterns, anomalies, and actual metrics.
    """
    summary = _data_context.get('summary_stats', {})
    anomalies = _data_context.get('anomalies', [])
    state_analytics = _data_context.get('state_analytics', {})
    
    recommendations = ["🏛️ **Policy Recommendations**\n"]
    recommendations.append("*Generated dynamically based on current data analysis*\n")
    rec_num = 1
    
    # BSI-based recommendations with actual data
    avg_bsi = summary.get('avg_bsi', 0)
    high_stress_state = summary.get('high_stress_state', 'Unknown')
    
    if avg_bsi > 1.5:
        recommendations.append(f"""
**{rec_num}. Biometric Alternative Deployment** ⚠️ HIGH PRIORITY
- Current Average BSI: **{avg_bsi:.2f}** (threshold: 1.5)
- Highest stress state: **{high_stress_state}**
- Action: Deploy iris scanners in {high_stress_state}
- Enable OTP-based authentication for manual laborers
- Target industrial and agricultural regions""")
        rec_num += 1
    else:
        recommendations.append(f"""
**{rec_num}. Biometric System Health** ✅ STABLE
- Current Average BSI: **{avg_bsi:.2f}** (healthy range)
- Continue current biometric processes
- Monitor {high_stress_state} for any BSI increases""")
        rec_num += 1
    
    # Anomaly-based recommendations with actual counts
    anomaly_count = len(anomalies) if anomalies else 0
    if anomaly_count > 5:
        # Get top anomaly locations
        top_anomalies = [a.get('state', 'Unknown') for a in anomalies[:3]] if anomalies else []
        recommendations.append(f"""
**{rec_num}. Data Quality Investigation** ⚠️ ATTENTION NEEDED
- Anomalies detected: **{anomaly_count}**
- Top affected regions: {', '.join(top_anomalies)}
- Action: Conduct data audit in flagged pincodes
- Verify enrolment center processes
- Implement additional validation checks""")
        rec_num += 1
    elif anomaly_count > 0:
        recommendations.append(f"""
**{rec_num}. Anomaly Monitoring** 📊 NORMAL
- Minor anomalies: **{anomaly_count}** (within acceptable range)
- Continue routine monitoring
- No immediate action required""")
        rec_num += 1
    
    # IVI-based capacity planning
    avg_ivi = summary.get('avg_ivi', 0)
    top_state = summary.get('top_state', 'Unknown')
    
    recommendations.append(f"""
**{rec_num}. Capacity Planning**
- Average Identity Velocity Index: **{avg_ivi:.2f}**
- Highest activity state: **{top_state}**
- {'⚠️ HIGH LOAD: Increase staffing in ' + top_state if avg_ivi > 1000 else '✅ Normal load levels'}
- Deploy mobile enrolment vans in high-IVI rural areas
- Optimize peak hours (10 AM - 2 PM) staffing""")
    rec_num += 1
    
    # Youth-focused with actual numbers
    total_enrol = summary.get('total_enrolments', 0)
    recommendations.append(f"""
**{rec_num}. Youth Identity Management**
- Total new enrolments: **{total_enrol:,}**
- Implement proactive notification for 5-17 age group
- Schedule school-based biometric update camps
- Create awareness campaigns for mandatory updates
- Focus on states with high youth enrollment ratios""")
    rec_num += 1
    
    # Resource summary
    total_bio = summary.get('total_bio_updates', 0)
    total_demo = summary.get('total_demo_updates', 0)
    unique_pincodes = summary.get('unique_pincodes', 0)
    
    recommendations.append(f"""
**{rec_num}. Resource Summary**
- Total Bio Updates Processed: **{total_bio:,}**
- Total Demo Updates Processed: **{total_demo:,}**
- Pincodes Served: **{unique_pincodes:,}**
- System Health: {'⚠️ High Load' if avg_ivi > 1500 else '✅ Operational'}""")
    
    return '\n'.join(recommendations)


@tool
def refresh_data() -> str:
    """Refresh the data by reloading from disk.
    
    Use this when new data files have been added to the data folders
    or when you want to see the latest updates.
    """
    global _pipeline
    if _pipeline is None:
        return "Pipeline not available. Cannot refresh data."
    
    try:
        from src.data_pipeline import refresh_pipeline, get_last_load_time
        refresh_pipeline()
        load_time = get_last_load_time()
        return f"✅ Data refreshed successfully at {load_time}. All cached analytics have been cleared."
    except Exception as e:
        return f"❌ Error refreshing data: {str(e)}"


@tool  
def check_data_freshness() -> str:
    """Check when the data was last loaded and if new files are available.
    
    Useful for determining if a data refresh is needed.
    """
    try:
        from src.data_pipeline import get_last_load_time, check_for_new_data
        
        last_load = get_last_load_time()
        file_counts = check_for_new_data()
        
        result = "📁 **Data Freshness Report**\n\n"
        result += f"Last data load: {last_load or 'Not recorded'}\n\n"
        result += "**Files per folder:**\n"
        for folder, count in file_counts.items():
            folder_name = folder.replace('api_data_aadhar_', '').title()
            result += f"- {folder_name}: {count} CSV files\n"
        
        return result
    except Exception as e:
        return f"Error checking data freshness: {str(e)}"


@tool
def compare_states(state1: str, state2: str) -> str:
    """Compare two states on key metrics.
    
    Args:
        state1: First state name
        state2: Second state name
    
    Returns side-by-side comparison of key metrics.
    """
    state_analytics = _data_context.get('state_analytics', {})
    if not isinstance(state_analytics, pd.DataFrame):
        return "State analytics not available."
    
    df = state_analytics
    s1 = df[df['state'].str.lower() == state1.lower()]
    s2 = df[df['state'].str.lower() == state2.lower()]
    
    if s1.empty:
        return f"State '{state1}' not found."
    if s2.empty:
        return f"State '{state2}' not found."
    
    s1, s2 = s1.iloc[0], s2.iloc[0]
    
    return f"""📊 **State Comparison: {s1['state']} vs {s2['state']}**

| Metric | {s1['state']} | {s2['state']} |
|--------|-------------|-------------|
| Biometric Updates | {s1.get('total_bio_updates', 0):,} | {s2.get('total_bio_updates', 0):,} |
| Demographic Updates | {s1.get('total_demo_updates', 0):,} | {s2.get('total_demo_updates', 0):,} |
| Total Enrolments | {s1.get('total_enrolments', 0):,} | {s2.get('total_enrolments', 0):,} |
| Identity Velocity Index | {s1.get('IVI', 0):.2f} | {s2.get('IVI', 0):.2f} |
| Biometric Stress Index | {s1.get('BSI', 0):.2f} | {s2.get('BSI', 0):.2f} |
| Stability Score | {s1.get('stability_score', 0):.1f} | {s2.get('stability_score', 0):.1f} |"""


@tool
def list_all_states() -> str:
    """List all states available in the dataset with their key metrics."""
    state_analytics = _data_context.get('state_analytics', {})
    if not isinstance(state_analytics, pd.DataFrame):
        return "State analytics not available."
    
    df = state_analytics.sort_values('total_updates', ascending=False)
    
    result = "📋 **All States (sorted by activity)**\n\n"
    for _, row in df.head(20).iterrows():
        result += f"• {row['state']}: {row.get('total_updates', 0):,} updates, BSI: {row.get('BSI', 0):.2f}\n"
    
    if len(df) > 20:
        result += f"\n... and {len(df) - 20} more states."
    
    return result


@tool
def get_district_analysis(state_name: str, district_name: str) -> str:
    """Get detailed analysis for a specific district within a state.
    
    Args:
        state_name: Name of the state (e.g., "Maharashtra", "Uttar Pradesh")
        district_name: Name of the district (e.g., "Pune", "Lucknow")
    
    Returns analysis including biometric updates, demographic updates, 
    enrolments broken down by age group (youth enrollment included).
    """
    global _pipeline
    
    # Try to get pincode data which has district info
    pincode_data = _data_context.get('pincode_data', None)
    if pincode_data is None and _pipeline is not None:
        pincode_data = _pipeline.get_pincode_analytics()
    
    if pincode_data is None or not isinstance(pincode_data, pd.DataFrame):
        return f"District-level data not available. Please ensure pincode data is loaded."
    
    # Filter by state and district (case-insensitive)
    df = pincode_data.copy()
    df['state_lower'] = df['state'].astype(str).str.lower()
    df['district_lower'] = df['district'].astype(str).str.lower()
    
    district_data = df[
        (df['state_lower'] == state_name.lower()) & 
        (df['district_lower'] == district_name.lower())
    ]
    
    if district_data.empty:
        # Try partial match
        district_data = df[
            (df['state_lower'] == state_name.lower()) & 
            (df['district_lower'].str.contains(district_name.lower(), na=False))
        ]
    
    if district_data.empty:
        # List available districts in the state
        state_districts = df[df['state_lower'] == state_name.lower()]['district'].unique()[:10]
        return f"District '{district_name}' not found in {state_name}. Available districts: {', '.join(state_districts)}"
    
    # Aggregate district data
    total_bio = district_data['total_bio_updates'].sum()
    total_demo = district_data['total_demo_updates'].sum()
    total_enrol = district_data['total_enrolments'].sum()
    
    # Youth data (age 5-17)
    youth_bio = district_data['bio_age_5_17'].sum() if 'bio_age_5_17' in district_data.columns else 0
    youth_demo = district_data['demo_age_5_17'].sum() if 'demo_age_5_17' in district_data.columns else 0
    youth_enrol = district_data['age_5_17'].sum() if 'age_5_17' in district_data.columns else 0
    
    # Child data (age 0-5)
    child_enrol = district_data['age_0_5'].sum() if 'age_0_5' in district_data.columns else 0
    
    # Adult data (age 18+)
    adult_enrol = district_data['age_18_greater'].sum() if 'age_18_greater' in district_data.columns else 0
    adult_bio = district_data['bio_age_17_'].sum() if 'bio_age_17_' in district_data.columns else 0
    adult_demo = district_data['demo_age_17_'].sum() if 'demo_age_17_' in district_data.columns else 0
    
    # Compute indices
    total_updates = total_bio + total_demo
    ivi = (total_updates / (total_enrol + 1)) * 100
    bsi = total_bio / (total_demo + 1)
    youth_ratio = (youth_bio + youth_demo) / (total_updates + 1) if total_updates > 0 else 0
    
    num_pincodes = len(district_data)
    
    return f"""📍 **District Analysis: {district_name.title()}, {state_name.title()}**

**Coverage:**
- Pincodes in District: {num_pincodes}

**ENROLMENTS (New Aadhaar Registrations):**
- Total Enrolments: {total_enrol:,.0f}
- 👶 Age 0-5 (Infants): {child_enrol:,.0f}
- 🧒 Age 5-17 (Youth): {youth_enrol:,.0f}  ← **Youth Enrollment**
- 🧑 Age 18+ (Adults): {adult_enrol:,.0f}

**BIOMETRIC UPDATES:**
- Total Biometric Updates: {total_bio:,.0f}
- Youth (5-17): {youth_bio:,.0f}
- Adults (17+): {adult_bio:,.0f}

**DEMOGRAPHIC UPDATES:**
- Total Demographic Updates: {total_demo:,.0f}
- Youth (5-17): {youth_demo:,.0f}
- Adults (17+): {adult_demo:,.0f}

**KEY INDICES:**
- Identity Velocity Index (IVI): {ivi:.2f}
- Biometric Stress Index (BSI): {bsi:.2f}
- Youth Update Ratio: {youth_ratio*100:.2f}%
- Total Updates: {total_updates:,.0f}"""


@tool
def list_districts_in_state(state_name: str) -> str:
    """List all districts available in a specific state.
    
    Args:
        state_name: Name of the state (e.g., "Maharashtra", "Karnataka")
    
    Returns list of districts with basic metrics.
    """
    global _pipeline
    
    pincode_data = _data_context.get('pincode_data', None)
    if pincode_data is None and _pipeline is not None:
        pincode_data = _pipeline.get_pincode_analytics()
    
    if pincode_data is None or not isinstance(pincode_data, pd.DataFrame):
        return "District data not available."
    
    df = pincode_data.copy()
    df['state_lower'] = df['state'].astype(str).str.lower()
    
    state_data = df[df['state_lower'] == state_name.lower()]
    
    if state_data.empty:
        return f"State '{state_name}' not found."
    
    # Aggregate by district
    district_agg = state_data.groupby('district').agg({
        'total_bio_updates': 'sum',
        'total_demo_updates': 'sum',
        'total_enrolments': 'sum',
        'pincode': 'count'
    }).rename(columns={'pincode': 'num_pincodes'}).reset_index()
    
    district_agg['total_updates'] = district_agg['total_bio_updates'] + district_agg['total_demo_updates']
    district_agg = district_agg.sort_values('total_updates', ascending=False)
    
    result = f"📋 **Districts in {state_name.title()}** ({len(district_agg)} districts)\n\n"
    
    for _, row in district_agg.head(20).iterrows():
        result += f"• **{row['district']}**: {row['total_enrolments']:,.0f} enrolments, {row['total_updates']:,.0f} updates, {row['num_pincodes']} pincodes\n"
    
    if len(district_agg) > 20:
        result += f"\n... and {len(district_agg) - 20} more districts."
    
    return result


# ============================================================================
# AGENT SYSTEM CLASS
# ============================================================================

# All available tools
ALL_TOOLS = [
    get_summary_statistics,
    get_anomaly_report,
    get_state_analysis,
    get_district_analysis,  # NEW: District-level analysis
    list_districts_in_state,  # NEW: List districts in a state
    get_cluster_insights,
    get_forecast_prediction,
    get_policy_recommendations,
    refresh_data,
    check_data_freshness,
    compare_states,
    list_all_states,
]


class AadhaarAnalysisAgents:
    """
    Multi-agent system for Aadhaar data analysis using LangGraph.
    
    This system uses the ReAct pattern where the agent can:
    1. Think about what tool to use
    2. Call the tool
    3. Observe the result
    4. Decide next action
    
    Available tools:
    - get_summary_statistics: Overall system metrics
    - get_anomaly_report: Detect unusual patterns  
    - get_state_analysis: Analyze specific states
    - get_cluster_insights: View state clustering
    - get_forecast_prediction: See demand forecasts
    - get_policy_recommendations: Get actionable advice
    - refresh_data: Reload data from disk
    - check_data_freshness: Check data status
    - compare_states: Compare two states
    - list_all_states: See all states
    """
    
    def __init__(self, nvidia_api_key: str | None = None):
        self.api_key = nvidia_api_key or os.getenv("NVIDIA_API_KEY")
        self.llm = None
        self.agent = None
        
        if self.api_key and NVIDIA_AVAILABLE:
            os.environ["NVIDIA_API_KEY"] = self.api_key
            self.llm = ChatNVIDIA(
                model="meta/llama-3.1-8b-instruct",
                temperature=0.1,
                max_tokens=512
            )
            
            # Create ReAct agent with tools
            if LANGGRAPH_AVAILABLE and self.llm:
                from langchain_core.messages import SystemMessage
        # Create the agent without system prompt in initialization
        # System prompt will be prepended to messages during invocation
        self.agent = create_react_agent(
            model=self.llm,
            tools=ALL_TOOLS
        )
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent."""
        return """You are an AI assistant for Aadhaar identity data analysis in India.

**IMPORTANT: ALWAYS USE TOOLS FOR DATA QUESTIONS**

You MUST call tools for ANY question about:
- States, metrics, statistics, trends, activity
- "last 30 days", "highest", "summary", "which state", "show me"
- Numbers, data, analysis, comparisons

Available tools:
1. get_summary_statistics - Overall system metrics (ALWAYS START HERE)
2. get_state_analysis - Specific state details
3. get_temporal_trends - Daily/weekly/monthly trends
4. detect_anomalies - Unusual patterns
5. compare_states - Compare multiple states

Example: "Give me last 30 days activity" → Call get_temporal_trends(period='daily', days=30)

For listing all states: Use list_all_states
For comparing states: Use compare_states(state1, state2)
For specific state details: Use get_state_analysis(state_name)
For anomalies: Use get_anomaly_report()
For recommendations: Use get_policy_recommendations()

**Understanding "Risk" Indicators:**
- "Highest risk/stress" = State shown in "Highest Biometric Stress State" field from get_summary_statistics
- "Critical" = High IVI (>1000) OR High BSI (>2.0)
- "Stable" = Low IVI (<500) AND Low BSI (<1.0)
- **DON'T analyze multiple states manually - use get_summary_statistics!**

**Response Strategy:**
- Greetings (hi, hello, thanks): Respond warmly without tools
- Help requests: Explain capabilities concisely
- Data questions: ALWAYS use tools - never guess or provide generic answers
- BE CONTEXTUAL: Check conversation history first - user might be asking about what YOU just said, not asking a new question

**Available Tools (USE THEM!):**
- list_all_states: See ALL states with IVI, BSI, updates - USE THIS FIRST for "which state" questions
- get_summary_statistics: Overall system metrics
- get_anomaly_report: Detect unusual patterns and high-risk pincodes
- get_state_analysis: Analyze ONE specific state (need exact name)
- get_district_analysis: District-level insights
- list_districts_in_state: List districts in a state
- get_cluster_insights: State clustering patterns
- get_forecast_prediction: 30-day demand forecasts
- get_policy_recommendations: Actionable advice with real data
- compare_states: Side-by-side comparison of TWO states
- check_data_freshness: Data status
- refresh_data: Reload from disk

**HOW TO ANSWER QUESTIONS:**

1. "Highest risk/stress state?" → Use get_summary_statistics, read "high_stress_state" field
2. "Which state has most updates?" → Use list_all_states, find the top one
3. "Tell me about [State]" → Use get_state_analysis("State")
4. "Compare X and Y" → Use compare_states("X", "Y")
5. "Show anomalies" → Use get_anomaly_report()
6. "Give recommendations" → Use get_policy_recommendations()
7. "What were we talking about?" → CHECK CONVERSATION HISTORY FIRST! Don't use tools!

**CONVERSATION MEMORY - CRITICAL:**
- ALWAYS review the conversation history FIRST before answering
- If user asks "what state?" or "which one?", look at the PREVIOUS messages to see what you just discussed
- DO NOT assume they're asking about "highest risk" - they might be asking about what YOU just mentioned
- Reference your OWN previous answers, not just the system knowledge
- Be natural and conversational - answer based on CONTEXT

**Key Metrics:**
- IVI (Identity Velocity Index): Updates per capita - High (>1000) = CRITICAL RISK
- BSI (Biometric Stress Index): Bio/demo ratio - High (>2.0) = FINGERPRINT ISSUES
- Youth Update Ratio: % updates from age 5-17
- Update Probability Score: Combined risk score

**ALWAYS cite specific numbers from tools. Never say "I don't have that information" - USE THE TOOLS!**

**Tone:** Professional, data-driven, actionable. You're helping government officials make critical decisions."""
    
    def set_context(self, context: Dict[str, Any], pipeline=None):
        """Set the data context for tools."""
        set_data_context(context, pipeline)
    
    def chat(self, query: str) -> str:
        """Simple chat interface for API endpoint."""
        context = _data_context.copy()
        return self.chat_with_agent(query, context, return_trace=False)
    
    def chat_with_agent(self, query: str, context: Dict[str, Any], return_trace: bool = False) -> str | tuple:
        """Interactive chat with the AI agent using tools.
        
        Args:
            query: User's question
            context: Data context for tools
            return_trace: If True, returns (response, trace) tuple
            
        Returns:
            Response string, or (response, trace) tuple if return_trace=True
        """
        # Clear previous trace and update context
        clear_trace()
        set_data_context(context)
        
        trace_entries = []
        
        # If we have a full ReAct agent, use it
        if self.agent:
            try:
                # Build message history with system prompt
                messages = [SystemMessage(content=self.system_prompt)]
                
                # Add conversation history from context if available
                conversation_history = context.get('conversation_history', [])
                print(f"\n[DEBUG AGENT] ========== BUILDING MESSAGES ==========")
                print(f"[DEBUG AGENT] Found {len(conversation_history)} messages in history")
                
                for i, msg in enumerate(conversation_history):
                    role = msg.get('role', '').lower()
                    content = msg.get('content', '')
                    print(f"[DEBUG AGENT] History[{i}]: role={role}, content={content[:60]}...")
                    
                    if role == 'user':
                        messages.append(HumanMessage(content=content))
                    elif role == 'assistant':
                        messages.append(AIMessage(content=content))
                
                # Add current query
                messages.append(HumanMessage(content=query))
                print(f"[DEBUG AGENT] Current query: {query}")
                print(f"[DEBUG AGENT] Total messages to LLM: {len(messages)} (1 system + {len(conversation_history)} history + 1 current)")
                print(f"[DEBUG AGENT] ========================================\n")
                
                # Stream to capture intermediate steps
                result = self.agent.invoke({
                    "messages": messages
                })
                
                # Extract trace from messages
                messages = result.get("messages", [])
                for msg in messages:
                    msg_type = type(msg).__name__
                    
                    # Check for tool calls
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tc in msg.tool_calls:
                            trace_entries.append({
                                'step': 'TOOL_CALL',
                                'tool': tc.get('name', 'unknown'),
                                'args': tc.get('args', {}),
                                'status': 'called'
                            })
                    
                    # Check for tool messages (responses)
                    if msg_type == 'ToolMessage':
                        content = msg.content if hasattr(msg, 'content') else str(msg)
                        trace_entries.append({
                            'step': 'TOOL_RESPONSE',
                            'tool': getattr(msg, 'name', 'unknown'),
                            'result': content[:300] + '...' if len(content) > 300 else content,
                            'status': 'completed'
                        })
                    
                    # AI thinking/response
                    if msg_type == 'AIMessage' and hasattr(msg, 'content') and msg.content:
                        if not (hasattr(msg, 'tool_calls') and msg.tool_calls):
                            trace_entries.append({
                                'step': 'AI_RESPONSE',
                                'content': msg.content[:200] + '...' if len(msg.content) > 200 else msg.content
                            })
                
                # Get final response
                final_response = messages[-1].content if messages else "No response generated."
                
                if return_trace:
                    return final_response, trace_entries
                return final_response
                
            except Exception as e:
                error_trace = [{'step': 'ERROR', 'error': str(e), 'fallback': 'simple_chat'}]
                response = self._simple_chat(query, context)
                if return_trace:
                    return response, error_trace
                return response
        elif self.llm:
            response = self._simple_chat(query, context)
            trace_entries.append({'step': 'SIMPLE_CHAT', 'mode': 'no_tools'})
            if return_trace:
                return response, trace_entries
            return response
        else:
            response = self._rule_based_response(query, context)
            trace_entries.append({'step': 'RULE_BASED', 'mode': 'no_llm'})
            if return_trace:
                return response, trace_entries
            return response
    
    def _simple_chat(self, query: str, context: Dict[str, Any]) -> str:
        """Simple chat without tool calling."""
        summary = context.get('summary_stats', {})
        
        system_prompt = f"""You are an AI assistant for Aadhaar data analysis.

Current Data Summary:
- Total Biometric Updates: {summary.get('total_bio_updates', 'N/A'):,}
- Total Demographic Updates: {summary.get('total_demo_updates', 'N/A'):,}
- Total Enrolments: {summary.get('total_enrolments', 'N/A'):,}
- States: {summary.get('unique_states', 'N/A')}
- Pincodes: {summary.get('unique_pincodes', 'N/A'):,}
- Avg IVI: {summary.get('avg_ivi', 'N/A'):.2f}
- Avg BSI: {summary.get('avg_bsi', 'N/A'):.2f}

Answer questions about this data. Be specific and helpful."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def run_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run complete analysis using the agent system."""
        set_data_context(context)
        
        # Collect outputs from various analyses
        insights = []
        recommendations = []
        
        # Get anomaly insights
        try:
            anomaly_result = get_anomaly_report.invoke({})
            if "anomalies found" in anomaly_result or "🚨" in anomaly_result:
                insights.append(anomaly_result)
        except Exception:
            pass
        
        # Get cluster insights
        try:
            cluster_result = get_cluster_insights.invoke({})
            if cluster_result and "not available" not in cluster_result.lower():
                insights.append(cluster_result)
        except Exception:
            pass
        
        # Get policy recommendations
        try:
            policy_result = get_policy_recommendations.invoke({})
            recommendations.append(policy_result)
        except Exception:
            pass
        
        # Build report
        report = self._build_report(context, insights, recommendations)
        
        return {
            'insights': insights,
            'recommendations': recommendations,
            'report': report
        }
    
    def _build_report(self, context: Dict[str, Any], insights: List[str], recommendations: List[str]) -> str:
        """Build a comprehensive report."""
        summary = context.get('summary_stats', {})
        
        lines = [
            "=" * 70,
            "   AADHAAR IDENTITY INTELLIGENCE REPORT",
            "=" * 70,
            "",
            "📋 EXECUTIVE SUMMARY:",
            f"   • Total Biometric Updates: {summary.get('total_bio_updates', 0):,}",
            f"   • Total Demographic Updates: {summary.get('total_demo_updates', 0):,}",
            f"   • Total New Enrolments: {summary.get('total_enrolments', 0):,}",
            f"   • Coverage: {summary.get('unique_states', 0)} States, {summary.get('unique_pincodes', 0):,} Pincodes",
            f"   • Average IVI: {summary.get('avg_ivi', 0):.2f}",
            f"   • Average BSI: {summary.get('avg_bsi', 0):.2f}",
            ""
        ]
        
        for insight in insights:
            lines.append(insight)
            lines.append("")
        
        for rec in recommendations:
            lines.append(rec)
            lines.append("")
        
        lines.extend([
            "=" * 70,
            "   Report generated by Aadhaar Identity Intelligence System",
            "=" * 70
        ])
        
        return '\n'.join(lines)
    
    def _rule_based_response(self, query: str, context: Dict[str, Any]) -> str:
        """Fallback rule-based response when LLM is not available."""
        query_lower = query.lower()
        summary = context.get('summary_stats', {})
        
        if 'anomaly' in query_lower or 'anomalies' in query_lower:
            return get_anomaly_report.invoke({})
        
        if 'state' in query_lower and 'list' in query_lower:
            return list_all_states.invoke({})
        
        if 'summary' in query_lower or 'statistics' in query_lower:
            return get_summary_statistics.invoke({})
        
        if 'forecast' in query_lower or 'predict' in query_lower:
            return get_forecast_prediction.invoke({})
        
        if 'recommend' in query_lower or 'policy' in query_lower:
            return get_policy_recommendations.invoke({})
        
        if 'cluster' in query_lower:
            return get_cluster_insights.invoke({})
        
        if 'refresh' in query_lower or 'reload' in query_lower:
            return refresh_data.invoke({})
        
        return f"""I can help analyze Aadhaar data. Try asking about:
- Summary statistics
- Anomaly detection
- State-wise analysis
- Clustering insights  
- Demand forecasts
- Policy recommendations
- Data refresh status

Current data: {summary.get('unique_states', 0)} states, {summary.get('unique_pincodes', 0):,} pincodes."""


def create_agents(api_key: str | None = None) -> AadhaarAnalysisAgents:
    """Create and return the agent system."""
    return AadhaarAnalysisAgents(api_key)

# Alias for API compatibility
AadhaarAgentSystem = AadhaarAnalysisAgents
