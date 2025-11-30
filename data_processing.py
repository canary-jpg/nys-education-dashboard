"""
Data Processing Pipeline for NYS Education Dashboard
Filters and merges data for NYC, Westchester, Nassau, and Suffolk counties
"""

import pandas as pd 
from pathlib import Path 
import numpy as np 

#paths
RAW_DIR = Path('data/raw')
PROCESSED_DIR = Path('data/processed')
OUTPUT_DIR = Path('data/processed')
OUTPUT_DIR.mkdir(exist_ok=True)

#target counties
TARGET_COUNTIES = ['NEW YORK', 'WESTCHESTER', 'NASSAU', 'SUFFOLK']

print("="*70)
print("NYS EDUCATION DATA PROCESSING PIPELINE")
print("="*70)

#Loading and filtering county/district mapping
print("\n[1/7] Loading district-county mappings...")

boces_df = pd.read_csv(PROCESSED_DIR / 'ENROLL_BOCES_and_N_RC.csv')
#get unique district in target counties
target_districts = boces_df[
    boces_df['COUNTY_NAME'].isin(TARGET_COUNTIES)
][['DISTRICT_CD', 'DISTRICT_NAME', 'COUNTY_NAME']].drop_duplicates()

print(f" Found {len(target_districts)} districts across target counties:")
for county in TARGET_COUNTIES:
    count = len(target_districts[target_districts['COUNTY_NAME'] == county])
    print(f" -{county}: {count} districts")

#save district mapping
target_districts.to_csv(OUTPUT_DIR / 'target_districts.csv', index=False)

# loading and filtering enrollment data
print("\n[2/7] Processing enrollment data...")

enrollment_df = pd.read_csv(PROCESSED_DIR / 'ENROLL_BEDS_Day_Enrollment.csv')

#filter for districts 
district_codes = target_districts['DISTRICT_CD'].dropna().astype(str).unique()

#for enrollments we'll need to filter based on ENTITY_NAME matching district names
enrollment_filtered = enrollment_df[
    enrollment_df['ENTITY_NAME'].isin(target_districts['DISTRICT_NAME']) |
    (enrollment_df['ENTITY_CD'] == 1) #includes NYC aggregate
]
print(f" Filtered to {len(enrollment_filtered)} enrollment records")
enrollment_filtered.to_csv(OUTPUT_DIR / 'enrollment_filtered.csv', index=False)

#loading and filtering demographics
print("\n[3/7] Processing demographic data...")

demographics_df = pd.read_csv(PROCESSED_DIR / 'ENROLL_Demographic_Factors.csv')
demographics_filtered = demographics_df[
    demographics_df['ENTITY_NAME'].isin(target_districts['DISTRICT_NAME']) |
    (demographics_df['ENTITY_CD'] == 1)
]
print(f" Filtered to {len(demographics_filtered)} demographics records")
demographics_filtered.to_csv(OUTPUT_DIR / 'demographics_filtered.csv', index=False)

#loading and filtering STUDED metrics
print('\n[4/7] Processing STUDED metrics...')

studed_files = {
    'attendance': 'STUDED_Attendance.csv',
    'class_size': 'STUDED_Average_Class_Size.csv',
    'lunch': 'STUDED_Free_Reduced_Price_Lunch.csv',
    'suspensions': 'STUDED_Suspensions.csv',
    'staff': 'STUDED_Staff.csv'
}
filtered_studed = {}

for name, filename in studed_files.items():
    file_path = PROCESSED_DIR / filename 
    if file_path.exists():
        df = pd.read_csv(file_path)

        if 'ENTITY_NAME' in df.columns:
            filtered = df[
                df['ENTITY_NAME'].isin(target_districts['DISTRICT_NAME']) |
                (df['ENTITY_CD'] == 1)
            ]
        elif 'DISTRICT_NAME' in df.columns:
            filtered = df[df['DISTRICT_NAME'].isin(target_districts['DISTRICT_NAME'])]
        else:
            filtered = df 
        filtered_studed[name] = filtered 
        output_file = OUTPUT_DIR / f'{name}_filtered.csv'
        filtered.to_csv(output_file, index=False)
        print(f" -{name}: {len(filtered)} records")

#load and filter graduation data
print("\n[6/7] Processing graduation data...")
grad_file = PROCESSED_DIR / 'GRAD_GRAD_RATE_AND_OUTCOMES_2024.csv'
if grad_file.exists():
    grad_df = pd.read_csv(grad_file, low_memory=False)

    #filter for target counties
    grad_filtered = grad_df[
        grad_df['county_name'].isin(TARGET_COUNTIES) |
        (grad_df['nyc_ind'] == 1)
    ].copy()
    
    pct_cols = ['grad_pct', 'dropout_pct', 'still_enr_pct', 'ged_pct',
                'local_pct', 'reg_pct', 'reg_adv_pct']
    
    for col in pct_cols:
        if col in grad_filtered.columns:
            grad_filtered[col] = grad_filtered[col].astype(str).str.replace("%", "").str.strip()
            grad_filtered[col] = pd.to_numeric(grad_filtered[col], errors='coerce')

    #filter for "all students" subgroup for main metrics
    grad_all_students = grad_filtered[grad_filtered['subgroup_name'] == 'All Students'].copy()
    print(f" Filtered to {len(grad_filtered)} total graduation records")
    print(f" 'All Students' records: {len(grad_all_students)}")

    #save filtered graduation data
    grad_filtered.to_csv(OUTPUT_DIR / 'grad_filtered.csv', index=False)
    grad_all_students.to_csv(OUTPUT_DIR / 'graducation_all_students.csv', index=False)
else:
    print(f" Graduation file not found")
    grad_all_students = None

#creating master dataset by joining key metrics
print("\n[7/7] Creating master dataset...")

master = enrollment_filtered[['ENTITY_CD', 'ENTITY_NAME', 'YEAR', 'K12']].copy()
master = master.rename(columns={'K12': 'total_enrollment'})

demo_cols = ['ENTITY_CD', 'YEAR', 'PER_ECDIS', 'PER_BLACK', 'PER_HISP',
            'PER_WHITE', 'PER_ASIAN', 'PER_ELL', 'PER_SWD']
if all(col in demographics_filtered.columns for col in demo_cols):
    master = master.merge(
        demographics_filtered[demo_cols],
        on=['ENTITY_CD', 'YEAR'],
        how='left'
    )
if 'lunch' in filtered_studed:
    lunch = filtered_studed['lunch'][['ENTITY_CD', 'YEAR', 'PER_FREE_LUNCH', 'PER_REDUCED_LUNCH']]
    master = master.merge(lunch, on=['ENTITY_CD', 'YEAR'], how='left')

if 'attendance' in filtered_studed:
    attendance = filtered_studed['attendance'][['ENTITY_CD', 'YEAR', 'ATTENDANCE_RATE']]
    master = master.merge(attendance, on=['ENTITY_CD', 'YEAR'], how='left')

if 'suspensions' in filtered_studed:
    suspensions = filtered_studed['suspensions'][['ENTITY_CD', 'YEAR', 'PER_SUSPENSIONS']]
    master = master.merge(suspensions, on=['ENTITY_CD', 'YEAR'], how='left')

#add county info from above mapping
entity_to_county = target_districts.set_index('DISTRICT_NAME')['COUNTY_NAME'].to_dict()
master['county'] = master['ENTITY_NAME'].map(entity_to_county)
master['county'] = master['county'].fillna('NYC')

#adding graduation data if available
if grad_all_students is not None:
    def standardize_district_name(name):
        if pd.isna(name):
            return name
        name = str(name).upper()
        replacements = {
            ' UNION FREE SCHOOL DISTRICT': ' UFSD',
            ' CENTRAL SCHOOL DISTRICT': ' CSD',
            ' CITY SCHOOL DISTRICT': ' CITY SD',
            ' COMMON SCHOOL DISTRICT': ' COMN SD',
            ' SCHOOL DISTRICT': ' SD'
        }
        for old, new in replacements.items():
            name = name.replace(old, new)
        return name
    
grad_all_students['lea_name_clean'] = grad_all_students['lea_name'].apply(standardize_district_name)
master['ENTITY_NAME_clean'] = master['ENTITY_NAME'].apply(standardize_district_name)

#create mapping from lea_name to graduation metrics
grad_summary = grad_all_students.groupby('lea_name_clean').agg({
    'grad_pct': 'mean',
    'dropout_pct': 'mean',
    'enroll_cnt': 'sum'
}).reset_index()

#merge with master (match on cleaned district)
master = master.merge(
    grad_summary,
    left_on='ENTITY_NAME_clean',
    right_on='lea_name_clean',
    how='left'
)
master = master.drop(['lea_name_clean', 'ENTITY_NAME_clean'], axis=1)
master = master.rename(columns={
    'grad_pct': 'graduation_rate',
    'dropout_pct': 'dropout_rate',
    'enroll_cnt': 'cohort_size'
})

merged_count = master['graduation_rate'].notna().sum()
print(f" Successfully merged graduation data for {merged_count}/{len(master)} records")

print(f"\n Master dataset shape: {master.shape}")
print(f" Columns: {master.columns.tolist()}")

#saving the master dataset
master.to_csv(OUTPUT_DIR / 'master_dataset.csv', index=False)

#summary stats
print("\n" +"="*70)
print("PROCESSING COMPLETE!")
print("="*70)
print(f"\nOutput files saved to: {OUTPUT_DIR}")
print("\nFiles created:")
print(" 1. target_districts.csv - District-county mapping")
print(" 2. enrollment_filtered.csv - Enrollment by grade")
print(" 3. demographics_filtered.csv - Race/ethnicity demographics")
print(" 4. *_filtered.csv - Various STUDED metrics")
print(" 5. graduation_filtered.csv - Graduation data (all subgroups)")
print(" 6. graduation_all_students.csv - Graduation data (all students only)")
print(" 7. master_dataset.csv - Combined key metrics")

print("\n" + "="*70)
print("MASTER DATASET SUMMARY")
print("="*70)
print(f"\nTotal records: {len(master)}")
print(f"\nRecords by county:")
print(master['county'].value_counts())
print(f"\nYears covered:")
print(master['YEAR'].value_counts().sort_index())
print(f"\nSample data:")
print(master.head(10))

print("\n" + "="*70)
print('NEXT STEP: Build Streamlit dashboard using master_dataset.csv')
print("="*70)
