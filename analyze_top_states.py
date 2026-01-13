"""Analyze top 3 states by enrolments."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'src')
from data_pipeline import get_pipeline

# Load data
pipeline = get_pipeline('data')
state_data = pipeline.get_state_analytics()

# Get top 3 states by enrolments
top_states = state_data.nlargest(3, 'total_enrolments')

print('=' * 70)
print('TOP 3 STATES BY ENROLMENTS - DETAILED ANALYSIS')
print('=' * 70)

for idx, row in top_states.iterrows():
    state_name = row['state']
    print(f"\n>> {state_name}")
    print('-' * 50)
    
    print("\nENROLMENTS:")
    print(f"  • Total New Enrolments: {row['total_enrolments']:,.0f}")
    print(f"  • Age 0-5: {row['age_0_5']:,.0f}")
    print(f"  • Age 5-17: {row['age_5_17']:,.0f}")
    print(f"  • Age 18+: {row['age_18_greater']:,.0f}")
    
    print("\nBIOMETRIC UPDATES:")
    print(f"  • Total Biometric Updates: {row['total_bio_updates']:,.0f}")
    print(f"  • Age 5-17: {row['bio_age_5_17']:,.0f}")
    print(f"  • Age 17+: {row['bio_age_17_']:,.0f}")
    
    print("\nDEMOGRAPHIC UPDATES:")
    print(f"  • Total Demographic Updates: {row['total_demo_updates']:,.0f}")
    print(f"  • Age 5-17: {row['demo_age_5_17']:,.0f}")
    print(f"  • Age 17+: {row['demo_age_17_']:,.0f}")
    
    print("\nKEY INDICES:")
    print(f"  • Identity Velocity Index (IVI): {row['IVI']:.2f}")
    print(f"  • Biometric Stress Index (BSI): {row['BSI']:.2f}")
    print(f"  • Youth Update Ratio: {row['youth_ratio']*100:.2f}%")
    print(f"  • Stability Score: {row['stability_score']:.1f}/100")
    print(f"  • Total Updates: {row['total_updates']:,.0f}")

# Comparison summary
print('\n' + '=' * 70)
print('COMPARATIVE SUMMARY')
print('=' * 70)

print("\nState Rankings by Enrolments:")
for i, (_, row) in enumerate(top_states.iterrows(), 1):
    print(f"  {i}. {row['state']}: {row['total_enrolments']:,.0f} enrolments")

print(f"\nHighest Biometric Updates: {top_states.nlargest(1, 'total_bio_updates').iloc[0]['state']}")
print(f"Highest BSI (Stress): {top_states.nlargest(1, 'BSI').iloc[0]['state']} ({top_states.nlargest(1, 'BSI').iloc[0]['BSI']:.2f})")
print(f"Most Stable: {top_states.nlargest(1, 'stability_score').iloc[0]['state']} ({top_states.nlargest(1, 'stability_score').iloc[0]['stability_score']:.1f}/100)")

print('\n' + '=' * 70)

