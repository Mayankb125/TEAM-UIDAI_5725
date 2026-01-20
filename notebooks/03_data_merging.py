import pandas as pd
import glob
import os

CLEANED_DIR = r"d:/UIDAI data hackathon/cleaned_data"

CATEGORIES = {
    "enrolment": "enrolment_master.csv",
    "demographic_updates": "demographic_master.csv",
    "biometric_updates": "biometric_master.csv"
}

def merge_category(folder_name, output_filename):
    print(f"\n--- Merging {folder_name} ---")
    input_path = os.path.join(CLEANED_DIR, folder_name)
    files = glob.glob(os.path.join(input_path, "*.csv"))
    
    if not files:
        print("  No files found!")
        return

    dfs = []
    total_raw_rows = 0
    
    for f in files:
        try:
            df = pd.read_csv(f)
            dfs.append(df)
            total_raw_rows += len(df)
        except Exception as e:
            print(f"  Error reading {os.path.basename(f)}: {e}")
            
    if not dfs:
        return

    # Concatenate all files
    master_df = pd.concat(dfs, ignore_index=True)
    print(f"  Combined Rows (Pre-Dedup): {len(master_df)}")

    # GLOBAL DEDUPLICATION
    # This handles the user's concern about "data mixed in files" (overlap)
    before_dedup = len(master_df)
    master_df.drop_duplicates(inplace=True)
    after_dedup = len(master_df)
    
    if before_dedup - after_dedup > 0:
        print(f"  [OVERLAP DETECTED] Removed {before_dedup - after_dedup} rows that existed in multiple files.")
    else:
        print("  No overlap found between files.")

    # Sort for cleanliness
    sort_cols = [c for c in ['state', 'district', 'date'] if c in master_df.columns]
    if sort_cols:
        master_df.sort_values(by=sort_cols, inplace=True)

    # Save Master
    output_path = os.path.join(CLEANED_DIR, output_filename)
    master_df.to_csv(output_path, index=False)
    print(f"  Saved master to: {output_path}")
    print(f"  Final Master Rows: {len(master_df)}")

def main():
    for folder, outfile in CATEGORIES.items():
        merge_category(folder, outfile)

if __name__ == "__main__":
    main()
