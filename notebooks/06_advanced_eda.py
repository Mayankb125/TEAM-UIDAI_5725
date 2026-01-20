import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from statsmodels.tsa.seasonal import seasonal_decompose

CLEANED_DIR = r"d:/UIDAI data hackathon/cleaned_data"
FIG_DIR = r"d:/UIDAI data hackathon/outputs/figures"
OS_REPORT = r"d:/UIDAI data hackathon/advanced_eda_report.md"

os.makedirs(FIG_DIR, exist_ok=True)

MASTERS = {
    "Enrolment": "enrolment_master.csv",
    "Demographic": "demographic_master.csv",
    "Biometric": "biometric_master.csv"
}

def load_data():
    data = {}
    for name, f in MASTERS.items():
        path = os.path.join(CLEANED_DIR, f)
        if os.path.exists(path):
            print(f"Loading {name}...")
            df = pd.read_csv(path)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            data[name] = df
    return data

def plot_churn_heatmap(data, f):
    f.write("## 1. State-Age Churn Heatmap\n\n")
    
    # Combine all data to get total activity by State & Age
    # We focus on Updates (Demographic + Biometric) as "Churn"
    
    demo = data['Demographic'][['state', 'age_5_17', 'age_18_plus']].copy()
    bio = data['Biometric'][['state', 'age_5_17', 'age_18_plus']].copy()
    
    # Sum by state
    demo_grp = demo.groupby('state').sum()
    bio_grp = bio.groupby('state').sum()
    
    # Combine
    combined = demo_grp.add(bio_grp, fill_value=0)
    # Rename for clarity
    combined.columns = ['Child_Updates (5-17)', 'Adult_Updates (18+)']
    
    # Normalize Row-wise (Percentage of that state's work)
    # This shows "Archetype" of the state
    combined_pct = combined.div(combined.sum(axis=1), axis=0) * 100
    
    # Filter out low-volume states for cleaner plot (optional, or just plot all)
    # Let's keep all but sort by Adult %
    combined_pct = combined_pct.sort_values('Adult_Updates (18+)', ascending=False)
    
    plt.figure(figsize=(10, 12))
    sns.heatmap(combined_pct, annot=True, cmap="YlOrRd", fmt=".1f")
    plt.title('State-wise Update Intensity: Who are they updating?')
    plt.xlabel('Age Group')
    plt.ylabel('State')
    plt.tight_layout()
    
    out_path = os.path.join(FIG_DIR, "churn_heatmap.png")
    plt.savefig(out_path)
    plt.close()
    
    f.write(f"![Churn Heatmap]({out_path})\n\n")
    f.write("> **Insight**: States with high 'Child' intensity are managing school-age compliance. States with high 'Adult' intensity are dealing with migration/correction.\n\n")
    print("Saved churn_heatmap.png")

def analyze_seasonality(data, f):
    f.write("## 2. Seasonality Decomposition (Biometric Updates)\n\n")
    
    df = data['Biometric']
    if 'date' not in df.columns: return

    # Daily sum
    daily = df.groupby('date')[['age_5_17', 'age_18_plus']].sum().sum(axis=1)
    
    # Resample to Monthly
    monthly = daily.resample('ME').sum()
    
    # Fill missing values if any
    monthly = monthly.fillna(method='ffill')

    # Decompose (Period = 12 months)
    # We need at least 2 cycles (24 months) for robust seasonality, 
    # but let's try with what we have or set period smaller if data is short.
    # Check length
    if len(monthly) < 24:
        f.write(f"**Note**: Data duration ({len(monthly)} months) is short for full yearly seasonality analysis, but we will attempt decomposition.\n")
    
    try:
        decomposition = seasonal_decompose(monthly, model='additive', period=12)
        
        plt.figure(figsize=(12, 10))
        decomposition.plot()
        plt.suptitle('Seasonality Decomposition: Biometric Updates', fontsize=16)
        plt.tight_layout()
        
        out_path = os.path.join(FIG_DIR, "seasonality_decomposition.png")
        plt.savefig(out_path) # statsmodels plot() returns figure, but sometimes need to save current fig
        plt.close() 

        # Hack because decomposition.plot() creates its own figure
        # We need to save the *current* figure after calling plot()
        # Actually statsmodels.plot() displays it. 
        # Safer way:
        fig = decomposition.plot()
        fig.set_size_inches(12, 10)
        fig.savefig(out_path)
        fig.clf()
        
        f.write(f"![Seasonality]({out_path})\n\n")
        f.write("> **Trend**: Shows the underlying growth/decline.\n")
        f.write("> **Seasonal**: Shows the repeating 'July Pattern'.\n")
        f.write("> **Residual**: Random noise.\n\n")
        print("Saved seasonality_decomposition.png")
        
    except Exception as e:
        f.write(f"Could not perform decomposition: {e}\n")
        print(f"Decomposition Error: {e}")

def main():
    print("Starting Advanced EDA...")
    data = load_data()
    
    with open(OS_REPORT, "w") as f:
        f.write("# Advanced EDA Report\n\n")
        try:
            plot_churn_heatmap(data, f)
            analyze_seasonality(data, f)
        except Exception as e:
            print(f"Analysis Error: {e}")
            f.write(f"\nError: {e}")
            
    print(f"Advanced EDA Complete. Report saved to {OS_REPORT}")

if __name__ == "__main__":
    main()
