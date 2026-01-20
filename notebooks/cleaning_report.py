import pandas as pd
import glob
import os

RAW_DIR = r"d:/UIDAI data hackathon/Data"
CLEANED_DIR = r"d:/UIDAI data hackathon/cleaned_data"
OUTPUT_FILE = "cleaning_report.txt"

# Mapping raw subfolders to cleaned subfolders
MAPPING = {
    "api_data_aadhar_enrolment": "enrolment",
    "api_data_aadhar_demographic": "demographic_updates",
    "api_data_aadhar_biometric": "biometric_updates"
}

with open(OUTPUT_FILE, "w") as f:
    header = f"{'Category':<25} | {'File':<45} | {'Raw Rows':<10} | {'Cleaned Rows':<12} | {'Dropped':<10}\n"
    f.write(header)
    print(header.strip())
    
    sep = "-" * 110 + "\n"
    f.write(sep)
    print(sep.strip())

    total_dropped = 0
    
    for raw_sub, cleaned_sub in MAPPING.items():
        raw_path = os.path.join(RAW_DIR, raw_sub)
        clean_path = os.path.join(CLEANED_DIR, cleaned_sub)
        
        if not os.path.exists(raw_path): continue
        
        files = glob.glob(os.path.join(raw_path, "*.csv"))
        
        for raw_f in files:
            filename = os.path.basename(raw_f)
            clean_f = os.path.join(clean_path, filename)
            
            if os.path.exists(clean_f):
                try:
                    df_raw = pd.read_csv(raw_f, usecols=[0])
                    df_clean = pd.read_csv(clean_f, usecols=[0])
                    
                    raw_count = len(df_raw)
                    clean_count = len(df_clean)
                    dropped = raw_count - clean_count
                    total_dropped += dropped
                    
                    category = cleaned_sub.replace("_updates", "").capitalize()
                    line = f"{category:<25} | {filename:<45} | {raw_count:<10} | {clean_count:<12} | {dropped:<10}\n"
                    f.write(line)
                    print(line.strip())
                except Exception as e:
                    print(f"Error reading {filename}: {e}")

    f.write("-" * 110 + "\n")
    f.write(f"Total Rows Dropped across all files: {total_dropped}\n")
    print(f"Total Rows Dropped across all files: {total_dropped}")
