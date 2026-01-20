import pandas as pd
import glob
import os

DATA_DIR = r"d:/UIDAI data hackathon/Data"

OUTPUT_FILE = "audit_result.txt"

def log(msg):
    print(msg)
    with open(OUTPUT_FILE, "a") as f:
        f.write(msg + "\n")

def audit_category(category_name, sub_folder):
    path = os.path.join(DATA_DIR, sub_folder)
    files = glob.glob(os.path.join(path, "*.csv"))
    log(f"\n--- Checking {category_name} ---")
    log(f"Found {len(files)} files.")
    
    if not files:
        log("WARNING: No files found!")
        return

    total_rows = 0
    first_file = True
    columns = []

    for f in files:
        try:
            df = pd.read_csv(f)
            total_rows += len(df)
            if first_file:
                columns = list(df.columns)
                log(f"Columns in {os.path.basename(f)}: {columns}")
                # log(f"Sample data:\n{df.head(2).to_string()}") # Skip sample data to verify columns first
                first_file = False
            else:
                # Check column consistency
                if list(df.columns) != columns:
                    log(f"ERROR: Column mismatch in {os.path.basename(f)}")
        except Exception as e:
            log(f"ERROR reading {f}: {e}")

    log(f"Total rows in {category_name}: {total_rows}")

def main():
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    if not os.path.exists(DATA_DIR):
        log(f"Data directory not found at {DATA_DIR}")
        return

    audit_category("Enrolment", "api_data_aadhar_enrolment")
    audit_category("Demographic Updates", "api_data_aadhar_demographic")
    audit_category("Biometric Updates", "api_data_aadhar_biometric")

if __name__ == "__main__":
    main()
