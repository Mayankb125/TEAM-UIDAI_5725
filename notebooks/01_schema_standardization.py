import pandas as pd
import glob
import os

DATA_DIR = r"d:/UIDAI data hackathon/Data"
CLEANED_DIR = r"d:/UIDAI data hackathon/cleaned_data"

# Mapping for standardization across categories
# Key: (Category Name, Subfolder)
# Value: Column rename dictionary
SCHEMA_MAPPINGS = {
    "Enrolment": {
        "subfolder": "api_data_aadhar_enrolment",
        "rename_map": {
            "age_18_greater": "age_18_plus",
            "age_18_": "age_18_plus", # Potential variant
            "State": "state",
            "District": "district",
            "Pincode": "pincode",
            "Date": "date"
        },
        "target_cols": ["date", "state", "district", "pincode", "age_0_5", "age_5_17", "age_18_plus"]
    },
    "Demographic Updates": {
        "subfolder": "api_data_aadhar_demographic",
        "rename_map": {
            "demo_age_5_17": "age_5_17",
            "demo_age_17_": "age_18_plus",
            "demo_age_18_": "age_18_plus",
            "State": "state",
            "District": "district",
            "Pincode": "pincode",
            "Date": "date"
        },
        "target_cols": ["date", "state", "district", "pincode", "age_5_17", "age_18_plus"]
    },
    "Biometric Updates": {
        "subfolder": "api_data_aadhar_biometric",
        "rename_map": {
            "bio_age_5_17": "age_5_17",
            "bio_age_17_": "age_18_plus",
            "bio_age_18_": "age_18_plus",
            "State": "state",
            "District": "district",
            "Pincode": "pincode",
            "Date": "date"
        },
        "target_cols": ["date", "state", "district", "pincode", "age_5_17", "age_18_plus"]
    }
}

def standardize_category(name, config):
    print(f"\n--- Standardising {name} ---")
    path = os.path.join(DATA_DIR, config["subfolder"])
    files = glob.glob(os.path.join(path, "*.csv"))
    
    for filepath in files:
        filename = os.path.basename(filepath)
        try:
            df = pd.read_csv(filepath, low_memory=False)
            original_cols = list(df.columns)
            
            # 1. Rename Columns
            df.rename(columns=config["rename_map"], inplace=True)
            
            # 2. Standardize Date
            if 'date' in df.columns:
                # Convert 'DD-MM-YYYY' or other formats to 'YYYY-MM-DD'
                # errors='coerce' will make invalid dates NaT, verifying consistency
                df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')
            
            # Verify basic schema
            current_cols = list(df.columns)
            missing = [c for c in config["target_cols"] if c not in current_cols]
            
            print(f"File: {filename}")
            print(f"  Orig Cols: {original_cols}")
            print(f"  New Cols : {current_cols}")
            if missing:
                print(f"  [!] MISSING TARGET COLS: {missing}")
            else:
                print(f"  [OK] Schema Verified")
            
            # Check Date Sample
            if 'date' in df.columns:
                print(f"  Date Sample: {df['date'].dropna().head(3).tolist()}")

            # SAVE FILE
            # out_subdir = os.path.join(CLEANED_DIR, config["subfolder_key"]) # ERROR HERE
            # User wants: cleaned_data/enrolment, cleaned_data/demographic_updates etc matching task.md
            # Task.md says: cleaned_data/enrolment, cleaned_data/demographic_updates, cleaned_data/biometric_updates
            
            # Map subfolder to cleaned folder name
            folder_map = {
                "api_data_aadhar_enrolment": "enrolment",
                "api_data_aadhar_demographic": "demographic_updates",
                "api_data_aadhar_biometric": "biometric_updates"
            }
            target_folder = folder_map.get(config["subfolder"], "misc")
            
            out_path = os.path.join(CLEANED_DIR, target_folder)
            os.makedirs(out_path, exist_ok=True)
            
            out_file = os.path.join(out_path, filename)
            df.to_csv(out_file, index=False)
            print(f"  [SAVED] {out_file}")

        except Exception as e:
            print(f"  [ERROR] {e}")

def main():
    for category, config in SCHEMA_MAPPINGS.items():
        standardize_category(category, config)

if __name__ == "__main__":
    main()
