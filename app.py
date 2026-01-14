"""
Aadhaar Identity Intelligence Platform
Main Streamlit Dashboard Application
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent / ".env")
except ImportError:
    pass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_pipeline import get_pipeline, AadhaarDataPipeline, refresh_pipeline, get_last_load_time, check_for_new_data
from ml_models import AnomalyDetector, StateClustering, DemandForecaster, IdentityLifecyclePredictor
from agents import create_agents, set_data_context, get_trace, clear_trace

# Page config
st.set_page_config(
    page_title="Aadhaar Identity Intelligence",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .insight-box {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .alert-box {
        background: #ffe6e6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ff4444;
        margin: 0.5rem 0;
    }
    .success-box {
        background: #e6ffe6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #44ff44;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_data():
    """Load and cache data pipeline."""
    # Create fresh instance to avoid stale data
    pipeline = AadhaarDataPipeline("data")
    pipeline.load_all_data()
    return pipeline


@st.cache_data
def get_cached_analytics(_pipeline: AadhaarDataPipeline):
    """Cache expensive analytics computations."""
    pincode_data = _pipeline.get_pincode_analytics()
    # Ensure state column is string type
    if 'state' in pincode_data.columns:
        pincode_data['state'] = pincode_data['state'].astype(str)
    
    return {
        'summary': _pipeline.get_summary_stats(),
        'state_data': _pipeline.get_state_analytics(),
        'pincode_data': pincode_data,
        'temporal': _pipeline.get_temporal_analytics()
    }


def main():
    """Main application."""
    
    # Header
    st.markdown('<h1 class="main-header">🔐 Aadhaar Identity Intelligence Platform</h1>', 
                unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/en/thumb/c/cf/Aadhaar_Logo.svg/1200px-Aadhaar_Logo.svg.png", 
                 width=150)
        st.title("Navigation")
        
        page = st.radio(
            "Select View",
            ["📊 Dashboard", "🗺️ State Analysis", "📍 Pincode Analytics", 
             "⚠️ Anomaly Detection", "📈 Forecasting", "🤖 AI Assistant"]
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.info("""
        This platform provides real-time analytics 
        and AI-powered insights for Aadhaar identity 
        system management.
        """)
        
        st.markdown("---")
        
        # Data refresh section
        st.markdown("### Data Status")
        last_load = get_last_load_time()
        if last_load:
            st.caption(f"📅 Last loaded: {last_load}")
        
        file_counts = check_for_new_data()
        if file_counts:
            total_files = sum(file_counts.values())
            st.caption(f"📁 {total_files} CSV files across 3 folders")
        
        if st.button("🔄 Refresh Data"):
            with st.spinner("Reloading data from disk..."):
                refresh_pipeline()
                st.cache_resource.clear()
                st.cache_data.clear()
            st.success("Data refreshed!")
            st.rerun()
        
        if st.button("🗑️ Clear Cache"):
            st.cache_resource.clear()
            st.cache_data.clear()
            st.rerun()
    
    # Load data
    with st.spinner("Loading data..."):
        try:
            pipeline = load_data()
            analytics = get_cached_analytics(pipeline)
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.stop()
    
    # Route to pages
    if page == "📊 Dashboard":
        render_dashboard(analytics)
    elif page == "🗺️ State Analysis":
        render_state_analysis(analytics)
    elif page == "📍 Pincode Analytics":
        render_pincode_analytics(analytics)
    elif page == "⚠️ Anomaly Detection":
        render_anomaly_detection(analytics)
    elif page == "📈 Forecasting":
        render_forecasting(analytics)
    elif page == "🤖 AI Assistant":
        render_ai_assistant(analytics)


def render_dashboard(analytics: dict):
    """Render main dashboard."""
    summary = analytics['summary']
    
    st.header("📊 Executive Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Biometric Updates",
            f"{summary['total_bio_updates']:,}",
            delta="70M+ processed"
        )
    
    with col2:
        st.metric(
            "Total Demographic Updates",
            f"{summary['total_demo_updates']:,}",
            delta="49M+ processed"
        )
    
    with col3:
        st.metric(
            "New Enrolments",
            f"{summary['total_enrolments']:,}",
            delta="5.4M+ registered"
        )
    
    with col4:
        st.metric(
            "Pincodes Covered",
            f"{summary['unique_pincodes']:,}",
            delta=f"{summary['unique_states']} States"
        )
    
    st.markdown("---")
    
    # Novel Indices
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Identity Velocity Index (IVI)")
        st.info(f"**Average IVI:** {summary['avg_ivi']:.2f}")
        st.caption("Higher IVI = More identity data changes per enrolment")
        
        # IVI gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=summary['avg_ivi'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "System IVI"},
            gauge={
                'axis': {'range': [0, 1000]},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [0, 200], 'color': "#e6ffe6"},
                    {'range': [200, 500], 'color': "#fff3e6"},
                    {'range': [500, 1000], 'color': "#ffe6e6"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 500
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.subheader("🔬 Biometric Stress Index (BSI)")
        st.info(f"**Average BSI:** {summary['avg_bsi']:.2f}")
        st.caption("Higher BSI = More biometric-related issues")
        
        # BSI gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=summary['avg_bsi'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "System BSI"},
            gauge={
                'axis': {'range': [0, 5]},
                'bar': {'color': "#764ba2"},
                'steps': [
                    {'range': [0, 1], 'color': "#e6ffe6"},
                    {'range': [1, 2], 'color': "#fff3e6"},
                    {'range': [2, 5], 'color': "#ffe6e6"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 2
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, width='stretch')
    
    st.markdown("---")
    
    # Temporal trends
    st.subheader("📈 Activity Trends")
    temporal = analytics['temporal']
    
    # Monthly trends
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    bio_monthly = temporal['bio_monthly']
    demo_monthly = temporal['demo_monthly']
    enrol_monthly = temporal['enrol_monthly']
    
    fig.add_trace(
        go.Scatter(
            x=[str(x) for x in bio_monthly.index],
            y=bio_monthly.values / 1e6,
            name="Biometric Updates",
            line=dict(color="#667eea", width=3)
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=[str(x) for x in demo_monthly.index],
            y=demo_monthly.values / 1e6,
            name="Demographic Updates",
            line=dict(color="#764ba2", width=3)
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=[str(x) for x in enrol_monthly.index],
            y=enrol_monthly.values / 1e6,
            name="New Enrolments",
            line=dict(color="#44af69", width=3)
        ),
        secondary_y=True
    )
    
    fig.update_layout(
        title="Monthly Activity Trends",
        xaxis_title="Month",
        height=400
    )
    fig.update_yaxes(title_text="Updates (Millions)", secondary_y=False)
    fig.update_yaxes(title_text="Enrolments (Millions)", secondary_y=True)
    
    st.plotly_chart(fig, width='stretch')


def render_state_analysis(analytics: dict):
    """Render state analysis page."""
    st.header("🗺️ State-Level Analysis")
    
    state_data = analytics['state_data']
    
    # State clustering
    st.subheader("State Clustering by Identity Behavior")
    
    clusterer = StateClustering(n_clusters=4)
    clustered_data = clusterer.fit_predict(state_data)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Cluster visualization
        if 'pca_x' in clustered_data.columns:
            fig = px.scatter(
                clustered_data,
                x='pca_x',
                y='pca_y',
                color='cluster_label',
                hover_name='state',
                size='total_updates',
                title="State Clusters (PCA Projection)",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, width='stretch')
    
    with col2:
        # Cluster profiles
        st.subheader("Cluster Profiles")
        profiles = clusterer.get_cluster_profiles(clustered_data)
        
        for cluster_name, profile in profiles.items():
            with st.expander(f"📌 {profile.get('label', cluster_name)}"):
                st.write(f"**States:** {len(profile.get('states', []))}")
                st.write(f"**Avg IVI:** {profile.get('avg_IVI', 0):.1f}")
                st.write(f"**Avg BSI:** {profile.get('avg_BSI', 0):.2f}")
                st.write(f"**States:** {', '.join(profile.get('states', [])[:5])}")
    
    st.markdown("---")
    
    # Top states charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top States by Total Updates")
        top_states = clustered_data.nlargest(15, 'total_updates')
        
        fig = px.bar(
            top_states,
            y='state',
            x='total_updates',
            orientation='h',
            color='cluster_label',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.subheader("State Identity Metrics Comparison")
        
        fig = px.scatter(
            clustered_data,
            x='IVI',
            y='BSI',
            size='total_updates',
            hover_name='state',
            color='cluster_label',
            title="IVI vs BSI by State",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, width='stretch')


def render_pincode_analytics(analytics: dict):
    """Render pincode-level analytics."""
    st.header("📍 Pincode-Level Analytics")
    
    pincode_data = analytics['pincode_data']
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        # Convert to string and filter out invalid entries before sorting
        state_list = pincode_data['state'].dropna().astype(str).unique().tolist()
        state_list = [s for s in state_list if not s.isdigit()]  # Remove numeric entries
        states = ['All'] + sorted(state_list)
        selected_state = st.selectbox("Filter by State", states)
    
    with col2:
        metric = st.selectbox(
            "Color by Metric",
            ['identity_velocity_index', 'biometric_stress_index', 'total_updates']
        )
    
    # Filter data
    if selected_state != 'All':
        filtered_data = pincode_data[pincode_data['state'] == selected_state]
    else:
        filtered_data = pincode_data
    
    # Lifecycle predictor
    predictor = IdentityLifecyclePredictor()
    filtered_data = predictor.calculate_update_probability(filtered_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Pincode Risk Distribution")
        risk_counts = filtered_data['risk_level'].value_counts()
        
        fig = px.pie(
            values=risk_counts.values,
            names=risk_counts.index,
            title="Pincodes by Risk Level",
            color_discrete_sequence=['#44af69', '#f9c74f', '#f8961e', '#f94144']
        )
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.subheader("High Priority Pincodes")
        high_priority = predictor.get_high_priority_pincodes(filtered_data, top_n=10)
        st.dataframe(
            high_priority[['pincode', 'state', 'district', 'risk_level', 'update_probability']],
            width='stretch'
        )
    
    st.markdown("---")
    
    # Distribution plots
    st.subheader("Index Distributions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig = px.histogram(
            filtered_data[filtered_data['identity_velocity_index'] < filtered_data['identity_velocity_index'].quantile(0.99)],
            x='identity_velocity_index',
            nbins=50,
            title="Identity Velocity Index Distribution",
            color_discrete_sequence=['#667eea']
        )
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        fig = px.histogram(
            filtered_data[filtered_data['biometric_stress_index'] < filtered_data['biometric_stress_index'].quantile(0.99)],
            x='biometric_stress_index',
            nbins=50,
            title="Biometric Stress Index Distribution",
            color_discrete_sequence=['#764ba2']
        )
        st.plotly_chart(fig, width='stretch')
    
    with col3:
        fig = px.histogram(
            filtered_data,
            x='update_probability',
            nbins=50,
            title="Update Probability Distribution",
            color_discrete_sequence=['#44af69']
        )
        st.plotly_chart(fig, width='stretch')


def render_anomaly_detection(analytics: dict):
    """Render anomaly detection page."""
    st.header("⚠️ Anomaly Detection")
    
    pincode_data = analytics['pincode_data']
    temporal = analytics['temporal']
    
    # Detect anomalies
    detector = AnomalyDetector(contamination=0.05)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Pincode-Level Anomalies")
        
        pincode_anomalies = detector.detect_pincode_anomalies(pincode_data)
        anomaly_summary = detector.get_anomaly_summary(pincode_anomalies)
        
        st.metric("Anomalies Detected", anomaly_summary['anomaly_count'])
        st.metric("Anomaly Rate", f"{anomaly_summary['anomaly_percentage']:.1f}%")
        
        # Show top anomalies
        if anomaly_summary.get('top_anomalies'):
            st.subheader("Top Anomalous Pincodes")
            top_anomalies = pd.DataFrame(anomaly_summary['top_anomalies'])
            if not top_anomalies.empty:
                display_cols = ['pincode', 'state', 'district', 'anomaly_score']
                display_cols = [c for c in display_cols if c in top_anomalies.columns]
                st.dataframe(top_anomalies[display_cols], width='stretch')
    
    with col2:
        st.subheader("Temporal Anomalies")
        
        daily_data = temporal['daily']
        temporal_anomalies = detector.detect_temporal_anomalies(daily_data)
        
        anomaly_dates = temporal_anomalies[temporal_anomalies.get('is_anomaly', False)]
        st.metric("Anomalous Days", len(anomaly_dates))
        
        if len(anomaly_dates) > 0:
            st.warning(f"⚠️ {len(anomaly_dates)} days with unusual activity detected")
    
    st.markdown("---")
    
    # Anomaly visualization
    st.subheader("Anomaly Distribution")
    
    fig = px.scatter(
        pincode_anomalies[pincode_anomalies['is_anomaly']],
        x='identity_velocity_index',
        y='biometric_stress_index',
        color='anomaly_score',
        hover_data=['pincode', 'state', 'district'],
        title="Anomalous Pincodes: IVI vs BSI",
        color_continuous_scale='Reds'
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, width='stretch')


def render_forecasting(analytics: dict):
    """Render forecasting page."""
    st.header("📈 Demand Forecasting")
    
    temporal = analytics['temporal']
    daily_data = temporal['daily']
    
    # Forecaster
    forecaster = DemandForecaster(forecast_days=30)
    
    st.subheader("30-Day Activity Forecast")
    
    metric = st.selectbox(
        "Select Metric to Forecast",
        ['total_bio_updates', 'total_demo_updates', 'total_enrolments']
    )
    
    with st.spinner("Generating forecast..."):
        forecast_result = forecaster.forecast_with_prophet(daily_data, metric)
    
    # Plot
    fig = go.Figure()
    
    # Historical data
    historical = forecast_result['historical']
    hist_df = pd.DataFrame(historical)
    
    fig.add_trace(go.Scatter(
        x=hist_df['date'] if 'date' in hist_df.columns else hist_df.index,
        y=hist_df[metric] if metric in hist_df.columns else hist_df.iloc[:, 1],
        name='Historical',
        line=dict(color='#667eea', width=2)
    ))
    
    # Forecast
    forecast = forecast_result['forecast']
    if forecast:
        forecast_df = pd.DataFrame(forecast)
        
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat'],
            name='Forecast',
            line=dict(color='#764ba2', width=2, dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat_upper'],
            fill=None,
            mode='lines',
            line=dict(color='rgba(118, 75, 162, 0.2)'),
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat_lower'],
            fill='tonexty',
            mode='lines',
            line=dict(color='rgba(118, 75, 162, 0.2)'),
            name='Confidence Interval'
        ))
    
    fig.update_layout(
        title=f"Forecast: {metric.replace('_', ' ').title()}",
        xaxis_title="Date",
        yaxis_title="Count",
        height=500
    )
    
    st.plotly_chart(fig, width='stretch')
    
    # Forecast summary
    if forecast:
        col1, col2, col3 = st.columns(3)
        forecast_df = pd.DataFrame(forecast)
        
        with col1:
            st.metric("Expected Peak", f"{forecast_df['yhat'].max():,.0f}")
        with col2:
            st.metric("Average Forecast", f"{forecast_df['yhat'].mean():,.0f}")
        with col3:
            st.metric("Forecast Method", forecast_result['method'].title())


def generate_dynamic_suggestions(summary: dict, anomalies: list, state_data: pd.DataFrame) -> list:
    """Generate context-aware suggestions based on actual data."""
    suggestions = []
    
    # Always include these core questions
    suggestions.append("What are the main anomalies?")
    
    # Add top state suggestion dynamically
    if summary.get('top_state'):
        suggestions.append(f"Analyze {summary['top_state']} in detail")
    
    # Add high-stress state if BSI is concerning
    if summary.get('avg_bsi', 0) > 1.5:
        high_stress = summary.get('high_stress_state', 'Unknown')
        suggestions.append(f"Why does {high_stress} have high biometric stress?")
    
    # Add comparison of top 2 states
    if isinstance(state_data, pd.DataFrame) and len(state_data) >= 2:
        top_states = state_data.nlargest(2, 'total_updates')['state'].tolist()
        suggestions.append(f"Compare {top_states[0]} and {top_states[1]}")
    
    # Add anomaly-specific question if anomalies exist
    if anomalies and len(anomalies) > 0:
        suggestions.append(f"What's causing the {len(anomalies)} detected anomalies?")
    
    # Add district-level suggestion based on top state
    if summary.get('top_state'):
        suggestions.append(f"List districts in {summary['top_state']}")
    
    # Add policy recommendation
    suggestions.append("What policies do you recommend based on current data?")
    
    # Limit to 6 suggestions max
    return suggestions[:6]


def render_ai_assistant(analytics: dict):
    """Render AI assistant page."""
    st.header("🤖 AI Analysis Assistant")
    
    # Initialize agents
    agents = create_agents()
    
    # Prepare context
    summary = analytics['summary']
    state_data = analytics['state_data']
    pincode_data = analytics['pincode_data']
    
    # Detect anomalies for context
    detector = AnomalyDetector()
    pincode_anomalies = detector.detect_pincode_anomalies(pincode_data)
    anomalies = pincode_anomalies[pincode_anomalies['is_anomaly']].head(10).to_dict('records')
    
    # Cluster for context
    clusterer = StateClustering()
    clustered_states = clusterer.fit_predict(state_data)
    cluster_profiles = clusterer.get_cluster_profiles(clustered_states)
    
    context = {
        'summary_stats': summary,
        'state_analytics': state_data,  # Pass DataFrame directly for tool access
        'pincode_data': pincode_data,   # Pass DataFrame for district-level analysis
        'anomalies': anomalies,
        'cluster_profiles': cluster_profiles,
        'forecasts': {}
    }
    
    # Set context for tools (enables LangGraph tools to access data)
    set_data_context(context)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Chat with AI")
        
        # Chat interface
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Toggle for showing trace
        show_trace = st.checkbox("🔍 Show Agent Trace (Debug Mode)", value=True)
        
        # Chat input
        if prompt := st.chat_input("Ask about the Aadhaar data..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get AI response with trace
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response, trace = agents.chat_with_agent(prompt, context, return_trace=True)
                
                # Show trace if enabled
                if show_trace and trace:
                    with st.expander("🔍 **Agent Execution Trace**", expanded=True):
                        for i, entry in enumerate(trace, 1):
                            step = entry.get('step', 'UNKNOWN')
                            
                            if step == 'TOOL_CALL':
                                st.markdown(f"""
**Step {i}: 🔧 Tool Called**
- **Tool:** `{entry.get('tool', 'unknown')}`
- **Arguments:** `{entry.get('args', {})}`
""")
                            elif step == 'TOOL_RESPONSE':
                                st.markdown(f"""
**Step {i}: 📤 Tool Response**
- **Tool:** `{entry.get('tool', 'unknown')}`
- **Result Preview:**
```
{entry.get('result', 'No result')}
```
""")
                            elif step == 'AI_RESPONSE':
                                st.markdown(f"""
**Step {i}: 🤖 AI Thinking**
```
{entry.get('content', '')}
```
""")
                            elif step == 'ERROR':
                                st.error(f"**Step {i}: ❌ Error** - {entry.get('error', 'Unknown error')}")
                            elif step == 'SIMPLE_CHAT':
                                st.info(f"**Step {i}: 💬 Simple Chat Mode** (no tools available)")
                            elif step == 'RULE_BASED':
                                st.info(f"**Step {i}: 📋 Rule-Based Mode** (no LLM configured)")
                            
                            st.markdown("---")
                
                st.markdown(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    with col2:
        st.subheader("📋 Auto-Generated Report")
        
        if st.button("🔄 Generate Full Report", width='stretch'):
            with st.spinner("Running AI analysis pipeline..."):
                result = agents.run_analysis(context)
            
            st.markdown("### Insights")
            for insight in result['insights']:
                st.markdown(insight)
            
            st.markdown("### Recommendations")
            for rec in result['recommendations']:
                st.markdown(rec)
            
            # Download button
            st.download_button(
                "📥 Download Report",
                result['report'],
                file_name="aadhaar_intelligence_report.txt",
                mime="text/plain"
            )
        
        st.markdown("---")
        st.subheader("💡 Suggested Questions")
        
        # Generate dynamic suggestions based on actual data
        suggestions = generate_dynamic_suggestions(summary, anomalies, state_data)
        
        for suggestion in suggestions:
            if st.button(suggestion, key=suggestion):
                st.session_state.messages.append({"role": "user", "content": suggestion})
                st.rerun()
        
        st.markdown("---")
        st.subheader("🛠️ Available Tools")
        st.caption("""
        The AI agent has access to:
        - **Summary Stats**: Overall system metrics
        - **Anomaly Report**: Detect unusual patterns
        - **State Analysis**: Analyze specific states
        - **District Analysis**: Analyze specific districts 🆕
        - **List Districts**: See districts in a state 🆕
        - **Cluster Insights**: View state groupings
        - **Forecasts**: Demand predictions
        - **Policy Recommendations**: Actionable advice
        - **Compare States**: Side-by-side comparison
        - **Refresh Data**: Reload from disk
        """)


if __name__ == "__main__":
    main()

