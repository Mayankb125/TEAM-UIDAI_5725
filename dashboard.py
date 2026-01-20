import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io
from datetime import datetime

# Page config
st.set_page_config(
    page_title="UIDAI Operational Intelligence Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">🔍 UIDAI Operational Intelligence Dashboard</div>', unsafe_allow_html=True)
st.markdown("### Aadhaar Lifecycle Stress & Compliance Risk Framework")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📁 Data Upload")
    st.markdown("Upload your CSV files to analyze district-level operational metrics.")
    
    enrolment_file = st.file_uploader("Enrolment Data", type=['csv'], key='enrolment')
    demographic_file = st.file_uploader("Demographic Updates", type=['csv'], key='demographic')
    biometric_file = st.file_uploader("Biometric Updates", type=['csv'], key='biometric')
    
    st.markdown("---")
    st.markdown("### 📊 Framework Modules")
    show_uesi = st.checkbox("UESI (Adult Stress)", value=True)
    show_resilience = st.checkbox("Operational Resilience", value=True)
    show_archetypes = st.checkbox("District Archetypes", value=True)
    
    analyze_button = st.button("🚀 Run Analysis", type="primary", use_container_width=True)


# Helper Functions
@st.cache_data
def load_and_validate_csv(file):
    """Load and validate CSV file"""
    try:
        df = pd.read_csv(file)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        return df, None
    except Exception as e:
        return None, str(e)


def calculate_uesi(enrolment_df, demographic_df):
    """Calculate UESI scores"""
    # Aggregate adult data
    enrol_adult = enrolment_df.groupby(['state', 'district'])['age_18_plus'].sum().reset_index()
    enrol_adult.rename(columns={'age_18_plus': 'total_adult_enrolments'}, inplace=True)
    
    demo_adult = demographic_df.groupby(['state', 'district'])['age_18_plus'].sum().reset_index()
    demo_adult.rename(columns={'age_18_plus': 'total_adult_updates'}, inplace=True)
    
    # Merge
    merged = pd.merge(enrol_adult, demo_adult, on=['state', 'district'], how='inner')
    merged = merged[merged['total_adult_enrolments'] > 100]
    
    # Calculate UESI
    merged['uesi_raw'] = (merged['total_adult_updates'] / merged['total_adult_enrolments']) * 1000
    
    # Normalize to 0-100
    min_val = merged['uesi_raw'].min()
    max_val = merged['uesi_raw'].max()
    merged['UESI_Score'] = ((merged['uesi_raw'] - min_val) / (max_val - min_val)) * 100
    
    return merged.sort_values('UESI_Score', ascending=False)


def calculate_resilience(enrolment_df, demographic_df, biometric_df):
    """Calculate Operational Resilience metrics"""
    # Combine all data sources for daily volume
    all_dfs = []
    
    for df, name in [(enrolment_df, 'Enrolment'), (demographic_df, 'Demographic'), (biometric_df, 'Biometric')]:
        age_cols = ['age_0_5', 'age_5_17', 'age_18_plus']
        available_cols = [col for col in age_cols if col in df.columns]
        df_copy = df.copy()
        df_copy['total_volume'] = df_copy[available_cols].sum(axis=1)
        daily = df_copy.groupby(['state', 'district', 'date'])['total_volume'].sum().reset_index()
        all_dfs.append(daily)
    
    # Combine and aggregate
    combined = pd.concat(all_dfs, ignore_index=True)
    district_daily = combined.groupby(['state', 'district', 'date'])['total_volume'].sum().reset_index()
    
    # Calculate metrics per district
    results = []
    for (state, district), group in district_daily.groupby(['state', 'district']):
        volumes = group['total_volume'].values
        
        if len(volumes) < 10:
            continue
        
        median_vol = np.median(volumes)
        peak_vol = np.max(volumes)
        std_vol = np.std(volumes)
        mean_vol = np.mean(volumes)
        
        shock_intensity = peak_vol / median_vol if median_vol > 0 else 0
        volatility_score = (std_vol / mean_vol * 100) if mean_vol > 0 else 0
        
        results.append({
            'state': state,
            'district': district,
            'shock_intensity': shock_intensity,
            'volatility_score': volatility_score,
            'median_daily_volume': median_vol,
            'peak_daily_volume': peak_vol
        })
    
    df = pd.DataFrame(results)
    
    # Classify into tiers
    shock_95 = df['shock_intensity'].quantile(0.95)
    shock_80 = df['shock_intensity'].quantile(0.80)
    vol_95 = df['volatility_score'].quantile(0.95)
    vol_80 = df['volatility_score'].quantile(0.80)
    
    def get_tier(row):
        if row['shock_intensity'] >= shock_95 and row['volatility_score'] >= vol_95:
            return "Extreme Instability"
        elif row['shock_intensity'] >= shock_80 or row['volatility_score'] >= vol_80:
            return "High Instability"
        elif row['shock_intensity'] >= df['shock_intensity'].quantile(0.60):
            return "Moderate Volatility"
        else:
            return "Stable"
    
    df['resilience_tier'] = df.apply(get_tier, axis=1)
    
    return df.sort_values('shock_intensity', ascending=False)


def create_archetypes(uesi_df, resilience_df):
    """Create district archetypes"""
    merged = pd.merge(
        uesi_df[['state', 'district', 'UESI_Score']],
        resilience_df[['state', 'district', 'shock_intensity', 'resilience_tier']],
        on=['state', 'district'],
        how='inner'
    )
    
    uesi_median = merged['UESI_Score'].median()
    
    def get_archetype(row):
        high_stress = row['UESI_Score'] > uesi_median
        high_shock = row['resilience_tier'] in ['Extreme Instability', 'High Instability']
        
        if high_stress and high_shock:
            return "Critical Priority"
        elif high_stress and not high_shock:
            return "Chronic Friction"
        elif not high_stress and high_shock:
            return "Hidden Risk"
        else:
            return "Stable"
    
    merged['archetype'] = merged.apply(get_archetype, axis=1)
    
    return merged


# Main Analysis Logic
if analyze_button:
    if not all([enrolment_file, demographic_file, biometric_file]):
        st.error("⚠️ Please upload all three CSV files (Enrolment, Demographic, Biometric)")
    else:
        with st.spinner("🔄 Loading and validating data..."):
            enrol_df, enrol_error = load_and_validate_csv(enrolment_file)
            demo_df, demo_error = load_and_validate_csv(demographic_file)
            bio_df, bio_error = load_and_validate_csv(biometric_file)
            
            if any([enrol_error, demo_error, bio_error]):
                st.error(f"Error loading files: {enrol_error or demo_error or bio_error}")
            else:
                st.success("✅ Data loaded successfully!")
                
                # Tabs for different analyses
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔥 UESI Analysis", "⚡ Resilience Analysis", "🎯 District Archetypes"])
                
                # Run analyses
                with st.spinner("🧮 Running UESI analysis..."):
                    uesi_results = calculate_uesi(enrol_df, demo_df)
                
                with st.spinner("🧮 Running Resilience analysis..."):
                    resilience_results = calculate_resilience(enrol_df, demo_df, bio_df)
                
                with st.spinner("🧮 Creating District Archetypes..."):
                    archetype_results = create_archetypes(uesi_results, resilience_results)
                
                # Overview Tab
                with tab1:
                    st.header("📊 Analysis Overview")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Districts Analyzed", len(archetype_results))
                    
                    with col2:
                        critical_count = len(archetype_results[archetype_results['archetype'] == 'Critical Priority'])
                        st.metric("Critical Priority", critical_count, delta=f"{(critical_count/len(archetype_results)*100):.1f}%")
                    
                    with col3:
                        extreme_count = len(resilience_results[resilience_results['resilience_tier'] == 'Extreme Instability'])
                        st.metric("Extreme Instability", extreme_count)
                    
                    with col4:
                        avg_uesi = uesi_results['UESI_Score'].mean()
                        st.metric("Avg UESI Score", f"{avg_uesi:.1f}")
                    
                    st.markdown("---")
                    
                    # Archetype distribution
                    st.subheader("District Archetype Distribution")
                    archetype_counts = archetype_results['archetype'].value_counts()
                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    colors = {'Critical Priority': '#e74c3c', 'Chronic Friction': '#3498db', 
                             'Hidden Risk': '#f39c12', 'Stable': '#2ecc71'}
                    archetype_counts.plot(kind='bar', color=[colors.get(x, 'gray') for x in archetype_counts.index], ax=ax)
                    ax.set_xlabel('Archetype', fontweight='bold')
                    ax.set_ylabel('Number of Districts', fontweight='bold')
                    ax.set_title('District Distribution by Archetype', fontweight='bold', fontsize=14)
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                    st.pyplot(fig)
                
                # UESI Tab
                with tab2:
                    if show_uesi:
                        st.header("🔥 Update Effectiveness Stress Index (UESI)")
                        st.markdown("Measures citizen pain from frequent adult data corrections")
                        
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.subheader("Top 20 Stressed Districts")
                            top20 = uesi_results.head(20)
                            
                            fig, ax = plt.subplots(figsize=(10, 8))
                            ax.barh(range(len(top20)), top20['UESI_Score'], color='#e74c3c', alpha=0.7)
                            ax.set_yticks(range(len(top20)))
                            ax.set_yticklabels([f"{row['district']}, {row['state']}" for _, row in top20.iterrows()], fontsize=9)
                            ax.set_xlabel('UESI Score', fontweight='bold')
                            ax.set_title('Top 20 Districts: Highest Adult Stress', fontweight='bold')
                            ax.invert_yaxis()
                            plt.tight_layout()
                            st.pyplot(fig)
                        
                        with col2:
                            st.subheader("Key Metrics")
                            st.metric("Highest UESI", f"{uesi_results['UESI_Score'].max():.1f}")
                            st.metric("Median UESI", f"{uesi_results['UESI_Score'].median():.1f}")
                            st.metric("Districts > 50", len(uesi_results[uesi_results['UESI_Score'] > 50]))
                            
                            st.markdown("### Top District")
                            top_district = uesi_results.iloc[0]
                            st.markdown(f"**{top_district['district']}, {top_district['state']}**")
                            st.markdown(f"Score: {top_district['UESI_Score']:.1f}")
                        
                        # Download button
                        csv = uesi_results.to_csv(index=False)
                        st.download_button("📥 Download UESI Results", csv, "uesi_results.csv", "text/csv")
                
                # Resilience Tab
                with tab3:
                    if show_resilience:
                        st.header("⚡ Operational Resilience Analysis")
                        st.markdown("Measures system stability through shock intensity and volatility")
                        
                        # Tier distribution
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("Resilience Tier Distribution")
                            tier_counts = resilience_results['resilience_tier'].value_counts()
                            st.dataframe(tier_counts.to_frame('Count'), use_container_width=True)
                        
                        with col2:
                            st.subheader("Top 5 Extreme Instability")
                            extreme = resilience_results[resilience_results['resilience_tier'] == 'Extreme Instability'].head(5)
                            for _, row in extreme.iterrows():
                                st.markdown(f"**{row['district']}, {row['state']}**")
                                st.markdown(f"Shock: {row['shock_intensity']:.1f}x | Volatility: {row['volatility_score']:.1f}%")
                                st.markdown("---")
                        
                        # Scatter plot
                        st.subheader("Shock vs Volatility")
                        fig, ax = plt.subplots(figsize=(12, 8))
                        
                        tier_colors = {'Extreme Instability': '#d62728', 'High Instability': '#ff7f0e',
                                      'Moderate Volatility': '#2ca02c', 'Stable': '#1f77b4'}
                        
                        for tier in resilience_results['resilience_tier'].unique():
                            subset = resilience_results[resilience_results['resilience_tier'] == tier]
                            ax.scatter(subset['shock_intensity'], subset['volatility_score'],
                                      label=f"{tier} (n={len(subset)})", 
                                      color=tier_colors.get(tier, 'gray'), alpha=0.6, s=80)
                        
                        ax.set_xlabel('Shock Intensity (Peak / Median)', fontweight='bold')
                        ax.set_ylabel('Volatility Score (%)', fontweight='bold')
                        ax.set_title('Operational Resilience Classification', fontweight='bold', fontsize=14)
                        ax.legend()
                        ax.grid(True, alpha=0.3)
                        plt.tight_layout()
                        st.pyplot(fig)
                        
                        # Download
                        csv = resilience_results.to_csv(index=False)
                        st.download_button("📥 Download Resilience Results", csv, "resilience_results.csv", "text/csv")
                
                # Archetypes Tab
                with tab4:
                    if show_archetypes:
                        st.header("🎯 District Archetypes (Policy-Ready Classification)")
                        
                        # Policy recommendations
                        st.subheader("Policy Interventions by Archetype")
                        
                        policy_table = {
                            'Archetype': ['Critical Priority', 'Chronic Friction', 'Hidden Risk', 'Stable'],
                            'Count': [
                                len(archetype_results[archetype_results['archetype'] == 'Critical Priority']),
                                len(archetype_results[archetype_results['archetype'] == 'Chronic Friction']),
                                len(archetype_results[archetype_results['archetype'] == 'Hidden Risk']),
                                len(archetype_results[archetype_results['archetype'] == 'Stable'])
                            ],
                            'Intervention': [
                                'Comprehensive overhaul: infrastructure + training + quality',
                                'Data quality audits, operator retraining',
                                'Event-based surge capacity (mobile vans)',
                                'Standard operations - no action needed'
                            ],
                            'Priority': ['Critical', 'Medium-High', 'Medium', 'Low']
                        }
                        
                        st.dataframe(pd.DataFrame(policy_table), use_container_width=True)
                        
                        st.markdown("---")
                        
                        # 2x2 Matrix
                        st.subheader("District Classification Matrix")
                        
                        fig, ax = plt.subplots(figsize=(14, 10))
                        
                        archetype_colors = {
                            'Critical Priority': '#e74c3c',
                            'Chronic Friction': '#3498db',
                            'Hidden Risk': '#f39c12',
                            'Stable': '#2ecc71'
                        }
                        
                        for archetype in archetype_results['archetype'].unique():
                            subset = archetype_results[archetype_results['archetype'] == archetype]
                            ax.scatter(subset['UESI_Score'], subset['shock_intensity'],
                                      label=f"{archetype} (n={len(subset)})",
                                      color=archetype_colors[archetype], alpha=0.6, s=100)
                        
                        # Add median lines
                        uesi_median = archetype_results['UESI_Score'].median()
                        shock_threshold = archetype_results[archetype_results['resilience_tier'].isin(['Moderate Volatility', 'Stable'])]['shock_intensity'].max()
                        
                        ax.axvline(uesi_median, color='black', linestyle='--', alpha=0.5, label=f'UESI Median ({uesi_median:.1f})')
                        ax.axhline(shock_threshold, color='black', linestyle='--', alpha=0.5)
                        
                        ax.set_xlabel('UESI Score (Adult Stress)', fontweight='bold', fontsize=12)
                        ax.set_ylabel('Shock Intensity', fontweight='bold', fontsize=12)
                        ax.set_title('District Archetypes: 2×2 Classification Matrix', fontweight='bold', fontsize=14)
                        ax.legend(loc='upper left')
                        ax.grid(True, alpha=0.3)
                        plt.tight_layout()
                        st.pyplot(fig)
                        
                        # Download
                        csv = archetype_results.to_csv(index=False)
                        st.download_button("📥 Download Archetype Results", csv, "archetype_results.csv", "text/csv")

else:
    # Welcome screen
    st.info("👆 Upload your CSV files in the sidebar to begin analysis")
    
    st.markdown("""
    ### 📋 Framework Overview
    
    This dashboard implements the **Aadhaar Lifecycle Stress & Compliance Risk Framework**, analyzing three key dimensions:
    
    1. **🔥 UESI (Update Effectiveness Stress Index)**
       - Measures citizen pain from frequent adult data corrections
       - Identifies districts with high data quality issues
    
    2. **⚡ Operational Resilience**
       - Analyzes daily volume patterns to detect system instability
       - Measures shock intensity and volatility
       - Classifies districts into 4 resilience tiers
    
    3. **🎯 District Archetypes**
       - Synthesizes UESI + Resilience into 4 actionable categories
       - Provides policy-ready recommendations
       - Enables targeted resource allocation
    
    ### 📁 Required File Format
    
    All CSV files should contain:
    - `state`: State name
    - `district`: District name  
    - `date`: Date (YYYY-MM-DD format)
    - Age columns: `age_0_5`, `age_5_17`, `age_18_plus`
    
    Upload your files and click **Run Analysis** to begin!
    """)

# Footer
st.markdown("---")
st.markdown("Built for UIDAI Data Hackathon 2026 | Powered by Streamlit")
