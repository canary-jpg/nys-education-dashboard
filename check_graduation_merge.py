"""
Check why graduation data isn't merging with master dataset
"""

import pandas as pd 
from pathlib import Path

PROCESSED_DIR = Path('data/processed')

#load both graduation datasets
master = pd.read_csv(PROCESSED_DIR/ 'master_dataset.csv')
grad = pd.read_csv(PROCESSED_DIR / 'graduation_all_students.csv')

print("="*70)
print("GRADUATION MERGE DIAGNOSTIC")
print("="*70)

print("\nMaster dataset districts (first 10):")
print(master['ENTITY_NAME'].unique()[:10])
print(master['ENTITY_NAME'].unique()[:10])

print("\nGraduation dataset district (first 10):")
print(grad['lea_name'].unique()[:10])

#check for exact matches
master_districts = set(master['ENTITY_NAME'].unique())
grad_districts = set(grad['lea_name'].unique())

print(f"\n{len(master_districts)} unique districts in master")
print(f"\n{len(grad_districts)} unique districts in graduation data")

#find matches
matches = master_districts.intersection(grad_districts)
print(f"\n{len(matches)} districts match exactly")

#find non-matches
in_master_not_grad = master_districts - grad_districts
in_grad_not_master = grad_districts = master_districts

print(f'\nIn master but not in graduation ({len(in_master_not_grad)}):')
for dist in list(in_master_not_grad)[:10]:
    print(f" - {dist}")

print(f"\nIn graduation but not in master ({len(in_grad_not_master)}):")
for dist in list(in_grad_not_master)[:10]:
    print(f" - {dist}")

print(f"\n" + "="*70)
print("NYC CHECK")
print("="*70)
print("\nNYC in master:")
nyc_master = master[master['ENTITY_NAME'].str.contains('NYC', case=False, na=False)]
print(nyc_master[['ENTITY_NAME']].drop_duplicates())

print("\nNYC in graduation:")
nyc_grad = grad[grad['lea_name'].str.contains('NYC', case=False, na=False)]
print(nyc_grad[['lea_name']].drop_duplicates().head(10))

#suggesting a fix
print(f'\n' + '='*70)
print('SUGGESTED FIX')
print('='*70)
print("""
The district names don't match exactly between datasets.
We need to either:
1. Use ENTITY_CD instead (if available in graduation data)
2. Create a mapping table
3. Use fuzzy matching for district names
Let's check if ENTITY_CD exists in graduation data...
 """)

if 'aggregation_code' in grad.columns:
    print("\n 'aggregation_code' exists in graduation data")
    print(f"Sample values: {grad['aggregation_code'].head()}")
    print("\nWe can try matching on codes instead of names!")