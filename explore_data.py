"""
Comprehensive EDA for Aadhaar Datasets
- Biometric Updates
- Demographic Updates  
- Enrolment Data
"""
import pandas as pd
import glob

# Load all biometric files
bio_files = glob.glob('data/api_data_aadhar_biometric/*.csv')
bio_df = pd.concat([pd.read_csv(f) for f in bio_files], ignore_index=True)

# Load all demographic files
demo_files = glob.glob('data/api_data_aadhar_demographic/*.csv')
demo_df = pd.concat([pd.read_csv(f) for f in demo_files], ignore_index=True)

# Load all enrolment files
enrol_files = glob.glob('data/api_data_aadhar_enrolment/*.csv')
enrol_df = pd.concat([pd.read_csv(f) for f in enrol_files], ignore_index=True)

print('='*70)
print('DATASET SIZES:')
print(f'Biometric: {bio_df.shape}')
print(f'Demographic: {demo_df.shape}')
print(f'Enrolment: {enrol_df.shape}')

print('\n' + '='*70)
print('DATE RANGES:')
bio_dates = bio_df['date'].unique()
demo_dates = demo_df['date'].unique()
enrol_dates = enrol_df['date'].unique()
print(f'Biometric: {len(bio_dates)} unique dates')
print(f'  Sample: {list(bio_dates[:5])}')
print(f'Demographic: {len(demo_dates)} unique dates')
print(f'  Sample: {list(demo_dates[:5])}')
print(f'Enrolment: {len(enrol_dates)} unique dates')
print(f'  Sample: {list(enrol_dates[:5])}')

print('\n' + '='*70)
print('GEOGRAPHIC COVERAGE:')
print(f'Biometric: {bio_df["state"].nunique()} states, {bio_df["district"].nunique()} districts, {bio_df["pincode"].nunique()} pincodes')
print(f'Demographic: {demo_df["state"].nunique()} states, {demo_df["district"].nunique()} districts, {demo_df["pincode"].nunique()} pincodes')
print(f'Enrolment: {enrol_df["state"].nunique()} states, {enrol_df["district"].nunique()} districts, {enrol_df["pincode"].nunique()} pincodes')

print('\n' + '='*70)
print('STATES LIST:')
all_states = sorted(set(bio_df['state'].unique()) | set(demo_df['state'].unique()) | set(enrol_df['state'].unique()))
print(f'Total unique states/UTs: {len(all_states)}')
for i, state in enumerate(all_states, 1):
    print(f'  {i}. {state}')

print('\n' + '='*70)
print('BIOMETRIC DATA - Descriptive Stats:')
print(bio_df.describe())

print('\n' + '='*70)
print('DEMOGRAPHIC DATA - Descriptive Stats:')
print(demo_df.describe())

print('\n' + '='*70)
print('ENROLMENT DATA - Descriptive Stats:')
print(enrol_df.describe())

print('\n' + '='*70)
print('NULL VALUES CHECK:')
print('Biometric:')
print(bio_df.isnull().sum())
print('\nDemographic:')
print(demo_df.isnull().sum())
print('\nEnrolment:')
print(enrol_df.isnull().sum())

print('\n' + '='*70)
print('AGGREGATED TOTALS:')
print(f'Total Biometric Updates (age 5-17): {bio_df["bio_age_5_17"].sum():,}')
print(f'Total Biometric Updates (age 17+): {bio_df["bio_age_17_"].sum():,}')
print(f'Total Demographic Updates (age 5-17): {demo_df["demo_age_5_17"].sum():,}')
print(f'Total Demographic Updates (age 17+): {demo_df["demo_age_17_"].sum():,}')
print(f'Total Enrolments (age 0-5): {enrol_df["age_0_5"].sum():,}')
print(f'Total Enrolments (age 5-17): {enrol_df["age_5_17"].sum():,}')
print(f'Total Enrolments (age 18+): {enrol_df["age_18_greater"].sum():,}')

print('\n' + '='*70)
print('STATE-WISE SUMMARY (Top 10 by activity):')
bio_state = bio_df.groupby('state')[['bio_age_5_17', 'bio_age_17_']].sum()
bio_state['total_bio'] = bio_state['bio_age_5_17'] + bio_state['bio_age_17_']
print('\nTop 10 States by Biometric Updates:')
print(bio_state.sort_values('total_bio', ascending=False).head(10))

demo_state = demo_df.groupby('state')[['demo_age_5_17', 'demo_age_17_']].sum()
demo_state['total_demo'] = demo_state['demo_age_5_17'] + demo_state['demo_age_17_']
print('\nTop 10 States by Demographic Updates:')
print(demo_state.sort_values('total_demo', ascending=False).head(10))

enrol_state = enrol_df.groupby('state')[['age_0_5', 'age_5_17', 'age_18_greater']].sum()
enrol_state['total_enrol'] = enrol_state['age_0_5'] + enrol_state['age_5_17'] + enrol_state['age_18_greater']
print('\nTop 10 States by Enrolments:')
print(enrol_state.sort_values('total_enrol', ascending=False).head(10))

print('\n' + '='*70)
print('PINCODE-LEVEL GRANULARITY ANALYSIS:')
print(f'Average records per pincode (Bio): {len(bio_df) / bio_df["pincode"].nunique():.2f}')
print(f'Average records per pincode (Demo): {len(demo_df) / demo_df["pincode"].nunique():.2f}')
print(f'Average records per pincode (Enrol): {len(enrol_df) / enrol_df["pincode"].nunique():.2f}')

print('\n' + '='*70)
print('COMMON PINCODES ACROSS DATASETS:')
bio_pins = set(bio_df['pincode'].unique())
demo_pins = set(demo_df['pincode'].unique())
enrol_pins = set(enrol_df['pincode'].unique())
common_all = bio_pins & demo_pins & enrol_pins
print(f'Pincodes in all 3 datasets: {len(common_all)}')
print(f'Pincodes in Bio & Demo: {len(bio_pins & demo_pins)}')
print(f'Pincodes in Bio & Enrol: {len(bio_pins & enrol_pins)}')
print(f'Pincodes in Demo & Enrol: {len(demo_pins & enrol_pins)}')

