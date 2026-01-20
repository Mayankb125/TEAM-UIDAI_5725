import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Constants
OUTPUT_DIR = r"d:/UIDAI data hackathon/outputs"
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

def load_frameworks():
    """Load UESI and Operational Resilience results"""
    print("Loading framework data...")
    
    uesi_path = os.path.join(OUTPUT_DIR, "uesi_all_districts.csv")
    resilience_path = os.path.join(OUTPUT_DIR, "operational_resilience.csv")
    
    uesi = pd.read_csv(uesi_path)
    resilience = pd.read_csv(resilience_path)
    
    print(f"Loaded UESI: {len(uesi)} districts")
    print(f"Loaded Resilience: {len(resilience)} districts")
    
    return uesi, resilience

def merge_frameworks(uesi, resilience):
    """Merge UESI and Resilience on state/district"""
    print("\nMerging frameworks...")
    
    # Merge on state and district
    merged = pd.merge(
        uesi[['state', 'district', 'UESI_Score']],
        resilience[['state', 'district', 'shock_intensity', 'volatility_score', 'resilience_tier']],
        on=['state', 'district'],
        how='inner'
    )
    
    print(f"Merged data: {len(merged)} districts")
    return merged

def classify_archetypes(df):
    """Classify districts into 4 archetypes using 2×2 matrix"""
    print("\nClassifying archetypes...")
    
    # Define thresholds
    uesi_median = df['UESI_Score'].median()
    
    def get_archetype(row):
        high_stress = row['UESI_Score'] > uesi_median
        high_shock = row['resilience_tier'] in ['Extreme Instability', 'High Instability']
        
        if not high_stress and not high_shock:
            return "Stable"
        elif not high_stress and high_shock:
            return "Hidden Risk"
        elif high_stress and not high_shock:
            return "Chronic Friction"
        else:
            return "Critical Priority"
    
    df['archetype'] = df.apply(get_archetype, axis=1)
    
    # Store threshold for reporting
    df.attrs['uesi_median'] = uesi_median
    
    return df

def plot_2x2_matrix(df):
    """Create 2×2 quadrant plot"""
    print("\nCreating 2×2 matrix plot...")
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Define archetype colors and order
    archetypes = ['Stable', 'Hidden Risk', 'Chronic Friction', 'Critical Priority']
    colors = {
        'Stable': '#2ecc71',           # Green
        'Hidden Risk': '#f39c12',      # Orange
        'Chronic Friction': '#3498db', # Blue
        'Critical Priority': '#e74c3c' # Red
    }
    
    # Plot each archetype
    for archetype in archetypes:
        subset = df[df['archetype'] == archetype]
        if len(subset) > 0:
            ax.scatter(
                subset['UESI_Score'], 
                subset['shock_intensity'],
                label=f"{archetype} (n={len(subset)})",
                color=colors[archetype],
                alpha=0.6,
                s=100,
                edgecolors='white',
                linewidth=0.5
            )
    
    # Add median lines to show quadrants
    uesi_median = df.attrs.get('uesi_median', df['UESI_Score'].median())
    
    # Determine shock threshold (boundary between High/Extreme and Moderate/Stable)
    shock_threshold = df[df['resilience_tier'].isin(['Moderate Volatility', 'Stable'])]['shock_intensity'].max()
    
    ax.axvline(uesi_median, color='black', linestyle='--', linewidth=1.5, alpha=0.7,
               label=f'UESI Median ({uesi_median:.1f})')
    ax.axhline(shock_threshold, color='black', linestyle='--', linewidth=1.5, alpha=0.7,
               label=f'Shock Threshold ({shock_threshold:.1f})')
    
    # Annotate quadrants
    x_mid = (df['UESI_Score'].min() + uesi_median) / 2
    x_high = (uesi_median + df['UESI_Score'].max()) / 2
    y_low = (df['shock_intensity'].min() + shock_threshold) / 2
    y_high = (shock_threshold + df['shock_intensity'].max()) / 2
    
    ax.text(x_mid, y_high, 'Hidden Risk\n(Surge Capacity)', 
            ha='center', va='center', fontsize=11, alpha=0.4, weight='bold')
    ax.text(x_high, y_high, 'Critical Priority\n(Comprehensive Fix)', 
            ha='center', va='center', fontsize=11, alpha=0.4, weight='bold')
    ax.text(x_mid, y_low, 'Stable\n(No Action)', 
            ha='center', va='center', fontsize=11, alpha=0.4, weight='bold')
    ax.text(x_high, y_low, 'Chronic Friction\n(Data Quality)', 
            ha='center', va='center', fontsize=11, alpha=0.4, weight='bold')
    
    ax.set_xlabel('UESI Score (Adult Stress)', fontsize=12, weight='bold')
    ax.set_ylabel('Shock Intensity (Peak/Median)', fontsize=12, weight='bold')
    ax.set_title('District Archetypes: Policy-Ready Classification', fontsize=14, weight='bold')
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    out_path = os.path.join(FIG_DIR, "district_archetypes_matrix.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved matrix plot to {out_path}")

def create_policy_table(df):
    """Create policy recommendation table"""
    print("\nGenerating policy recommendations...")
    
    # Define interventions for each archetype
    interventions = {
        'Stable': {
            'priority': 'Low',
            'intervention': 'Standard operations - no special action required',
            'resources': 'Routine maintenance',
            'timeline': 'Annual review'
        },
        'Hidden Risk': {
            'priority': 'Medium',
            'intervention': 'Deploy event-based surge capacity (mobile vans, temporary staff)',
            'resources': 'Flexible infrastructure, seasonal planning',
            'timeline': 'Quarterly monitoring, pre-event deployment'
        },
        'Chronic Friction': {
            'priority': 'Medium-High',
            'intervention': 'Data quality audits, operator retraining, enrollment validation',
            'resources': 'Training programs, quality control systems',
            'timeline': 'Immediate training, 6-month audit cycle'
        },
        'Critical Priority': {
            'priority': 'Critical',
            'intervention': 'Comprehensive overhaul: infrastructure + training + quality systems',
            'resources': 'Permanent center upgrades, dedicated staff, real-time monitoring',
            'timeline': 'Immediate intervention, intensive 3-month program'
        }
    }
    
    # Create policy table
    policy_data = []
    for archetype in ['Critical Priority', 'Chronic Friction', 'Hidden Risk', 'Stable']:
        count = len(df[df['archetype'] == archetype])
        pct = (count / len(df)) * 100
        
        policy_data.append({
            'Archetype': archetype,
            'Districts': count,
            'Percentage': f"{pct:.1f}%",
            'Priority': interventions[archetype]['priority'],
            'Intervention': interventions[archetype]['intervention'],
            'Resources': interventions[archetype]['resources'],
            'Timeline': interventions[archetype]['timeline']
        })
    
    policy_df = pd.DataFrame(policy_data)
    
    # Save to CSV
    out_path = os.path.join(OUTPUT_DIR, "policy_recommendations.csv")
    policy_df.to_csv(out_path, index=False)
    print(f"Saved policy table to {out_path}")
    
    return policy_df

def identify_case_studies(df):
    """Identify showcase districts from each archetype"""
    print("\nIdentifying case studies...")
    
    case_studies = {}
    
    for archetype in ['Stable', 'Hidden Risk', 'Chronic Friction', 'Critical Priority']:
        subset = df[df['archetype'] == archetype]
        
        if len(subset) == 0:
            continue
        
        if archetype == 'Critical Priority':
            # Highest combined risk (high UESI + high shock)
            case = subset.nlargest(2, ['UESI_Score', 'shock_intensity'])
        elif archetype == 'Hidden Risk':
            # Highest shock with low UESI
            case = subset.nlargest(2, 'shock_intensity')
        elif archetype == 'Chronic Friction':
            # Highest UESI with low shock
            case = subset.nlargest(2, 'UESI_Score')
        else:  # Stable
            # Most stable (lowest scores)
            case = subset.nsmallest(2, ['UESI_Score', 'shock_intensity'])
        
        case_studies[archetype] = case[['state', 'district', 'UESI_Score', 'shock_intensity', 'resilience_tier']]
    
    return case_studies

def save_results(df, policy_df, case_studies):
    """Save all results and print summary"""
    print("\n" + "="*70)
    print("DISTRICT ARCHETYPES: FINAL CLASSIFICATION")
    print("="*70)
    
    # Save main results
    out_path = os.path.join(OUTPUT_DIR, "district_archetypes.csv")
    df_sorted = df.sort_values(['archetype', 'UESI_Score'], ascending=[True, False])
    df_sorted.to_csv(out_path, index=False)
    print(f"\nSaved archetype data to {out_path}")
    
    # Print distribution
    print("\n" + "-"*70)
    print("ARCHETYPE DISTRIBUTION")
    print("-"*70)
    print(policy_df[['Archetype', 'Districts', 'Percentage', 'Priority']].to_string(index=False))
    
    # Print case studies
    print("\n" + "-"*70)
    print("CASE STUDIES (Showcase Districts)")
    print("-"*70)
    for archetype, cases in case_studies.items():
        print(f"\n{archetype.upper()}:")
        print(cases.to_string(index=False))
    
    # Print thresholds
    if 'uesi_median' in df.attrs:
        print("\n" + "-"*70)
        print("CLASSIFICATION THRESHOLDS")
        print("-"*70)
        print(f"  UESI Median (Stress Threshold): {df.attrs['uesi_median']:.2f}")
        print(f"  Shock Tier Threshold: High/Extreme Instability")

def main():
    print("="*70)
    print("DISTRICT ARCHETYPES FRAMEWORK")
    print("Synthesizing UESI + Operational Resilience")
    print("="*70)
    
    # Load data
    uesi, resilience = load_frameworks()
    
    # Merge
    merged = merge_frameworks(uesi, resilience)
    
    # Classify
    classified = classify_archetypes(merged)
    
    # Visualize
    plot_2x2_matrix(classified)
    
    # Policy recommendations
    policy_df = create_policy_table(classified)
    
    # Case studies
    case_studies = identify_case_studies(classified)
    
    # Save and summarize
    save_results(classified, policy_df, case_studies)
    
    print("\n" + "="*70)
    print("✅ DISTRICT ARCHETYPES FRAMEWORK COMPLETE!")
    print("="*70)

if __name__ == "__main__":
    main()
