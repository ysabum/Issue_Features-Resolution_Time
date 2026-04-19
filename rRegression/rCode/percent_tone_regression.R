library(ggplot2)

resolved <- read.csv("tone-relevance_analyzed.csv")

# Fix column names
names(resolved)[names(resolved) == "X.tone"] <- "percent_tone"
names(resolved)[names(resolved) == "X.relevance"] <- "percent_relevance"

# Ensure numeric
resolved$resolutiontime <- as.numeric(resolved$resolutiontime)
resolved$percent_tone   <- as.numeric(resolved$percent_tone)

# Keep only rows where tone is positive AND finite
resolved_clean <- subset(
  resolved,
  percent_tone > 0 &
    is.finite(percent_tone) &
    is.finite(resolutiontime)
)

# Add constant for log model
resolved_clean$percent_tone_adj <- resolved_clean$percent_tone + 0.001

# Remove any remaining non-finite values
resolved_clean <- resolved_clean[
  is.finite(resolved_clean$percent_tone_adj) &
    is.finite(resolved_clean$resolutiontime),
]

# Models

model_linear <- lm(resolutiontime ~ percent_tone, data = resolved_clean)
summary(model_linear)

model_log <- lm(resolutiontime ~ log(percent_tone_adj), data = resolved_clean)
summary(model_log)

model_quad <- lm(resolutiontime ~ percent_tone + I(percent_tone^2), data = resolved_clean)
summary(model_quad)


# Export
linear_summary <- as.data.frame(summary(model_linear)$coefficients)
log_summary    <- as.data.frame(summary(model_log)$coefficients)
quad_summary   <- as.data.frame(summary(model_quad)$coefficients)

linear_summary$model <- "Linear"
log_summary$model    <- "Logarithmic"
quad_summary$model   <- "Quadratic"

all_models <- rbind(linear_summary, log_summary, quad_summary)
write.csv(all_models, "tone_regression_summaries.csv", row.names = TRUE)

# ---- PLOT ----

ggplot(resolved_clean, aes(x = percent_tone, y = resolutiontime)) +
  geom_point(alpha = 0.5) +
  stat_smooth(method = "lm", formula = y ~ x, se = FALSE, color = "blue") +
  stat_smooth(method = "lm", formula = y ~ log(x + 0.001), se = FALSE, color = "green") +
  stat_smooth(method = "lm", formula = y ~ poly(x, 2, raw = TRUE), se = FALSE, color = "red") +
  labs(
    title = "Resolution Time vs %Tone (Non-neutral only)",
    x = "%Tone",
    y = "Resolution Time (days)"
  ) +
  theme_minimal()

ggsave("tone_vs_resolutiontime.png", width = 8, height = 6, dpi = 300)
