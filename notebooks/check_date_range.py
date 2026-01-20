import pandas as pd
import os

CLEANED_DIR = r"d:/UIDAI data hackathon/cleaned_data"
MASTERS = [
    "enrolment_master.csv",
    "demographic_master.csv",
    "biometric_master.csv"
]

def check_dates():
    overall_min = None
    overall_max = None
    
    for f in MASTERS:
        path = os.path.join(CLEANED_DIR, f)
        if os.path.exists(path):
            try:
                # Read only chunks to be faster if files are huge, but they seem small enough based on prev output
                df = pd.read_csv(path)
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                    min_d = df['date'].min()
                    max_d = df['date'].max()
                    
                    print(f"File: {f}")
                    print(f"  Start: {min_d.strftime('%Y-%m-%d')}")
                    print(f"  End:   {max_d.strftime('%Y-%m-%d')}")
                    
                    if overall_min is None or min_d < overall_min: overall_min = min_d
                    if overall_max is None or max_d > overall_max: overall_max = max_d
            except Exception as e:
                print(f"Error reading {f}: {e}")

    if overall_min and overall_max:
        print("\n--- Overall Data Range ---")
        print(f"From: {overall_min.strftime('%Y-%m-%d')}")
        print(f"To:   {overall_max.strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    check_dates()
