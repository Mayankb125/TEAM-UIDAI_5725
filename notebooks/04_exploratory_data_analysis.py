import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

CLEANED_DIR = r"d:/UIDAI data hackathon/cleaned_data"
FIG_DIR = r"d:/UIDAI data hackathon/outputs/figures"
OS_REPORT = r"d:/UIDAI data hackathon/eda_summary.md"

os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(os.path.dirname(OS_REPORT), exist_ok=True)

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

def plot_temporal_trends(data, f):
    f.write("## 1. Temporal Trends\n\n")
    plt.figure(figsize=(14, 6))
    
    for name, df in data.items():
        if 'date' not in df.columns: continue
        
        # Determine numeric metric columns
        if name == "Enrolment":
            cols = ['age_0_5', 'age_5_17', 'age_18_plus']
        elif name == "Demographic":
            cols = ['age_5_17', 'age_18_plus']
        elif name == "Biometric":
            cols = ['age_5_17', 'age_18_plus']
            
        # Sum daily
        daily = df.groupby('date')[cols].sum().sum(axis=1)
        # Resample monthly for smoother plot
        monthly = daily.resample('ME').sum()
        
        plt.plot(monthly.index, monthly.values, label=name, marker='o')
        
        f.write(f"- **{name} Peak**: {monthly.max():,.0f} in {monthly.idxmax().strftime('%b %Y')}\n")

    plt.title('Monthly Activity Trends (Enrolment vs Updates)')
    plt.xlabel('Date')
    plt.ylabel('Total Volume')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    out_path = os.path.join(FIG_DIR, "temporal_trends.png")
    plt.savefig(out_path)
    plt.close()
    f.write(f"\n![Temporal Trends]({out_path})\n\n")
    print("Saved temporal_trends.png")

def plot_age_distribution(data, f):
    f.write("## 2. Age Distribution\n\n")
    
    summary = []
    
    for name, df in data.items():
        if name == "Enrolment":
            cols = ['age_0_5', 'age_5_17', 'age_18_plus']
        else:
            cols = ['age_5_17', 'age_18_plus']
            
        totals = df[cols].sum()
        totals.name = name
        summary.append(totals)
        
    df_chem = pd.DataFrame(summary).T
    
    # Plot
    df_chem.plot(kind='bar', figsize=(10, 6))
    plt.title('Age-wise Distribution by Category')
    plt.ylabel('Total Volume')
    plt.xlabel('Age Group')
    plt.xticks(rotation=0)
    plt.grid(axis='y')
    plt.tight_layout()
    
    out_path = os.path.join(FIG_DIR, "age_distribution.png")
    plt.savefig(out_path)
    plt.close()
    
    f.write(f"\n![Age Distribution]({out_path})\n\n")
    f.write("### Raw Age Counts\n")
    f.write("```\n")
    f.write(df_chem.to_string() + "\n")
    f.write("```\n\n")
    print("Saved age_distribution.png")

def analyze_geography(data, f):
    f.write("## 3. Geographic Analysis\n\n")
    
    for name, df in data.items():
        if 'district' not in df.columns: continue
        
        if name == "Enrolment":
            cols = ['age_0_5', 'age_5_17', 'age_18_plus']
        else:
            cols = ['age_5_17', 'age_18_plus']
            
        df['total'] = df[cols].sum(axis=1)
        dist_stats = df.groupby('district')['total'].sum().sort_values(ascending=False)
        
        top_5 = dist_stats.head(5)
        bottom_5 = dist_stats[dist_stats > 0].tail(5) # Ignore actual 0s for bottom 5
        
        f.write(f"### {name} - Top 5 Districts\n")
        for d, v in top_5.items():
            f.write(f"- {d}: {v:,.0f}\n")
            
        f.write(f"\n### {name} - Bottom 5 Districts (Non-Zero)\n")
        for d, v in bottom_5.items():
            f.write(f"- {d}: {v:,.0f}\n")
        f.write("\n")

def main():
    print("Starting EDA...")
    data = load_data()
    
    with open(OS_REPORT, "w") as f:
        f.write("# Exploratory Data Analysis Report\n\n")
        
        plot_temporal_trends(data, f)
        plot_age_distribution(data, f)
        analyze_geography(data, f)
        
    print(f"EDA Complete. Report saved to {OS_REPORT}")

if __name__ == "__main__":
    main()
