"""
Quick exploration of graduation data
"""

import pandas as pd 
from pathlib import Path 

PROCESSED_DIR = Path('data/processed')

print("="*70)
print("GRADUATION DATA EXPLORATION")
print("="*70)

#load graduation data
grad_file = PROCESSED_DIR / 'GRAD_GRAD_RATE_AND_OUTCOMES_2024.csv'
grad_df = pd.read_csv(grad_file)

print(f"\nShape: {grad_df.shape}")
print(f"\nColumns ({len(grad_df.columns)}):")
for i, col in enumerate(grad_df.columns, 1):
    print(f" {i}. {col}")

print(f"\nFirst 10 rows:")
print(grad_df.head(10))

print(f"\nData types:")
print(grad_df.dtypes)

#look for entity/district identifiers
print(f"\n" + "="*70)
print("KEY IDENTIFIERS")
print("="*70)

if 'ENTITY_CD' in grad_df.columns:
    print(f"\nUnique ENTITY_CD values: {grad_df['ENTITY_CD'].nunique()}")
    print(f"Dample ENTITY_CD values:")
    print(grad_df['ENTITY_CD'].value_counts().head(10))

if 'ENTITY_NAME' in grad_df.columns:
    print("\nSample ENTITY_NAME values:")
    print(grad_df['ENTITY_NAME'].value_counts().head(10))

#look for graduation rate columns
print(f"\n" + "="*70)
print("GRADUATION METRICS")
print("="*70)

grad_cols = [col for col in grad_df.columns if 'GRAD' in col.upper() or 'RATE' in col.upper()]
print("\nColumns related to graduation rates:")
for col in grad_cols:
    print(f" - {col}")
    if len(grad_df) > 0:
        print(f" Sample values: {grad_df[col].dropna().head(5).tolist()}")

#look for cohort information
cohort_cols = [col for col in grad_df.columns if 'COHORT' in col.upper()]
if cohort_cols:
    print("\nCohort columns:")
    for col in cohort_cols:
        print(f" - {col}")

#check for subgroup breakdowns
print(f"\n" + "="*70)
print("DEMOGRAPHIC SUBGROUPS")
print("="*70)

subgroup_indicators = ['SUBGROUP', 'DEMOGRAPHICS', 'RACE', 'ETHNICITY', 'DISABILITY', 'ELL']
subgroup_cols = [col for col in grad_df.columns if any(ind in col.upper() for ind in subgroup_indicators)]

if subgroup_cols:
    print(f"\nSubgroup columns found:")
    for col in subgroup_cols:
        print(f" - {col}")
        if grad_df[col].dtype == 'object':
            print(f" Unique values: {grad_df[col].nunique()}")
            print(f" Sample: {grad_df[col].value_counts().head(3).to_dict()}")

#check for nyc and target counties
print(f"\n" + "="*70)
print("TARGET REGIONS")
print("="*70)

if 'ENTITY_NAME' in grad_df.columns:
    nyc = grad_df[grad_df['ENTITY_NAME'].str.contains('NYC|NEW YORK CITY', case=False, na=False)]
    print(f"\nNYC records: {len(nyc)}")
    if len(nyc) > 0:
        print(nyc[['ENTITY_CD', 'ENTITY_NAME']].head())

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("""
Next steps:
1. Identify the main graduation rate column(s)
2. Filter for target counties (NYC, Westchester, Nassau, Suffolk)
3. Merge with master dataset
4. Add to dashboard visualizations
 """)