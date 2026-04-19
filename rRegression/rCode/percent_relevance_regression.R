# Load libraries
library(ggplot2)

# Read in data
resolved <- read.csv("tone-relevance_analyzed.csv")

# Fix column names
names(resolved)[names(resolved) == "X.tone"] <- "percent_tone"
names(resolved)[names(resolved) == "X.relevance"] <- "percent_relevance"

# Ensure numeric
resolved$resolutiontime <- as.numeric(resolved$resolutiontime)
resolved$percent_relevance <- as.numeric(resolved$percent_relevance)

# Remove NA rows
resolved_clean <- subset(resolved, !is.na(percent_relevance) & !is.na(resolutiontime))

# Linear model
model_linear <- lm(resolutiontime ~ percent_relevance, data = resolved_clean)
summary(model_linear)

# Logarithmic model
model_log <- lm(resolutiontime ~ log(percent_relevance), data = resolved_clean)
summary(model_log)

# Quadratic model
model_quad <- lm(resolutiontime ~ percent_relevance + I(percent_relevance^2), data = resolved_clean)
summary(model_quad)

# Export summaries
linear_summary <- as.data.frame(summary(model_linear)$coefficients)
log_summary <- as.data.frame(summary(model_log)$coefficients)
quad_summary <- as.data.frame(summary(model_quad)$coefficients)

linear_summary$model <- "Linear"
log_summary$model <- "Logarithmic"
quad_summary$model <- "Quadratic"

all_models <- rbind(linear_summary, log_summary, quad_summary)
write.csv(all_models, "relevance_regression_summaries.csv", row.names = TRUE)

# Plot
ggplot(resolved_clean, aes(x = percent_relevance, y = resolutiontime)) +
  geom_point(alpha = 0.5) +
  stat_smooth(method = "lm", formula = y ~ x, se = FALSE, color = "blue") +
  stat_smooth(method = "lm", formula = y ~ log(x), se = FALSE, color = "green") +
  stat_smooth(method = "lm", formula = y ~ poly(x, 2, raw = TRUE), se = FALSE, color = "red") +
  labs(
    title = "Resolution Time vs %Relevance",
    x = "%Relevance",
    y = "Resolution Time (days)"
  ) +
  theme_minimal()

ggsave("relevance_vs_resolutiontime.png", width = 8, height = 6, dpi = 300)
