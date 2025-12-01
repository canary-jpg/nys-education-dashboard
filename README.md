# 🎓 NYS School District Performance & Equity Dashboard

Interactive dashboard analyzing education outcomes for 182 districts in the New York City metropolitan area.

![Dashboard Preview]('images/dashboard_preview.png')

! [Equity Analysis]('images/equity_analysis.png')


## 📊 Overview
This project processes and visualizes education data from the New York State Education Department, focusing on NYC, Westchester, Nassau, and Suffolk counties. The dashboard enables stakeholders to compare district performance, identify equity gaps, and track trends over time.

### Key Features
- **📈 Performance Metrics**: Track graduation rates, dropout rates, attendance, and suspensions
- **⚖️ Equity Analysis**: Visualize relationships between economic disadvantage and educational outcomes
- **🔍 District Comparison**: Side-by-side comparison of any districts
- **📊 Summary Statistics**: Statistical distribution (mean, median, std dev) for all metrics
- **📆 Trend Analysis**: Track changes across 3 years (2022-2024)
- **📥 Data Export**: Download filtered data and summary statistics as CSV

## 🎯 Use Cases
- **School Administrators**: Compare district performance against regional peers
- **Policy Makers**: Identify districts needing additional resources
- **Researchers**: Analyze equity gaps and demographic patterns
- **Parents**: Evaluate school district quality metrics
- **Data Analysts**: Demonstrate ETL and visualization skills

## 🛠️ Tech Stack
- **Python 3.12**
- **pandas**: Data manipulation and analysis
- **Streamlit** : Interactive web dashboard
- **Plotly**: Data visualization 
- **mdb-tools**: Access database extraction (macOS)

## 📁 Project Structure
```
nys-education-dashboard/
├── data/
│   ├── raw/                                    # Original data files
│   │   ├── ENROLL2024_20241105.accdb
│   │   ├── STUDED_2024.accdb
│   │   ├── 2024_GRADUATION_RATE.mdb
│   │   └── 2024 Districts...Refusals.xlsx
│   └── processed/                              # Cleaned CSV files
│       ├── master_dataset.csv
│       ├── graduation_filtered.csv
│       └── ...
├── notebooks/
│   └── 01_data_exploration.ipynb              # Initial data exploration
├── src/
│   └── data_processing.py                     # Data cleaning functions
├── app.py                                      # Streamlit dashboard
├── export_access_tables.py                    # Extract Access databases
├── data_processing.py                         # Main ETL pipeline
├── requirements.txt
└── README.md
```

### Prerequisites

- Python 3.8+
- Homebrew (macOS) for mdb-tools
- ~500MB disk space for data files

### Installation
1. **Clone the repository**
```bash
git clone https://github.com/yourusername/nys-education-dashboard.git
cd nys-education-dashboard
```
2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate #on windows venv/Scripts/activate
```
3. **Install dependencies**
```bash
pip install -r requirements.txt
```
4. **Install mdb-tools (macOS only, for Access database processing)
```bash
brew install mdb-tools
```

### Data Setup
1. **Download data files from [NYS Education Data](https://data.nysed.gov/downloads.php):
- 2024 Enrollment database
- 2024 Student/District Database
- 2024 Graduation Rate Database
- 2024 Test Refusals (Excel file)

2. **Place files in `data/raw/`**

3. **Run the data pipeline**:
```bash
#extract access database tables to csv
python export_access_tables.py

#process and merge all data
python data_processing.py
```
### Running the Dashboard
```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 📊 Data Sources
All data sourced from the **New York State Education Departments** (data.nysed.gov):
- **Enrollment Database**: Student counts by grade, race/ethnicity, and demographics
- **Student/District Database**: Attendance, suspensions, free lunch eligibility, class sizes
- **Graduation Database**: 4-year graduation rates, dropout rates, cohort sizes
- **Test refusals**: ELA, Math, and Science assessment participation

**Coverage**: 182 districts accross 4 counties, SYs22-24

## 📈 Key Metrics

### Performance Indicators
- **Graduation Rate**: 4-year cohort graduation percentage
- **Dropout Rate**: Students who left school without graduating
- **Attendance Rate**: Average daily attendance
- **Suspension Rate**: Percentage of students suspended

### Equity Indicators
- **Economically Disadvantaged**: Students eligible for free/reduced lunch
- **English Language Learners**: Students learning English
- **Students with Disabilities**: Students with IEPs
**Demographic Breakdown**: By race/ethnicity

## 🎨 Dashboard Features

### 1. Key Metrics Overview
Top-level statistics for selected region and year

### 2. Summary Statistics
Comprehensive statistical analysis (mean, median, min, max, std dev) for all metrics

![Summary Stats]('/images/summary_stats.png')

### 3. Visualization
- County enrollment comparison (bar chart)
- Demographics breakdown (pie chart)
- Equity analysis (scatter plots)
- District comparison (side-by-side bars)
- Trend analysis (line charts)

### 4. Interactive Filters
- Year selection (2022-2024)
- County selection (NYC, Westchester, Nassau, Suffolk)
- District multi-select for comparisons

### 5. Data Exports
- Download filtered data
- Export summary statistics
- Full dataset export

## 💡 Sample Insights
- **Average graduation rate**: ~88% across all districts
- **Equity Gap**: Districts with >60% economically disadvantaged students who 8-12% lower graduation rates
- **Geographic variation**: Suffolk county has the widest range in graduation rate (68%-98%)
- **Trend**: Overall graduation rates improved 2.3% from 2022-2024

## 🔧 Developments

### Adding New Metrics
1. Add data file to `data/raw/`
2. Update `export_access_tables.py` to export new tables
3. Modify `data_processing.py` to include new metrics in master dataset
4. Update `app.py` to visualize new metrics

### Extending to Other Regions

Modify `TARGET_COUNTIES` in `data_processing.py`:
``` python
TARGET_COUNTIES = ['ALBANY', 'ERIE', 'MONROE', 'ONONDAGA']
```

## 📝 Future Enhancements

- [ ] Add test score data (grades 3-8 ELA/Math)
- [ ] Include per-pupil spending analysis
- [ ] Geographic mapping of districts
- [ ] Predictive modeling for at-risk districts
- [ ] Demographic subgroup analysis (graduation by race/ethnicity)
- [ ] Year-over-year comparison dashboard
- [ ] PDF report generation

Contributions welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Hazel Donaldson**
- Portfolio: [yourportfolio.com](https://yourportfolio.com)
- LinkedIn: [linkedin.com/in/hazel-donaldson](https://linkedin.com/in/hazel-donaldson)
- GitHub: [@canary-jpg](https://github.com/canary-jpg)

## 🙏 Acknowledgments

- Data provided by the New York State Education Department
- Built with [Streamlit](https://streamlit.io/) and [Plotly](https://plotly.com/)

## 📧 Contact

For questions, collaborations, or data analysis consulting inquiries, reach out at hazel90.hd@gmail.com

---

**Note**: This is a portfolio/demonstration project. For production use, consider additional data validation, error handling, and security measures.
