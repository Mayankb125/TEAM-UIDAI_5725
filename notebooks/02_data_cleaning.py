import pandas as pd
import glob
import os
import numpy as np

CLEANED_DIR = r"d:/UIDAI data hackathon/cleaned_data"

CATEGORIES = {
    "enrolment": ["age_0_5", "age_5_17", "age_18_plus"],
    "demographic_updates": ["age_5_17", "age_18_plus"],
    "biometric_updates": ["age_5_17", "age_18_plus"]
}

def clean_file(filepath, numeric_cols):
    filename = os.path.basename(filepath)
    print(f"\nCleaning {filename}...")
    
    try:
        df = pd.read_csv(filepath)
        initial_rows = len(df)
        
        # 1. Convert Numeric Columns
        for col in numeric_cols:
            # Coerce errors to NaN, then fill with 0 or drop? 
            # "Do NOT impute" -> usually means don't guess values. 
            # If a count is non-numeric, it's likely bad data.
            # We will coerce to NaN and drop rows if ALL metrics are NaN, or assume 0?
            # Safer to coerce to numeric.
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # 2. Drop duplicates
        df.drop_duplicates(inplace=True)
        dedup_rows = len(df)
        if initial_rows - dedup_rows > 0:
            print(f"  Dropped {initial_rows - dedup_rows} duplicate rows")

        # 3. Drop missing geography
        # Critical: State, District
        # Pincode might be missing legitimately? Task says "Drop rows with missing critical geography (district/PIN)" -> Strict.
        crit_geo = ['state', 'district', 'pincode']
        before_geo = len(df)
        df.dropna(subset=crit_geo, inplace=True)
        after_geo = len(df)
        
        if before_geo - after_geo > 0:
            print(f"  Dropped {before_geo - after_geo} rows with missing geography")
            
        # 4. Filter out rows where all numeric metrics are 0 or NaN?
        # Sometimes a row exists but has 0 updates. That's valid info (0 updates).
        # But if all are NaN, it's useless.
        df.dropna(subset=numeric_cols, how='all', inplace=True)
        
        final_rows = len(df)
        print(f"  Final Rows: {final_rows} (Removed total {initial_rows - final_rows})")

        # Overwrite file
        df.to_csv(filepath, index=False)
        return True

    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def main():
    print("Starting Data Cleaning (Phase 1.3)...")
    
    for folder, metrics in CATEGORIES.items():
        path = os.path.join(CLEANED_DIR, folder)
        if not os.path.exists(path):
            print(f"Skipping {folder}, does not exist.")
            continue
            
        files = glob.glob(os.path.join(path, "*.csv"))
        print(f"\nProcessing {folder} ({len(files)} files)")
        
        for f in files:
            clean_file(f, metrics)

    print("\nData Cleaning Complete.")

if __name__ == "__main__":
    main()
