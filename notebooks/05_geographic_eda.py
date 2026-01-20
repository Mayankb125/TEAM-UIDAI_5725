import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

CLEANED_DIR = r"d:/UIDAI data hackathon/cleaned_data"
FIG_DIR = r"d:/UIDAI data hackathon/outputs/figures"
OS_REPORT = r"d:/UIDAI data hackathon/geographic_eda.md"

os.makedirs(FIG_DIR, exist_ok=True)

MASTERS = {
    "Enrolment": "enrolment_master.csv",
    "Demographic": "demographic_master.csv",
    "Biometric": "biometric_master.csv"
}

def load_district_totals():
    combined = None
    
    for name, f in MASTERS.items():
        path = os.path.join(CLEANED_DIR, f)
        if not os.path.exists(path): continue
        
        df = pd.read_csv(path)
        
        # Determine total column
        if name == "Enrolment":
            cols = ['age_0_5', 'age_5_17', 'age_18_plus']
        else:
            cols = ['age_5_17', 'age_18_plus']
            
        df['total'] = df[cols].sum(axis=1)
        
        # Group by district
        dist_total = df.groupby('district')['total'].sum().reset_index()
        dist_total.rename(columns={'total': f'{name}_Volume'}, inplace=True)
        
        if combined is None:
            combined = dist_total
        else:
            combined = pd.merge(combined, dist_total, on='district', how='outer').fillna(0)
            
    return combined

def analyze_geo_patterns(df, f):
    f.write("## Geographic Update Intensity\n\n")
    
    # Calculate Total Updates
    df['Total_Updates'] = df['Demographic_Volume'] + df['Biometric_Volume']
    
    # Calculate Updates per Enrolment (Proxy for "Maintenance Load")
    # Avoid division by zero
    df['Update_Density'] = df['Total_Updates'] / df['Enrolment_Volume'].replace(0, 1)
    
    # Sort by Density (ignoring low volume noise)
    # Filter: at least 1000 enrolments to be significant
    significant = df[df['Enrolment_Volume'] > 1000].copy()
    
    top_density = significant.sort_values(by='Update_Density', ascending=False).head(10)
    
    f.write("### Top 10 High-Maintenance Districts (Updates per Enrolment)\n")
    f.write("| District | Enrolments | Updates | Ratio |\n")
    f.write("| :--- | :--- | :--- | :--- |\n")
    for _, row in top_density.iterrows():
        f.write(f"| {row['district']} | {row['Enrolment_Volume']:,.0f} | {row['Total_Updates']:,.0f} | {row['Update_Density']:.2f} |\n")
        
    f.write("\n> **Insight**: Districts with high ratios usually indicate high migration or frequent data correction needs.\n\n")
    
    return significant

def plot_geo_scatter(df, f):
    f.write("## Enrolment vs Update Volume\n\n")
    
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='Enrolment_Volume', y='Total_Updates', alpha=0.6)
    
    plt.title('District-wise: Enrolment Volume vs Update Volume')
    plt.xlabel('Total Enrolments')
    plt.ylabel('Total Updates (Bio + Demo)')
    plt.grid(True)
    
    # Annotate top outliers
    top_districts = df.sort_values('Total_Updates', ascending=False).head(3)
    for _, row in top_districts.iterrows():
        plt.text(row['Enrolment_Volume'], row['Total_Updates'], row['district'], 
                 fontsize=9, ha='right', color='black', weight='bold')

    out_path = os.path.join(FIG_DIR, "geo_scatter.png")
    plt.savefig(out_path)
    plt.close()
    
    f.write(f"![Enrolment vs Updates]({out_path})\n\n")
    print("Saved geo_scatter.png")

def main():
    print("Starting Geographic EDA...")
    df = load_district_totals()
    
    with open(OS_REPORT, "w") as f:
        f.write("# Geographic EDA Report\n\n")
        significant_df = analyze_geo_patterns(df, f)
        plot_geo_scatter(significant_df, f)
        
    print(f"Geographic EDA Complete. Saved to {OS_REPORT}")

if __name__ == "__main__":
    main()
