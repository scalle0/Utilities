# Utilities

Energy management and data analysis tools by scalle0.

## Projects

### 🔋 Growatt Battery Automation
Intelligent battery management system that optimizes charging schedules based on dynamic electricity prices.

**Features:**
- Automatic price fetching from multiple sources (ENTSO-E, Tibber, etc.)
- Smart optimization to minimize electricity costs
- Daily automation with cron scheduling
- Supports Growatt inverters via API or Modbus
- Potential savings of €10-50+ per month

**Quick Start:**
```bash
pip install -r requirements.txt
cp battery_config.example.json battery_config.json
# Edit battery_config.json with your settings
./setup_scheduler.sh
```

**Documentation:** See [BATTERY_AUTOMATION_README.md](BATTERY_AUTOMATION_README.md)

**Files:**
- `battery_automation.py` - Main automation script
- `price_fetcher.py` - Electricity price fetching
- `battery_optimizer.py` - Optimization algorithms
- `growatt_controller.py` - Inverter control

---

### 📊 ATF-FITR Cluster Analysis
Comprehensive R script for cluster analysis on ATF-FITR (Automated Transfer Function - Finite Impulse Response) data.

**Features:**
- Multiple clustering algorithms (K-Means, Hierarchical, PAM)
- Optimal cluster determination (Elbow, Silhouette, Gap methods)
- Extensive visualizations and profiling
- Export results to CSV

**Quick Start:**
```r
source("atf_fitr_cluster_analysis.R")
results <- main_cluster_analysis(
  data_file = "your_data.csv",
  k = 3
)
```

**Documentation:** See [CLUSTER_ANALYSIS_README.md](CLUSTER_ANALYSIS_README.md)

**Files:**
- `atf_fitr_cluster_analysis.R` - Complete analysis script

---

## License

These tools are provided as-is for personal energy management and data analysis.
