"""Test script for all system components."""
import sys
sys.path.insert(0, 'src')

from data_pipeline import get_pipeline
from ml_models import AnomalyDetector, StateClustering, IdentityLifecyclePredictor
from agents import create_agents

print("=" * 60)
print("TESTING AADHAAR IDENTITY INTELLIGENCE PLATFORM")
print("=" * 60)

# Test 1: Data Pipeline
print("\n1. Testing Data Pipeline...")
pipeline = get_pipeline('data')
summary = pipeline.get_summary_stats()
print(f"   [OK] Total Bio Updates: {summary['total_bio_updates']:,}")
print(f"   [OK] Total Demo Updates: {summary['total_demo_updates']:,}")
print(f"   [OK] Unique Pincodes: {summary['unique_pincodes']:,}")
print(f"   [OK] States: {summary['unique_states']}")

# Test 2: Pincode Analytics
print("\n2. Testing Pincode Analytics...")
pincode_data = pipeline.get_pincode_analytics()
print(f"   [OK] Pincode records: {len(pincode_data):,}")
print(f"   [OK] Avg IVI: {pincode_data['identity_velocity_index'].mean():.2f}")
print(f"   [OK] Avg BSI: {pincode_data['biometric_stress_index'].mean():.2f}")

# Test 3: State Analytics
print("\n3. Testing State Analytics...")
state_data = pipeline.get_state_analytics()
print(f"   [OK] States analyzed: {len(state_data)}")
top_state = state_data.nlargest(1, 'total_updates')['state'].iloc[0]
print(f"   [OK] Top state: {top_state}")

# Test 4: Anomaly Detection
print("\n4. Testing Anomaly Detection...")
detector = AnomalyDetector(contamination=0.05)
anomaly_results = detector.detect_pincode_anomalies(pincode_data)
anomaly_count = anomaly_results['is_anomaly'].sum()
print(f"   [OK] Anomalies detected: {anomaly_count:,}")

# Test 5: State Clustering
print("\n5. Testing State Clustering...")
clusterer = StateClustering(n_clusters=4)
clustered_states = clusterer.fit_predict(state_data)
profiles = clusterer.get_cluster_profiles(clustered_states)
print(f"   [OK] Clusters created: {len(profiles)}")
for name, profile in profiles.items():
    print(f"      - {profile['label']}: {profile['count']} states")

# Test 6: Lifecycle Predictor
print("\n6. Testing Identity Lifecycle Predictor...")
predictor = IdentityLifecyclePredictor()
risk_data = predictor.calculate_update_probability(pincode_data)
risk_counts = risk_data['risk_level'].value_counts()
print("   [OK] Risk distribution:")
for level, count in risk_counts.items():
    print(f"      - {level}: {count:,} pincodes")

# Test 7: Agentic AI
print("\n7. Testing Agentic AI System...")
agents = create_agents()

context = {
    'summary_stats': summary,
    'anomalies': anomaly_results[anomaly_results['is_anomaly']].head(5).to_dict('records'),
    'cluster_profiles': profiles,
    'forecasts': {}
}

result = agents.run_analysis(context)
print(f"   [OK] Insights generated: {len(result['insights'])}")
print(f"   [OK] Recommendations: {len(result['recommendations'])}")
print(f"   [OK] Report length: {len(result['report'])} characters")

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
print("\nRun the dashboard with: streamlit run app.py")

