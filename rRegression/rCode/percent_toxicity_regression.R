# Load libraries
library(ggplot2)

# Read in data
tox <- read.csv("toxic-percent.csv")

# Ensure numeric
tox$resolutiontime <- as.numeric(tox$resolutiontime)
tox$percent_toxic  <- as.numeric(tox$percent_toxic)

# Keep only rows where toxicity is positive AND finite
tox_clean <- subset(
  tox,
  percent_toxic > 0 &
  is.finite(percent_toxic) &
  is.finite(resolutiontime)
)

# Add constant for log model (avoids log(0))
tox_clean$percent_toxic_adj <- tox_clean$percent_toxic + 0.001

# Remove any remaining non-finite values
tox_clean <- tox_clean[
  is.finite(tox_clean$percent_toxic_adj) &
  is.finite(tox_clean$resolutiontime),
]

# Models

# Linear
model_linear <- lm(resolutiontime ~ percent_toxic, data = tox_clean)
summary(model_linear)

# Logarithmic
model_log <- lm(resolutiontime ~ log(percent_toxic_adj), data = tox_clean)
summary(model_log)

# Quadratic
model_quad <- lm(resolutiontime ~ percent_toxic + I(percent_toxic^2), data = tox_clean)
summary(model_quad)

# Export
linear_summary <- as.data.frame(summary(model_linear)$coefficients)
log_summary    <- as.data.frame(summary(model_log)$coefficients)
quad_summary   <- as.data.frame(summary(model_quad)$coefficients)

linear_summary$model <- "Linear"
log_summary$model    <- "Logarithmic"
quad_summary$model   <- "Quadratic"

all_models <- rbind(linear_summary, log_summary, quad_summary)
write.csv(all_models, "toxicity_regression_summaries.csv", row.names = TRUE)

# Plot
ggplot(tox_clean, aes(x = percent_toxic, y = resolutiontime)) +
  geom_point(alpha = 0.5) +
  stat_smooth(method = "lm", formula = y ~ x, se = FALSE, color = "blue") +
  stat_smooth(method = "lm", formula = y ~ log(x + 0.001), se = FALSE, color = "green") +
  stat_smooth(method = "lm", formula = y ~ poly(x, 2, raw = TRUE), se = FALSE, color = "red") +
  labs(
    title = "Resolution Time vs %Toxicity",
    x = "%Toxicity",
    y = "Resolution Time (days)"
  ) +
  theme_minimal()

ggsave("toxicity_vs_resolutiontime.png", width = 8, height = 6, dpi = 300)