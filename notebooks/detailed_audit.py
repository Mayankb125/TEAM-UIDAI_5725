import pandas as pd
import glob
import os
import numpy as np

DATA_DIR = r"d:/UIDAI data hackathon/Data"
OUTPUT_REPORT = r"d:/UIDAI data hackathon/audit_notes.md"

def log(f, msg):
    print(msg)
    f.write(msg + "\n")

def check_date_column(df, filename, f):
    if 'date' in df.columns:
        try:
            # Attempt to parse dates
            pd.to_datetime(df['date'], format='%Y-%m-%d', errors='raise')
            # log(f, f"  [OK] Date format consistent.")
        except ValueError:
            log(f, f"  [!] Date format ISSUES in {filename}. checking unique formats...")
            # Simple check for mixed formats
            sample = df['date'].sample(min(len(df), 20)).tolist()
            log(f, f"      Samples: {sample}")
    else:
        log(f, f"  [!] 'date' column MISSING.")

def check_negatives(df, filename, f):
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if "pincode" in col.lower(): continue
        
        neg_count = (df[col] < 0).sum()
        if neg_count > 0:
            log(f, f"  [!] Found {neg_count} NEGATIVE values in column '{col}'")

def check_geography(df, filename, f):
    issues = []
    if 'state' in df.columns:
        null_state = df['state'].isnull().sum()
        if null_state > 0: issues.append(f"{null_state} missing states")
    
    if 'district' in df.columns:
        null_dist = df['district'].isnull().sum()
        if null_dist > 0: issues.append(f"{null_dist} missing districts")
        
    if 'pincode' in df.columns:
        null_pin = df['pincode'].isnull().sum()
        if null_pin > 0: issues.append(f"{null_pin} missing pincodes")
        
        # Check for non-numeric pincodes
        non_numeric_pin = pd.to_numeric(df['pincode'], errors='coerce').isnull().sum()
        if non_numeric_pin > 0: issues.append(f"{non_numeric_pin} non-numeric pincodes")

    if issues:
        log(f, f"  [!] Geography Issues: {', '.join(issues)}")

def audit_files(category_name, sub_folder, f):
    path = os.path.join(DATA_DIR, sub_folder)
    files = glob.glob(os.path.join(path, "*.csv"))
    
    log(f, f"\n### Auditing {category_name} ({len(files)} files)")
    
    for filepath in files:
        filename = os.path.basename(filepath)
        log(f, f"\n**File: {filename}**")
        
        try:
            df = pd.read_csv(filepath, low_memory=False) # low_memory=False to handle mixed types warning if any
            
            # 1. Date Checks
            check_date_column(df, filename, f)
            
            # 2. Negative/Zero Checks (Focus on Negatives per task)
            check_negatives(df, filename, f)
            
            # 3. Geography consistency (Missing values mostly, rigorous consistency is hard without master list)
            check_geography(df, filename, f)
            
        except Exception as e:
            log(f, f"  [CRITICAL] Error reading file: {e}")

def main():
    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        log(f, "# Data Audit Report")
        log(f, "Generated automatically by Detailed Audit Script\n")
        
        audit_files("Enrolment", "api_data_aadhar_enrolment", f)
        audit_files("Demographic Updates", "api_data_aadhar_demographic", f)
        audit_files("Biometric Updates", "api_data_aadhar_biometric", f)

    print(f"\nAudit complete. Report saved to {OUTPUT_REPORT}")

if __name__ == "__main__":
    main()
