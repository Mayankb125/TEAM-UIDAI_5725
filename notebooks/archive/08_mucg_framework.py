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
    "Biometric": "biometric_master.csv"
}

def load_data():
    data = {}
    for name, f in MASTERS.items():
        path = os.path.join(CLEANED_DIR, f)
        if os.path.exists(path):
            print(f"Loading {name}...")
            df = pd.read_csv(path)
            cols = ['age_0_5', 'age_5_17', 'age_18_plus']
            for c in cols:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            data[name] = df
    return data

def calculate_mucg(data):
    print("Calculating MUCG...")
    
    # 1. Expected Updates (Denominator)
    # We look at child enrolments (0-5) as the base population that NEEDS update
    # Ideally, we'd lag this by 5 years, but we aggregate all available data as a simplified view
    enrol = data['Enrolment']
    # Filter for reasonable volume
    enrol_district = enrol.groupby(['state', 'district'])['age_0_5'].sum().reset_index()
    enrol_district.rename(columns={'age_0_5': 'child_enrolments_0_5'}, inplace=True)
    
    # 2. Actual Updates (Numerator)
    # Mandatory updates occur at 5 and 15. So we look at age 5-17 biometric updates.
    bio = data['Biometric']
    bio_district = bio.groupby(['state', 'district'])['age_5_17'].sum().reset_index()
    bio_district.rename(columns={'age_5_17': 'bio_updates_5_17'}, inplace=True)
    
    # 3. Merge
    merged = pd.merge(enrol_district, bio_district, on=['state', 'district'], how='inner')
    
    # 4. Compute Gap
    # Avoid tiny denominators
    merged = merged[merged['child_enrolments_0_5'] > 50]
    
    merged['compliance_ratio'] = merged['bio_updates_5_17'] / merged['child_enrolments_0_5']
    
    # Gap = 1 - Ratio. If Ratio > 1 (more updates than orig enrolments), Gap is 0.
    merged['MUCG_Score'] = 1 - merged['compliance_ratio']
    merged.loc[merged['MUCG_Score'] < 0, 'MUCG_Score'] = 0
    
    # Sort by Gap (High Gap = High Risk)
    merged = merged.sort_values('MUCG_Score', ascending=False)
    
    return merged

def plot_mucg_distribution(df):
    plt.figure(figsize=(10, 6))
    sns.histplot(df['MUCG_Score'], bins=30, kde=True, color='skyblue')
    plt.title('Distribution of Mandatory Update Compliance Gap (MUCG)')
    plt.xlabel('MUCG Score (0 = Fully Compliant, 1 = No Updates)')
    plt.ylabel('Count of Districts')
    plt.axvline(df['MUCG_Score'].mean(), color='blue', linestyle='--', label='Mean')
    plt.legend()
    
    out_path = os.path.join(FIG_DIR, "mucg_distribution.png")
    plt.savefig(out_path)
    print(f"Saved distribution plot to {out_path}")
    plt.close()

def save_high_risk_districts(df):
    # Top 20 High Gap
    top_20 = df.head(20)[['state', 'district', 'child_enrolments_0_5', 'bio_updates_5_17', 'MUCG_Score']]
    out_path = os.path.join(OUTPUT_DIR, "top_20_compliance_gap_districts.csv")
    top_20.to_csv(out_path, index=False)
    print(f"Saved top 20 gap districts to {out_path}")
    
    # Save Full
    full_path = os.path.join(OUTPUT_DIR, "mucg_all_districts.csv")
    df.to_csv(full_path, index=False)
    print(f"Saved full MUCG data to {full_path}")

def main():
    data = load_data()
    if "Enrolment" not in data or "Biometric" not in data:
        print("Error: Missing required data.")
        return
        
    mucg_df = calculate_mucg(data)
    
    print("\nTop 5 High Risk Districts (High Gap):")
    print(mucg_df.head(5))
    
    plot_mucg_distribution(mucg_df)
    save_high_risk_districts(mucg_df)

if __name__ == "__main__":
    main()
