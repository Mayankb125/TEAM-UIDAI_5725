import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

# Constants
CLEANED_DIR = r"d:/UIDAI data hackathon/cleaned_data"
OUTPUT_DIR = r"d:/UIDAI data hackathon/outputs"
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

MASTERS = {
    "Enrolment": "enrolment_master.csv",
    "Demographic": "demographic_master.csv"
}

def load_data():
    data = {}
    for name, f in MASTERS.items():
        path = os.path.join(CLEANED_DIR, f)
        if os.path.exists(path):
            print(f"Loading {name}...")
            df = pd.read_csv(path)
            # Ensure age columns are numeric
            cols = ['age_0_5', 'age_5_17', 'age_18_plus']
            for c in cols:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            data[name] = df
    return data

def calculate_uesi(data):
    print("Calculating UESI...")
    
    # 1. Aggregate Enrolments by District (Denominator Proxy)
    # We assume Total Adult Enrolments over time ~ Adult Population in system
    enrol = data['Enrolment']
    enrol_district = enrol.groupby(['state', 'district'])['age_18_plus'].sum().reset_index()
    enrol_district.rename(columns={'age_18_plus': 'total_adult_enrolments'}, inplace=True)
    
    # 2. Aggregate Returns/Updates by District (Numerator)
    # We focus on Demographic Updates for Adults as the "Stress" signal
    demo = data['Demographic']
    demo_district = demo.groupby(['state', 'district'])['age_18_plus'].sum().reset_index()
    demo_district.rename(columns={'age_18_plus': 'total_adult_updates'}, inplace=True)
    
    # 3. Merge
    merged = pd.merge(enrol_district, demo_district, on=['state', 'district'], how='inner')
    
    # 4. Calculate Raw UESI (Updates per 1000 Enrolments)
    # Avoid division by zero
    merged = merged[merged['total_adult_enrolments'] > 100] # Filter out tiny districts
    merged['uesi_raw'] = (merged['total_adult_updates'] / merged['total_adult_enrolments']) * 1000
    
    # 5. Normalize (Min-Max to 0-100 Scale)
    min_val = merged['uesi_raw'].min()
    max_val = merged['uesi_raw'].max()
    merged['UESI_Score'] = ((merged['uesi_raw'] - min_val) / (max_val - min_val)) * 100
    
    # Sort
    merged = merged.sort_values('UESI_Score', ascending=False)
    
    return merged

def plot_uesi_distribution(df):
    plt.figure(figsize=(10, 6))
    sns.histplot(df['UESI_Score'], bins=30, kde=True, color='salmon')
    plt.title('Distribution of UESI Scores across Districts')
    plt.xlabel('UESI Score (Normalized Stress Index)')
    plt.ylabel('Count of Districts')
    plt.axvline(df['UESI_Score'].mean(), color='red', linestyle='--', label='Mean')
    plt.legend()
    
    out_path = os.path.join(FIG_DIR, "uesi_distribution.png")
    plt.savefig(out_path)
    print(f"Saved distribution plot to {out_path}")
    plt.close()

def save_top_districts(df):
    # Top 20 Stressed
    top_20 = df.head(20)[['state', 'district', 'total_adult_enrolments', 'total_adult_updates', 'UESI_Score']]
    out_path = os.path.join(OUTPUT_DIR, "top_20_stressed_districts.csv")
    top_20.to_csv(out_path, index=False)
    print(f"Saved top 20 districts to {out_path}")
    
    # Save Full UESI Report
    full_path = os.path.join(OUTPUT_DIR, "uesi_all_districts.csv")
    df.to_csv(full_path, index=False)
    print(f"Saved full UESI data to {full_path}")

def main():
    data = load_data()
    if "Enrolment" not in data or "Demographic" not in data:
        print("Error: Missing required data files.")
        return
        
    uesi_df = calculate_uesi(data)
    
    print("\nTop 5 Stressed Districts:")
    print(uesi_df.head(5))
    
    plot_uesi_distribution(uesi_df)
    save_top_districts(uesi_df)

if __name__ == "__main__":
    main()
