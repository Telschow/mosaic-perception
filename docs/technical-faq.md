# Technical FAQ

**Q: Why can fusion make the result worse?**  
A: Poor association, miscalibrated uncertainty, dropouts/disagreements, timing issues, or bad initialization can corrupt fused estimates. Controlled experiments reveal these cases.

**Q: What is the purpose of the range-only baseline?**  
A: A fair reference on equivalent conditions; fusion must justify its additional complexity/information.

**Q: What does the EKF assume?**  
A: Local linearization, approximately Gaussian errors, known/approximate models. Covariances reflect model assumptions.

**Q: Why is data association difficult?**  
A: Ambiguity, false alarms/misses, clutter, and gating trade-offs. Current implementation uses gated nearest-neighbor (greedy).

**Q: How does observer motion affect the measurement model?**  
A: Range/bearing depend on observer position/orientation; observer pose must be available to the estimator (propagated via context).

**Q: How are uncertainty and RMSE different?**  
A: RMSE measures accuracy vs truth; reported covariance measures claimed uncertainty. Calibration is separate (empirical coverage) and not guaranteed.

**Q: Why can one seed be misleading?**  
A: Stochastic effects vary; use multiple seeds and report aggregates/variability.

**Q: What does the synthetic model omit?**  
A: Raw sensing, occlusions/clutter details, full out-of-sequence replay, real calibration, etc. Results are not real-world performance.

**Q: Why restrict vision-only initialization?**  
A: Single bearing gives no unique 2D range/position; insufficient observability. Vision updates existing tracks when available.

**Q: What would be needed before real-sensor claims?**  
A: Validated models against real data, careful calibration, timing/latency handling, association robustness, and extensive testing outside simulation.
