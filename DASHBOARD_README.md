# UIDAI Operational Intelligence Dashboard

## Quick Start

### 1. Install Dependencies

```bash
pip install streamlit pandas matplotlib seaborn numpy
```

### 2. Run the Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Features

### 📊 Interactive Analysis

- **File Upload**: Drag and drop your CSV files (Enrolment, Demographic, Biometric)
- **Real-time Processing**: Instant analysis across all frameworks
- **Interactive Visualizations**: Explore data with charts and plots

### 🔍 Framework Modules

1. **UESI Analysis**
   - Adult stress index calculation
   - Top stressed districts ranking
   - Downloadable results

2. **Operational Resilience**
   - Shock intensity measurement
   - Volatility scoring
   - Tier classification (Extreme/High/Moderate/Stable)

3. **District Archetypes**
   - 4-quadrant classification
   - Policy recommendations
   - 2×2 matrix visualization

### 📁 Expected File Format

All CSV files should contain:

- `state` (string): State name
- `district` (string): District name
- `date` (date): Transaction date (YYYY-MM-DD)
- `age_0_5` (integer): Count for age 0-5
- `age_5_17` (integer): Count for age 5-17
- `age_18_plus` (integer): Count for age 18+

### 🎨 Dashboard Sections

#### Overview Tab

- Total districts analyzed
- Critical priority count
- Extreme instability count
- Average UESI score
- Archetype distribution chart

#### UESI Analysis Tab

- Top 20 stressed districts bar chart
- Key metrics summary
- Top district spotlight
- Downloadable results (CSV)

#### Resilience Analysis Tab

- Tier distribution table
- Top 5 extreme instability districts
- Shock vs Volatility scatter plot
- Downloadable results (CSV)

#### District Archetypes Tab

- Policy intervention table
- 2×2 classification matrix
- Quadrant visualization
- Downloadable results (CSV)

## Usage Tips

1. **Select Frameworks**: Use checkboxes in sidebar to enable/disable specific analyses
2. **Download Results**: Each tab has a download button for CSV exports
3. **Interactive Plots**: Hover over charts for detailed information

## Technical Details

- **Framework**: Streamlit
- **Visualization**: Matplotlib, Seaborn
- **Data Processing**: Pandas, NumPy
- **Caching**: Results are cached for performance

## Troubleshooting

**Dashboard won't start**:

```bash
# Reinstall streamlit
pip install --upgrade streamlit
```

**CSV upload fails**:

- Check file format (must be valid CSV)
- Verify required columns exist
- Ensure date column is in YYYY-MM-DD format

**Memory issues with large files**:

- Use smaller date ranges
- Aggregate data before upload
- Increase Python memory limit

## For Presentation

To present the dashboard during the hackathon:

1. Start the dashboard: `streamlit run dashboard.py`
2. Upload your pre-cleaned CSV files
3. Click "Run Analysis"
4. Navigate through tabs to showcase each framework
5. Use download buttons to export results

The dashboard automatically saves your uploaded files in a temporary session, so you can re-run analyses without re-uploading.
