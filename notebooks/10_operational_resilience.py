import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Constants
CLEANED_DIR = r"d:/UIDAI data hackathon/cleaned_data"
OUTPUT_DIR = r"d:/UIDAI data hackathon/outputs"
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

MASTERS = {
    "Enrolment": "enrolment_master.csv",
    "Demographic": "demographic_master.csv",
    "Biometric": "biometric_master.csv"
}

def load_data():
    """Load all master datasets with date parsing"""
    data = {}
    for name, filename in MASTERS.items():
        path = os.path.join(CLEANED_DIR, filename)
        if os.path.exists(path):
            print(f"Loading {name}...")
            df = pd.read_csv(path)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            data[name] = df
    return data

def calculate_daily_volume(df, category_name):
    """Calculate total daily volume per district"""
    age_cols = ['age_0_5', 'age_5_17', 'age_18_plus']
    available_cols = [col for col in age_cols if col in df.columns]
    
    df['total_volume'] = df[available_cols].sum(axis=1)
    
    # Group by district and date
    daily = df.groupby(['state', 'district', 'date'])['total_volume'].sum().reset_index()
    daily['category'] = category_name
    
    return daily

def calculate_resilience_metrics(daily_df):
    """Calculate shock, volatility, and recovery metrics for each district"""
    results = []
    
    for (state, district), group in daily_df.groupby(['state', 'district']):
        volumes = group['total_volume'].values
        
        if len(volumes) < 10:  # Need enough data points
            continue
        
        # Core Metrics
        median_vol = np.median(volumes)
        mean_vol = np.mean(volumes)
        peak_vol = np.max(volumes)
        std_vol = np.std(volumes)
        
        # Shock Intensity: How much does the peak exceed normal?
        shock_intensity = peak_vol / median_vol if median_vol > 0 else 0
        
        # Volatility Score: Coefficient of Variation (normalized std dev)
        volatility_score = (std_vol / mean_vol * 100) if mean_vol > 0 else 0
        
        # Recovery Time: Days to return to median after a spike
        recovery_days = calculate_recovery_time(volumes, median_vol)
        
        # Stability Score (inverse of volatility, 0-100 scale)
        stability_score = max(0, 100 - volatility_score)
        
        results.append({
            'state': state,
            'district': district,
            'median_daily_volume': median_vol,
            'peak_daily_volume': peak_vol,
            'shock_intensity': shock_intensity,
            'volatility_score': volatility_score,
            'stability_score': stability_score,
            'recovery_days': recovery_days,
            'data_points': len(volumes)
        })
    
    return pd.DataFrame(results)

def calculate_recovery_time(volumes, median_vol):
    """Calculate average recovery time after spikes"""
    recovery_times = []
    in_spike = False
    spike_start = 0
    
    for i, vol in enumerate(volumes):
        if vol > median_vol * 1.5:  # Define spike as 1.5x median
            if not in_spike:
                in_spike = True
                spike_start = i
        elif in_spike:
            recovery_times.append(i - spike_start)
            in_spike = False
    
    return np.mean(recovery_times) if recovery_times else 0

def classify_resilience(df):
    """Classify districts into resilience tiers using percentiles"""
    # Calculate percentiles for both metrics
    shock_95 = df['shock_intensity'].quantile(0.95)
    shock_80 = df['shock_intensity'].quantile(0.80)
    shock_60 = df['shock_intensity'].quantile(0.60)
    
    volatility_95 = df['volatility_score'].quantile(0.95)
    volatility_80 = df['volatility_score'].quantile(0.80)
    volatility_60 = df['volatility_score'].quantile(0.60)
    
    def get_tier(row):
        shock = row['shock_intensity']
        volatility = row['volatility_score']
        
        # Extreme: Top 5% in BOTH shock AND volatility
        if shock >= shock_95 and volatility >= volatility_95:
            return "Extreme Instability"
        
        # High: Top 20% in at least one metric
        elif shock >= shock_80 or volatility >= volatility_80:
            return "High Instability"
        
        # Moderate: Between 40-80th percentile
        elif shock >= shock_60 or volatility >= volatility_60:
            return "Moderate Volatility"
        
        # Stable: Bottom 60%
        else:
            return "Stable"
    
    df['resilience_tier'] = df.apply(get_tier, axis=1)
    
    # Store thresholds for reporting
    df.attrs['thresholds'] = {
        'shock_95': shock_95,
        'shock_80': shock_80,
        'volatility_95': volatility_95,
        'volatility_80': volatility_80
    }
    
    return df

def plot_resilience_scatter(df):
    """Create scatter plot of Shock vs Volatility with percentile tiers"""
    plt.figure(figsize=(14, 9))
    
    tiers = ['Extreme Instability', 'High Instability', 'Moderate Volatility', 'Stable']
    colors = {
        'Extreme Instability': '#d62728',  # Red
        'High Instability': '#ff7f0e',     # Orange
        'Moderate Volatility': '#2ca02c',  # Green
        'Stable': '#1f77b4'                # Blue
    }
    
    for tier in tiers:
        subset = df[df['resilience_tier'] == tier]
        if len(subset) > 0:
            plt.scatter(subset['shock_intensity'], subset['volatility_score'], 
                       label=f"{tier} (n={len(subset)})", 
                       color=colors.get(tier, 'gray'), alpha=0.6, s=80)
    
    # Add percentile threshold lines
    if 'thresholds' in df.attrs:
        thresholds = df.attrs['thresholds']
        plt.axvline(thresholds['shock_95'], color='red', linestyle='--', 
                   linewidth=1, alpha=0.5, label=f"95th %ile Shock ({thresholds['shock_95']:.1f})")
        plt.axhline(thresholds['volatility_95'], color='red', linestyle='--', 
                   linewidth=1, alpha=0.5, label=f"95th %ile Volatility ({thresholds['volatility_95']:.1f})")
    
    plt.xlabel('Shock Intensity (Peak / Median)', fontsize=12)
    plt.ylabel('Volatility Score (%)', fontsize=12)
    plt.title('Operational Resilience: Tiered Classification', fontsize=14, fontweight='bold')
    plt.legend(loc='upper right', fontsize=9)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    out_path = os.path.join(FIG_DIR, "resilience_scatter.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved scatter plot to {out_path}")

def plot_top_extreme_districts(df, n=20):
    """Plot top extreme instability districts"""
    extreme = df[df['resilience_tier'] == 'Extreme Instability'].sort_values('shock_intensity', ascending=False).head(n)
    
    if len(extreme) == 0:
        print("No Extreme Instability districts found")
        return
    
    plt.figure(figsize=(14, 10))
    y_pos = np.arange(len(extreme))
    
    # Create bars colored by shock intensity
    colors = plt.cm.Reds(extreme['shock_intensity'] / extreme['shock_intensity'].max())
    plt.barh(y_pos, extreme['shock_intensity'], color=colors, alpha=0.8)
    
    plt.yticks(y_pos, [f"{row['district']}, {row['state']}" for _, row in extreme.iterrows()], fontsize=9)
    plt.xlabel('Shock Intensity (Peak / Median)', fontsize=11)
    plt.title(f'Top {n} Districts: Extreme Operational Instability', fontweight='bold', fontsize=13)
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    
    out_path = os.path.join(FIG_DIR, "top_extreme_districts.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved extreme districts plot to {out_path}")

def save_results(df):
    """Save resilience results to CSV with summary statistics"""
    out_path = os.path.join(OUTPUT_DIR, "operational_resilience.csv")
    df_sorted = df.sort_values('shock_intensity', ascending=False)
    df_sorted.to_csv(out_path, index=False)
    print(f"Saved resilience data to {out_path}")
    
    # Summary stats
    print("\n=== OPERATIONAL RESILIENCE SUMMARY ===")
    tier_counts = df_sorted['resilience_tier'].value_counts()
    print("\nTier Distribution:")
    for tier in ['Extreme Instability', 'High Instability', 'Moderate Volatility', 'Stable']:
        count = tier_counts.get(tier, 0)
        pct = (count / len(df_sorted)) * 100
        print(f"  {tier}: {count} districts ({pct:.1f}%)")
    
    print(f"\n{'='*60}")
    print("TOP 10 DISTRICTS: EXTREME OPERATIONAL INSTABILITY")
    print(f"{'='*60}")
    extreme = df_sorted[df_sorted['resilience_tier'] == 'Extreme Instability'].head(10)
    print(extreme[['state', 'district', 'shock_intensity', 'volatility_score']].to_string(index=False))
    
    if 'thresholds' in df.attrs:
        thresholds = df.attrs['thresholds']
        print(f"\n{'='*60}")
        print("CLASSIFICATION THRESHOLDS (Percentiles)")
        print(f"{'='*60}")
        print(f"  95th Percentile Shock: {thresholds['shock_95']:.2f}")
        print(f"  80th Percentile Shock: {thresholds['shock_80']:.2f}")
        print(f"  95th Percentile Volatility: {thresholds['volatility_95']:.2f}%")
        print(f"  80th Percentile Volatility: {thresholds['volatility_80']:.2f}%")

def main():
    print("Starting Operational Resilience Analysis...")
    data = load_data()
    
    # Combine all categories to get total daily system load
    all_daily = []
    for name, df in data.items():
        daily = calculate_daily_volume(df, name)
        all_daily.append(daily)
    
    combined_daily = pd.concat(all_daily, ignore_index=True)
    
    # Aggregate across categories to get total district load per day
    district_daily = combined_daily.groupby(['state', 'district', 'date'])['total_volume'].sum().reset_index()
    
    # Calculate metrics
    resilience_df = calculate_resilience_metrics(district_daily)
    resilience_df = classify_resilience(resilience_df)
    
    # Visualize
    plot_resilience_scatter(resilience_df)
    plot_top_extreme_districts(resilience_df)
    
    # Save
    save_results(resilience_df)
    
    print("\n✅ Operational Resilience Framework Complete!")

if __name__ == "__main__":
    main()
