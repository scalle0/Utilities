# ATF-FITR Cluster Analysis Script
# This script performs cluster analysis on ATF-FITR (Automated Transfer Function -
# Finite Impulse Response) raw data for energy management systems
# Author: Automated Analysis
# Date: 2025-11-05

# Load required libraries
library(tidyverse)    # For data manipulation and visualization
library(cluster)      # For clustering algorithms
library(factoextra)   # For cluster visualization
library(NbClust)      # For determining optimal number of clusters
library(dendextend)   # For dendrogram visualization
library(corrplot)     # For correlation plots

# ============================================================================
# 1. DATA LOADING AND PREPARATION
# ============================================================================

# Function to load ATF-FITR data
load_atf_fitr_data <- function(file_path) {
  cat("Loading ATF-FITR data from:", file_path, "\n")

  # Try to read the data (adjust based on actual format)
  tryCatch({
    data <- read.csv(file_path, header = TRUE, stringsAsFactors = FALSE)
    cat("Data loaded successfully. Dimensions:", dim(data), "\n")
    return(data)
  }, error = function(e) {
    cat("Error loading data:", e$message, "\n")
    return(NULL)
  })
}

# Function to preprocess the data
preprocess_data <- function(data, remove_na = TRUE, scale_data = TRUE) {
  cat("\n=== Data Preprocessing ===\n")

  # Display data structure
  cat("Data structure:\n")
  str(data)

  # Display summary statistics
  cat("\nSummary statistics:\n")
  print(summary(data))

  # Handle missing values
  if (remove_na) {
    na_count <- sum(is.na(data))
    cat("\nMissing values found:", na_count, "\n")
    if (na_count > 0) {
      data <- na.omit(data)
      cat("Rows after removing NA:", nrow(data), "\n")
    }
  }

  # Select only numeric columns for clustering
  numeric_cols <- sapply(data, is.numeric)
  numeric_data <- data[, numeric_cols]

  cat("\nNumeric columns selected for clustering:", ncol(numeric_data), "\n")
  cat("Column names:", paste(names(numeric_data), collapse = ", "), "\n")

  # Scale the data if requested
  if (scale_data && ncol(numeric_data) > 0) {
    scaled_data <- scale(numeric_data)
    cat("\nData has been scaled (standardized)\n")
    return(list(
      original = data,
      numeric_original = numeric_data,
      scaled = as.data.frame(scaled_data)
    ))
  } else {
    return(list(
      original = data,
      numeric_original = numeric_data,
      scaled = numeric_data
    ))
  }
}

# ============================================================================
# 2. EXPLORATORY DATA ANALYSIS
# ============================================================================

perform_eda <- function(data, output_dir = "cluster_output") {
  cat("\n=== Exploratory Data Analysis ===\n")

  # Create output directory if it doesn't exist
  if (!dir.exists(output_dir)) {
    dir.create(output_dir, recursive = TRUE)
  }

  # Correlation matrix
  if (ncol(data) > 1) {
    cat("\nGenerating correlation matrix...\n")
    png(file.path(output_dir, "correlation_matrix.png"), width = 800, height = 800)
    cor_matrix <- cor(data)
    corrplot(cor_matrix, method = "color", type = "upper",
             tl.col = "black", tl.srt = 45,
             title = "ATF-FITR Data Correlation Matrix",
             mar = c(0, 0, 2, 0))
    dev.off()

    # Print correlation matrix
    cat("\nCorrelation Matrix:\n")
    print(round(cor_matrix, 3))
  }

  # Distribution plots
  cat("\nGenerating distribution plots...\n")
  png(file.path(output_dir, "data_distributions.png"), width = 1200, height = 800)
  par(mfrow = c(ceiling(ncol(data)/3), 3))
  for (col in names(data)) {
    hist(data[[col]], main = paste("Distribution of", col),
         xlab = col, col = "skyblue", border = "white")
  }
  dev.off()

  # Boxplots
  png(file.path(output_dir, "boxplots.png"), width = 1200, height = 600)
  boxplot(data, main = "ATF-FITR Data Boxplots",
          las = 2, col = rainbow(ncol(data)))
  dev.off()

  cat("EDA plots saved in:", output_dir, "\n")
}

# ============================================================================
# 3. DETERMINING OPTIMAL NUMBER OF CLUSTERS
# ============================================================================

determine_optimal_clusters <- function(data, max_clusters = 10, output_dir = "cluster_output") {
  cat("\n=== Determining Optimal Number of Clusters ===\n")

  # Elbow method
  cat("\nUsing Elbow Method...\n")
  png(file.path(output_dir, "elbow_method.png"), width = 800, height = 600)
  fviz_nbclust(data, kmeans, method = "wss", k.max = max_clusters) +
    labs(title = "Elbow Method for Optimal K") +
    theme_minimal()
  dev.off()

  # Silhouette method
  cat("Using Silhouette Method...\n")
  png(file.path(output_dir, "silhouette_method.png"), width = 800, height = 600)
  fviz_nbclust(data, kmeans, method = "silhouette", k.max = max_clusters) +
    labs(title = "Silhouette Method for Optimal K") +
    theme_minimal()
  dev.off()

  # Gap statistic method
  cat("Using Gap Statistic Method...\n")
  png(file.path(output_dir, "gap_statistic.png"), width = 800, height = 600)
  fviz_nbclust(data, kmeans, method = "gap_stat", k.max = max_clusters,
               nboot = 50) +
    labs(title = "Gap Statistic Method for Optimal K") +
    theme_minimal()
  dev.off()

  cat("Optimal cluster plots saved in:", output_dir, "\n")
}

# ============================================================================
# 4. K-MEANS CLUSTERING
# ============================================================================

perform_kmeans <- function(data, k = 3, nstart = 25, output_dir = "cluster_output") {
  cat("\n=== K-Means Clustering ===\n")
  cat("Number of clusters (k):", k, "\n")

  # Perform k-means clustering
  set.seed(123)
  kmeans_result <- kmeans(data, centers = k, nstart = nstart)

  # Print clustering results
  cat("\nCluster sizes:\n")
  print(table(kmeans_result$cluster))

  cat("\nCluster centers:\n")
  print(kmeans_result$centers)

  cat("\nWithin-cluster sum of squares:", kmeans_result$tot.withinss, "\n")
  cat("Between-cluster sum of squares:", kmeans_result$betweenss, "\n")

  # Visualize clusters
  png(file.path(output_dir, "kmeans_clusters.png"), width = 1000, height = 800)
  fviz_cluster(kmeans_result, data = data,
               palette = "jco",
               ggtheme = theme_minimal(),
               main = paste("K-Means Clustering (k =", k, ")"))
  dev.off()

  # Silhouette plot
  png(file.path(output_dir, "kmeans_silhouette.png"), width = 800, height = 600)
  sil <- silhouette(kmeans_result$cluster, dist(data))
  fviz_silhouette(sil) +
    labs(title = paste("Silhouette Plot - K-Means (k =", k, ")")) +
    theme_minimal()
  dev.off()

  cat("\nAverage silhouette width:", mean(sil[, 3]), "\n")

  return(kmeans_result)
}

# ============================================================================
# 5. HIERARCHICAL CLUSTERING
# ============================================================================

perform_hierarchical <- function(data, k = 3, method = "ward.D2", output_dir = "cluster_output") {
  cat("\n=== Hierarchical Clustering ===\n")
  cat("Linkage method:", method, "\n")
  cat("Number of clusters:", k, "\n")

  # Calculate distance matrix
  dist_matrix <- dist(data, method = "euclidean")

  # Perform hierarchical clustering
  hc_result <- hclust(dist_matrix, method = method)

  # Cut tree to get clusters
  clusters <- cutree(hc_result, k = k)

  cat("\nCluster sizes:\n")
  print(table(clusters))

  # Plot dendrogram
  png(file.path(output_dir, "dendrogram.png"), width = 1200, height = 800)
  plot(hc_result, main = paste("Hierarchical Clustering Dendrogram (", method, ")"),
       xlab = "Sample Index", sub = "", cex = 0.7)
  rect.hclust(hc_result, k = k, border = 2:4)
  dev.off()

  # Fancy dendrogram
  png(file.path(output_dir, "dendrogram_colored.png"), width = 1200, height = 800)
  dend <- as.dendrogram(hc_result)
  dend_colored <- color_branches(dend, k = k)
  plot(dend_colored, main = paste("Colored Dendrogram (k =", k, ")"))
  dev.off()

  # Cluster visualization
  png(file.path(output_dir, "hierarchical_clusters.png"), width = 1000, height = 800)
  fviz_cluster(list(data = data, cluster = clusters),
               palette = "jco",
               ggtheme = theme_minimal(),
               main = paste("Hierarchical Clustering (k =", k, ")"))
  dev.off()

  # Silhouette plot
  png(file.path(output_dir, "hierarchical_silhouette.png"), width = 800, height = 600)
  sil <- silhouette(clusters, dist_matrix)
  fviz_silhouette(sil) +
    labs(title = paste("Silhouette Plot - Hierarchical (k =", k, ")")) +
    theme_minimal()
  dev.off()

  cat("\nAverage silhouette width:", mean(sil[, 3]), "\n")

  return(list(hclust = hc_result, clusters = clusters))
}

# ============================================================================
# 6. PAM (PARTITIONING AROUND MEDOIDS) CLUSTERING
# ============================================================================

perform_pam <- function(data, k = 3, output_dir = "cluster_output") {
  cat("\n=== PAM Clustering ===\n")
  cat("Number of clusters (k):", k, "\n")

  # Perform PAM clustering
  pam_result <- pam(data, k = k)

  # Print results
  cat("\nCluster sizes:\n")
  print(table(pam_result$clustering))

  cat("\nMedoids:\n")
  print(pam_result$medoids)

  # Visualize clusters
  png(file.path(output_dir, "pam_clusters.png"), width = 1000, height = 800)
  fviz_cluster(pam_result,
               palette = "jco",
               ggtheme = theme_minimal(),
               main = paste("PAM Clustering (k =", k, ")"))
  dev.off()

  # Silhouette plot
  png(file.path(output_dir, "pam_silhouette.png"), width = 800, height = 600)
  fviz_silhouette(pam_result) +
    labs(title = paste("Silhouette Plot - PAM (k =", k, ")")) +
    theme_minimal()
  dev.off()

  cat("\nAverage silhouette width:", pam_result$silinfo$avg.width, "\n")

  return(pam_result)
}

# ============================================================================
# 7. CLUSTER PROFILING AND INTERPRETATION
# ============================================================================

profile_clusters <- function(data_original, clusters, output_file = "cluster_output/cluster_profiles.csv") {
  cat("\n=== Cluster Profiling ===\n")

  # Add cluster assignment to original data
  data_with_clusters <- data_original
  data_with_clusters$Cluster <- as.factor(clusters)

  # Calculate mean values for each cluster
  cluster_profiles <- data_with_clusters %>%
    group_by(Cluster) %>%
    summarise(across(where(is.numeric), list(
      mean = ~mean(., na.rm = TRUE),
      sd = ~sd(., na.rm = TRUE),
      min = ~min(., na.rm = TRUE),
      max = ~max(., na.rm = TRUE)
    ))) %>%
    as.data.frame()

  cat("\nCluster Profiles:\n")
  print(cluster_profiles)

  # Save cluster profiles
  write.csv(cluster_profiles, output_file, row.names = FALSE)
  cat("\nCluster profiles saved to:", output_file, "\n")

  # Save data with cluster assignments
  output_data_file <- gsub("profiles.csv", "assignments.csv", output_file)
  write.csv(data_with_clusters, output_data_file, row.names = FALSE)
  cat("Data with cluster assignments saved to:", output_data_file, "\n")

  return(list(profiles = cluster_profiles, data_with_clusters = data_with_clusters))
}

# ============================================================================
# 8. MAIN ANALYSIS PIPELINE
# ============================================================================

main_cluster_analysis <- function(data_file,
                                  k = NULL,
                                  max_clusters = 10,
                                  methods = c("kmeans", "hierarchical", "pam"),
                                  output_dir = "cluster_output") {

  cat("========================================\n")
  cat("ATF-FITR CLUSTER ANALYSIS PIPELINE\n")
  cat("========================================\n\n")

  # Create output directory
  if (!dir.exists(output_dir)) {
    dir.create(output_dir, recursive = TRUE)
  }

  # Step 1: Load data
  raw_data <- load_atf_fitr_data(data_file)
  if (is.null(raw_data)) {
    stop("Failed to load data. Please check the file path and format.")
  }

  # Step 2: Preprocess data
  processed_data <- preprocess_data(raw_data, remove_na = TRUE, scale_data = TRUE)

  # Step 3: Exploratory Data Analysis
  perform_eda(processed_data$numeric_original, output_dir)

  # Step 4: Determine optimal number of clusters (if k not specified)
  if (is.null(k)) {
    determine_optimal_clusters(processed_data$scaled, max_clusters, output_dir)
    cat("\nPlease review the optimal cluster plots and specify k parameter.\n")
    cat("Re-run the analysis with the desired k value.\n")
    return(list(data = processed_data))
  }

  # Step 5: Perform clustering with different methods
  results <- list()

  if ("kmeans" %in% methods) {
    results$kmeans <- perform_kmeans(processed_data$scaled, k = k, output_dir = output_dir)
  }

  if ("hierarchical" %in% methods) {
    results$hierarchical <- perform_hierarchical(processed_data$scaled, k = k, output_dir = output_dir)
  }

  if ("pam" %in% methods) {
    results$pam <- perform_pam(processed_data$scaled, k = k, output_dir = output_dir)
  }

  # Step 6: Profile clusters (using k-means results as default)
  if ("kmeans" %in% methods) {
    cluster_profiles <- profile_clusters(
      processed_data$numeric_original,
      results$kmeans$cluster,
      output_file = file.path(output_dir, "cluster_profiles.csv")
    )
    results$profiles <- cluster_profiles
  }

  cat("\n========================================\n")
  cat("ANALYSIS COMPLETE!\n")
  cat("Results saved in:", output_dir, "\n")
  cat("========================================\n")

  return(results)
}

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

# Example 1: Run complete analysis with automatic k determination
# results <- main_cluster_analysis(
#   data_file = "atf_fitr_data.csv",
#   k = NULL,  # Will generate plots to help determine optimal k
#   max_clusters = 10
# )

# Example 2: Run complete analysis with specified k
# results <- main_cluster_analysis(
#   data_file = "atf_fitr_data.csv",
#   k = 3,
#   methods = c("kmeans", "hierarchical", "pam"),
#   output_dir = "cluster_results"
# )

# Example 3: Load your data and run analysis
# Uncomment and modify the following lines to run the analysis:
#
# data_file <- "path/to/your/atf_fitr_data.csv"
# results <- main_cluster_analysis(
#   data_file = data_file,
#   k = 3,  # Specify number of clusters, or NULL to determine optimal k
#   max_clusters = 10,
#   methods = c("kmeans", "hierarchical", "pam"),
#   output_dir = "cluster_output"
# )

cat("\n=== ATF-FITR Cluster Analysis Script Loaded ===\n")
cat("To run the analysis, use:\n")
cat("results <- main_cluster_analysis(data_file = 'your_data.csv', k = 3)\n")
cat("\nFor help, see the EXAMPLE USAGE section at the end of this script.\n")
