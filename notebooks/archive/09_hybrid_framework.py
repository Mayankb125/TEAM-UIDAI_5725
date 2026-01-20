import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

# Constants
OUTPUT_DIR = r"d:/UIDAI data hackathon/outputs"
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

UESI_FILE = os.path.join(OUTPUT_DIR, "uesi_all_districts.csv")
MUCG_FILE = os.path.join(OUTPUT_DIR, "mucg_all_districts.csv")

def load_indices():
    if not os.path.exists(UESI_FILE) or not os.path.exists(MUCG_FILE):
        raise FileNotFoundError("UESI or MUCG files not found. Run previous steps first.")
    
    uesi = pd.read_csv(UESI_FILE)
    mucg = pd.read_csv(MUCG_FILE)
    
    # Keep only relevant columns for merge
    uesi_cols = ['state', 'district', 'UESI_Score']
    mucg_cols = ['state', 'district', 'MUCG_Score']
    
    merged = pd.merge(uesi[uesi_cols], mucg[mucg_cols], on=['state', 'district'], how='inner')
    return merged

def calculate_alvi(df):
    print("Calculating ALVI...")
    # ALVI = Average of Normalized UESI (0-100) and Normalized MUCG (0-1 -> 0-100)
    df['MUCG_Score_Scaled'] = df['MUCG_Score'] * 100
    
    df['ALVI_Score'] = (df['UESI_Score'] + df['MUCG_Score_Scaled']) / 2
    
    # Rank
    df = df.sort_values('ALVI_Score', ascending=False)
    return df

def assign_quadrants(df):
    # Determine thresholds (median or fixed)
    uesi_med = df['UESI_Score'].median()
    mucg_med = df['MUCG_Score_Scaled'].median()
    
    def get_quadrant(row):
        high_stress = row['UESI_Score'] > uesi_med
        high_gap = row['MUCG_Score_Scaled'] > mucg_med
        
        if high_stress and high_gap:
            return "Critical Priority" # High Stress, High Gap
        elif not high_stress and high_gap:
            return "Passive Risk" # Low Stress, High Gap (Silent Accumulation)
        elif high_stress and not high_gap:
            return "Operational Strain" # High Updates, Low Gap (System is working but stressed)
        else:
            return "Stable" # Low Stress, Low Gap
            
    df['Risk_Category'] = df.apply(get_quadrant, axis=1)
    return df

def plot_quadrant(df):
    plt.figure(figsize=(10, 8))
    sns.scatterplot(data=df, x='UESI_Score', y='MUCG_Score_Scaled', hue='Risk_Category', alpha=0.7)
    
    # Add median lines
    plt.axvline(df['UESI_Score'].median(), color='gray', linestyle='--')
    plt.axhline(df['MUCG_Score_Scaled'].median(), color='gray', linestyle='--')
    
    plt.title('Hybrid Risk Framework: Stress vs Compliance Gap')
    plt.xlabel('UESI Score (Update Stress)')
    plt.ylabel('MUCG Score (Compliance Gap - Scaled)')
    plt.legend(title='Risk Category')
    
    out_path = os.path.join(FIG_DIR, "risk_quadrant_plot.png")
    plt.savefig(out_path)
    print(f"Saved quadrant plot to {out_path}")
    plt.close()

def save_results(df):
    out_path = os.path.join(OUTPUT_DIR, "alvi_final_ranking.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved ALVI ranking to {out_path}")

def main():
    try:
        df = load_indices()
        df = calculate_alvi(df)
        df = assign_quadrants(df)
        
        print("\nTop 5 Most Vulnerable Districts (ALVI):")
        print(df.head(5))
        
        plot_quadrant(df)
        save_results(df)
        
    except Exception as e:
        print(f"Error in Hybrid Framework: {e}")

if __name__ == "__main__":
    main()
