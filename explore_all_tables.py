"""
Quick script to explore all CSV tables and identify what we need
"""

import pandas as pd 
from pathlib import Path 

PROCESSED_DIR = Path('data/processed')

#get all csv files
csv_files = sorted(list(PROCESSED_DIR.glob('*.csv')))

print("="*70)
print("ALL TABLES OVERVIEW")
print("="*70)

for i, file in enumerate(csv_files, 1):
    print(f"\n{i}. {file.name}")
    df = pd.read_csv(file, nrows=5)
    print(f" Shape: {df.shape[0]} rows (showing first 5)")
    print(f"  Columns: {', '.join(df.columns.tolist())}")

print("\n" + "="*70)
print('DETAILED EXPLORATION OF KEY TABLES')
print("="*70)

#find county information
print("\n1. COUNTY INFORMATION")
print("-"*70)
boces_file = PROCESSED_DIR / 'ENROLL_BOCES_and_N_RC.csv'
if boces_file.exists():
    df = pd.read_csv(boces_file)

    #finding target counties
    target_counties = ['NEW YORK', 'WESTCHESTER', 'NASSAU', 'SUFFOLK']
    print(f"\nAll counties in dataset:")
    print(df['COUNTY_NAME'].value_counts())

    print(f"\nTarget counties districts:")
    for county in target_counties:
        matches = df[df['COUNTY_NAME'].str.contains(county, case=False, na=False)]
        if len(matches) > 0:
            print(f"\n{county} County: {matches['DISTRICT_NAME'].nunique()} unique districts")
            print(matches[['DISTRICT_CD', 'DISTRICT_NAME', 'COUNTY_NAME']].drop_duplicates().head(10))

#look at studed tables for metrics
print("\n\n2. AVAILABLE METRICS IN STUDED TABLES")
print("=" * 70)
studed_files = [f for f in csv_files if f.name.startswith('STUDED_')]
for file in studed_files:
    print(f"\n{file.name}:")
    df = pd.read_csv(file, nrows=100)

    #check for ENTITY_CD and ENTITY_NAME
    if 'ENTITY_CD' in df.columns and 'ENTITY_NAME' in df.columns:
        #checking for NYC
        nyc = df[df['ENTITY_NAME'].str.contains('NYC', case=False, na=False)]
        if len(nyc) > 0:
            print(f"Contains NYC data")
            print(f"Sample columns: {', '.join(df.columns.tolist())}")

#look at enrollment data structure
print("\n\n3. ENROLLMENT DATA STRUCTURE")
print('='*70)
enroll_bed = PROCESSED_DIR / 'ENROLL_BEDS_Day_Enrollment.csv'
if enroll_bed.exists():
    df = pd.read_csv(enroll_bed)
    print(f"Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print("\nSample NYC data:")
    nyc = df[df['ENTITY_CD'] == 1]
    if len(nyc) > 0:
        print(nyc.head())

print("\n\n" + "="*70)
print("SUMMARY: Tables We Need")
print("="*70)
print("""
For the dashboard, we'll use:
1. ENROLL_BOCES_and_N_RC.csv - For county/district mapping
2. ENROLL_BEDS_Day_Enrollment.csv - For enrollment counts
3. ENROLL_Demographic_Factors.csv - For demographics (race, poverty, etc.)
4. STUDED tables - For performance metrics:
    - Test scores
    - Graduation rates
    - Class sizes
    - Attendance/suspensions
Next: Create data preprocessing pipeline to filter and merge these.
 """)
