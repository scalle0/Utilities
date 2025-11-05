# ATF-FITR Cluster Analysis

This repository contains a comprehensive R script for performing cluster analysis on ATF-FITR (Automated Transfer Function - Finite Impulse Response) raw data.

## Features

The `atf_fitr_cluster_analysis.R` script provides:

1. **Data Loading and Preprocessing**
   - Flexible data loading from CSV files
   - Automatic handling of missing values
   - Data scaling and standardization
   - Summary statistics generation

2. **Exploratory Data Analysis (EDA)**
   - Correlation matrix visualization
   - Distribution plots for all variables
   - Boxplots for outlier detection

3. **Optimal Cluster Determination**
   - Elbow method
   - Silhouette method
   - Gap statistic method

4. **Multiple Clustering Algorithms**
   - K-Means clustering
   - Hierarchical clustering (with multiple linkage methods)
   - PAM (Partitioning Around Medoids)

5. **Comprehensive Visualization**
   - Cluster plots in 2D (using PCA)
   - Dendrograms for hierarchical clustering
   - Silhouette plots for cluster quality assessment
   - Correlation heatmaps

6. **Cluster Profiling**
   - Statistical summaries for each cluster
   - Cluster assignments for each data point
   - Export results to CSV files

## Prerequisites

Install the required R packages:

```r
install.packages(c(
  "tidyverse",
  "cluster",
  "factoextra",
  "NbClust",
  "dendextend",
  "corrplot"
))
```

## Quick Start

### 1. Prepare Your Data

Your ATF-FITR data should be in CSV format with:
- First row containing column headers
- Numeric columns for the variables to cluster
- Each row representing an observation/sample

Example data structure:
```
timestamp,power,voltage,current,frequency,temperature
2025-01-01 00:00:00,1500.5,230.2,6.52,50.0,25.3
2025-01-01 00:05:00,1623.7,229.8,7.06,50.1,25.5
...
```

### 2. Run the Analysis

#### Option A: Determine Optimal Number of Clusters First

```r
# Load the script
source("atf_fitr_cluster_analysis.R")

# Run analysis without specifying k to see optimal cluster suggestions
results <- main_cluster_analysis(
  data_file = "your_atf_fitr_data.csv",
  k = NULL,  # This will generate plots to help determine optimal k
  max_clusters = 10
)

# Review the plots in the 'cluster_output' folder:
# - elbow_method.png
# - silhouette_method.png
# - gap_statistic.png
```

#### Option B: Run Full Analysis with Known k

```r
# Load the script
source("atf_fitr_cluster_analysis.R")

# Run complete analysis with k=3 clusters
results <- main_cluster_analysis(
  data_file = "your_atf_fitr_data.csv",
  k = 3,
  methods = c("kmeans", "hierarchical", "pam"),
  output_dir = "cluster_results"
)
```

### 3. Review Results

All outputs are saved in the specified output directory (default: `cluster_output/`):

**Plots:**
- `correlation_matrix.png` - Variable correlations
- `data_distributions.png` - Histograms of all variables
- `boxplots.png` - Boxplots for outlier detection
- `elbow_method.png` - Elbow plot for optimal k
- `silhouette_method.png` - Silhouette plot for optimal k
- `gap_statistic.png` - Gap statistic for optimal k
- `kmeans_clusters.png` - K-means cluster visualization
- `kmeans_silhouette.png` - K-means silhouette plot
- `dendrogram.png` - Hierarchical clustering dendrogram
- `dendrogram_colored.png` - Colored dendrogram
- `hierarchical_clusters.png` - Hierarchical cluster visualization
- `hierarchical_silhouette.png` - Hierarchical silhouette plot
- `pam_clusters.png` - PAM cluster visualization
- `pam_silhouette.png` - PAM silhouette plot

**Data Files:**
- `cluster_profiles.csv` - Statistical summary for each cluster
- `cluster_assignments.csv` - Original data with cluster labels

## Advanced Usage

### Custom Clustering Parameters

```r
# K-means with specific parameters
kmeans_result <- perform_kmeans(
  data = scaled_data,
  k = 4,
  nstart = 50,
  output_dir = "custom_output"
)

# Hierarchical clustering with different linkage methods
# Options: "ward.D", "ward.D2", "single", "complete", "average", "mcquitty", "median", "centroid"
hc_result <- perform_hierarchical(
  data = scaled_data,
  k = 4,
  method = "complete",
  output_dir = "custom_output"
)

# PAM clustering
pam_result <- perform_pam(
  data = scaled_data,
  k = 4,
  output_dir = "custom_output"
)
```

### Step-by-Step Analysis

```r
# Load and preprocess data manually
raw_data <- load_atf_fitr_data("your_data.csv")
processed_data <- preprocess_data(raw_data, remove_na = TRUE, scale_data = TRUE)

# Run EDA
perform_eda(processed_data$numeric_original, output_dir = "eda_output")

# Determine optimal clusters
determine_optimal_clusters(processed_data$scaled, max_clusters = 15)

# Run specific clustering method
kmeans_result <- perform_kmeans(processed_data$scaled, k = 3)

# Profile the clusters
cluster_profiles <- profile_clusters(
  processed_data$numeric_original,
  kmeans_result$cluster
)
```

## Interpreting Results

### Silhouette Width
- Values close to 1: Well-clustered observations
- Values close to 0: On the border between clusters
- Negative values: Possibly misclassified observations
- Average silhouette width > 0.5 indicates good clustering

### Elbow Method
- Look for the "elbow" point where adding more clusters doesn't significantly reduce within-cluster variance

### Gap Statistic
- Higher gap statistic indicates better clustering
- Choose k where the gap statistic is maximized

### Cluster Profiles
- Review the mean, standard deviation, min, and max values for each variable in each cluster
- Identify distinguishing characteristics of each cluster

## Energy Management Applications

For energy management systems, this cluster analysis can help identify:

1. **Load Patterns**: Different electricity consumption patterns (peak, off-peak, baseline)
2. **Device States**: Operational states of energy devices (standby, active, high-load)
3. **Anomalies**: Unusual energy consumption patterns that may indicate issues
4. **Time-based Patterns**: Daily, weekly, or seasonal energy usage patterns
5. **Efficiency Groups**: Grouping similar energy efficiency profiles

## Troubleshooting

**Error: "Failed to load data"**
- Check that the file path is correct
- Ensure the file is in CSV format
- Verify that the file has a header row

**Error: "Cannot find function"**
- Make sure all required packages are installed
- Load the script using `source("atf_fitr_cluster_analysis.R")`

**Warning: "Missing values"**
- The script automatically removes rows with missing values
- Check your data quality if too many rows are removed

**Poor clustering results (low silhouette width)**
- Try different values of k
- Consider using different clustering methods
- Check if your data needs additional preprocessing
- Verify that your variables are on comparable scales

## Example Data Format

If you need to test the script, create a sample CSV file:

```csv
power_avg,voltage_avg,current_avg,frequency,temperature,timestamp_hour
1500.5,230.2,6.52,50.0,25.3,0
1623.7,229.8,7.06,50.1,25.5,1
1456.2,230.5,6.32,49.9,25.2,2
2134.8,228.9,9.32,50.2,26.1,8
2456.3,229.1,10.72,50.0,26.8,9
1789.4,230.0,7.78,50.1,26.2,10
```

## License

This script is provided as-is for energy management analysis purposes.

## Contact

For issues or questions, please refer to the repository documentation.
