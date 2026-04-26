# Load required library
library(dplyr)

# Read your sample-testing_results.csv file
df <- read.csv("sample-testing_results.csv", stringsAsFactors = FALSE)

# Rename columns for convenience (adjust if your column names differ)
df <- df %>%
  rename(
    predicted = predicted.resolution.time..days.,
    actual = actual.resolution.time..days.
  )

# !! Performance Metrics !!

# Mean Absolute Error (MAE)
MAE <- mean(abs(df$actual - df$predicted))

# Root Mean Squared Error (RMSE)
RMSE <- sqrt(mean((df$actual - df$predicted)^2))

# R-squared (Coefficient of Determination)
SS_res <- sum((df$actual - df$predicted)^2)
SS_tot <- sum((df$actual - mean(df$actual))^2)
R2 <- 1 - (SS_res / SS_tot)

# Create a results data frame
results <- data.frame(
  MAE = MAE,
  RMSE = RMSE,
  R2 = R2
)

# Write results to a new CSV file
write.csv(results, "sample-testing_metrics.csv", row.names = FALSE)

# Print confirmation
print("Metrics saved to sample-testing_metrics.csv")
print(results)