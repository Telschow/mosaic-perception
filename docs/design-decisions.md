# Design Decisions

- **Synthetic observations first**: Start at detector outputs (range/bearing/class probs) rather than raw images/waveforms to focus on estimation/tracking/fusion/evaluation.
- **Range-only baseline**: Provides a fair, interpretable reference against which fusion is compared on equivalent scenarios.
- **Vision-bearing alone cannot initialize 2D tracks**: A single bearing measurement is not uniquely observable for range/position in 2D; tracker does not initiate from vision-only observations.
- **Observer-pose contract**: Observations carry observer pose context; tracker uses it for correct measurement models under motion.
- **Canonical EKF**: Single update path with Joseph form and angle wrapping for numerical/consistency reasons.
- **Per-epoch miss counting**: Avoids double-counting misses across multiple sensors in the same cycle.
- **Reproducibility first**: Explicit seeds, deterministic streams, configuration capture, generated reports.
- **Honest limitations**: Document what is not modeled (raw sensing, full timing replay, advanced association) rather than hiding it.
