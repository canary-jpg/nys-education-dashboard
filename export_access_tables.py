"""
Export all tables from access databases to CSV files
Making them easier to work with in pandas
"""

import subprocess
from pathlib import Path 

DATA_DIR = Path('data/raw')
PROCESSED_DIR = Path('data/processed')
PROCESSED_DIR.mkdir(exist_ok=True)

def list_tables(db_path):
    """ List all tables in an Access database"""
    try:
        cmd = f'mdb-tables -1 "{str(db_path)}"'
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        tables = [t.strip() for t in result.stdout.strip().split('\n') if t.strip()]
        return tables
    except Exception as e:
        print(f"Error listing tables: {e}")
        return []

def export_table(db_path, table_name, output_path):
    """ Export a single table to CSV"""
    try:
        cmd = f'mdb-export "{str(db_path)}" "{table_name}" > "{str(output_path)}"'
        subprocess.run(cmd, shell=True, check=True)
        print(f"{table_name} -> {output_path.name}")
        return True
    except Exception as e:
        print(f"Failed to export {table_name}: {e}")
        return False 

def export_all_tables(db_path, prefix):
    """ Export all tables from a database"""
    print(f"\n{'='*60}")
    print(f"Processing: {db_path.name}")
    print('='*60)
    tables = list_tables(db_path)
    print(f"Found {len(tables)} tables: {tables}\n")

    for table in tables:
        clean_name = table.replace(' ', '_').replace('/', '_').replace('&', 'and')
        output_file = PROCESSED_DIR / f"{prefix}_{clean_name}.csv"
        export_table(db_path, table, output_file)

#export from both databases
if __name__ == '__main__':
    print("Exporting Access database tables to CSV...")


    #enrollment database
    enroll_db = DATA_DIR  / 'ENROLL2024_20241105.accdb'
    if enroll_db.exists():
        export_all_tables(enroll_db, 'ENROLL')
    else:
        print(f"Not found: {enroll_db}")
    
    #student/district database
    studed_db = DATA_DIR / 'STUDED_2024.accdb'
    if studed_db.exists():
        export_all_tables(studed_db, 'STUDED')
    else:
        print(f"Not found: {studed_db}")

    #graduation database
    grad_db = DATA_DIR / '2024_GRADUATION_RATE.mdb'
    if grad_db.exists():
        export_all_tables(grad_db, 'GRAD')
    else:
        print(f"Not Found: {grad_db}")

    print(f"\n{'='*60}")
    print("Done! All tables exported to:" ,PROCESSED_DIR)
    print('='*60)