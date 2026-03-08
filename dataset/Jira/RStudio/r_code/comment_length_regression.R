# Load libraries
library(ggplot2)

# Read in data
resolved <- read.csv("csv_final/6-issues_analyzed.csv")

# Convert resolutiontime and timespent to numeric (if not already)
resolved$resolutiontime <- as.numeric(resolved$resolutiontime)

# Linear model: resolutiontime vs commentlength
model1 <- lm(resolutiontime ~ commentlength, data = resolved)
summary(model1)

# Logarithmic regression: resolutiontime ~ log(commentlength)
log_model1 <- lm(resolutiontime ~ log(commentlength), data = resolved)
summary(log_model1)

# Quadratic regression: resolutiontime ~ commentlength^2
poly_model1 <- lm(resolutiontime ~ commentlength + I(commentlength^2), data = resolved)
summary(poly_model1)




## Export Data:
# Extract summaries as data frames
linear_summary <- as.data.frame(summary(model1)$coefficients)
log_summary <- as.data.frame(summary(log_model1)$coefficients)
poly_summary <- as.data.frame(summary(poly_model1)$coefficients)

# Add model names
linear_summary$model <- "Linear"
log_summary$model <- "Logarithmic"
poly_summary$model <- "Quadratic"

# Combine all into one table
all_models <- rbind(linear_summary, log_summary, poly_summary)

# Export to CSV
write.csv(all_models, "RStudio/exports/regression_model_summaries.csv", row.names = TRUE)





# Plot Data
# Base scatter plot
ggplot(resolved, aes(x = commentlength, y = resolutiontime)) +
  geom_point(alpha = 0.5) +
  
  # Linear fit
  stat_smooth(method = "lm", formula = y ~ x, se = FALSE, color = "blue", linetype = "dashed") +
  
  # Logarithmic fit (only on positive x)
  stat_smooth(method = "lm", formula = y ~ log(x), se = FALSE, color = "green") +
  
  # Quadratic fit
  stat_smooth(method = "lm", formula = y ~ poly(x, 2, raw = TRUE), se = FALSE, color = "red") +
  
  labs(
    title = "Resolution Time vs Comment Length",
    x = "Comment Length",
    y = "Resolution Time (days)"
  ) +
  theme_minimal()


# Save the last plot as PNG
ggsave("RStudio/exports/resolutiontime_vs_commentlength.png", width = 8, height = 6, dpi = 300)

