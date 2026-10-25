# Technical FAQ

**Q: Why can fusion make the result worse?**
A: Poor association, miscalibrated uncertainty, dropouts, disagreement between
sensors, timing effects, false alarms or bad initialization can corrupt fused
estimates. In the current development benchmark, fused accuracy is often
slightly better, but fused precision is lower in every scenario with defined
precision; accuracy alone does not prove that fusion improved the tracker.

**Q: What is the range-only baseline?**
A: The method identifier is `range_only`, but it now means "range-bearing sensor
only". Vision observations are not enqueued or associated at all, so the
baseline cannot be influenced by the modality it excludes. It uses the same
track management and evaluation as fused.

**Q: What does the EKF assume?**
A: A constant-velocity motion model, local linearisation, approximately Gaussian
errors, known observer pose and approximate measurement models. Covariances
reflect those assumptions; they are not guaranteed to be calibrated.

**Q: Why is data association difficult?**
A: Ambiguity, false alarms, misses, crossings and gate trade-offs. The current
implementation uses independent gated Hungarian assignments per measurement
group, not MHT or JPDA.

**Q: How does observer motion affect the measurement model?**
A: Range and bearing depend on observer position and heading, and range rate
depends on observer velocity. Observations carry the observer pose at capture
time, and the EKF uses it. Bearings are sensor-frame angles: world line-of-sight
minus heading, wrapped to `[-π, π]`.

**Q: Can one track receive both range and vision in the same epoch?**
A: Yes. The two measurement groups are associated independently, so one
range-bearing and one vision observation can update the same track in the same
epoch. Updates are applied range-bearing first, then vision. Within each group,
matching is one-to-one.

**Q: How are hits and misses counted?**
A: One hit per epoch if at least one observation was successfully applied; one
miss if no update was accepted. Rejected or numerically failed updates do not
count as hits and do not reset misses.

**Q: What happens to delayed or out-of-sequence observations?**
A: They are held in a pending queue until delivery. An observation older than
one tracker epoch (`dt + 1e-6`) at processing time is rejected with a logged
stale reason and counted in `rejected_out_of_sequence`. It is not replayed.
In-flight observations at the end of a run are reported as pending.

**Q: Why is coverage still low?**
A: Coverage is measured empirically. Under the miscalibration scenario the
filter is told covariances are 20× smaller than the actual noise, so it is
overconfident and 95% coverage is roughly 0.12–0.14. The workbench measures
this rather than assuming calibration.

**Q: Why is track fragmentation N/A?**
A: It is not implemented. Reporting `None`/`N/A` is deliberate; a fabricated
zero would look like a perfect result.

**Q: What does the synthetic model omit?**
A: Raw sensing, occlusion, clutter maps, multipath, realistic environments,
full out-of-sequence replay, hardware effects and real calibration. Results are
not real-world performance.

**Q: Why restrict vision-only initialization?**
A: A single bearing gives no unique 2-D range/position. Vision can update
existing tracks when fusion is enabled, but range-bearing observations are
required to initiate them.

**Q: Are the checked-in results held out?**
A: No. The benchmark uses development seeds 1–5. Seeds 25–49 are reserved and
have not been run. The published v0.1.0 numbers are invalid and superseded; do
not use them as a baseline.

**Q: What would be needed before real-sensor claims?**
A: Validated sensor models against real data, calibration, timing/latency
handling including out-of-sequence fusion, association robustness, hardware
testing and an independently frozen held-out evaluation.
