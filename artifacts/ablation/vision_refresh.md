# Ablation: vision refreshing range-missed tracks

Fused minus range-only, paired over development seeds 0-24 (95% t interval).
`all` is the benchmark default; `range_supported` lets vision update only tracks a
range observation updated in the same epoch. Claims are limited to this tracker and
these gates.
Commit: `591276d56d7e002ffd10b5abf38866aab088dc00`

| Scenario | Policy | Metric | Mean difference | 95% interval |
|---|---|---|---|---|
| nominal | all | precision | -0.130 | [-0.162, -0.099] |
| nominal | all | mota | -0.226 | [-0.286, -0.167] |
| nominal | all | gospa_p1 | +0.635 | [+0.447, +0.822] |
| nominal | range_supported | precision | -0.005 | [-0.034, +0.024] |
| nominal | range_supported | mota | -0.009 | [-0.052, +0.034] |
| nominal | range_supported | gospa_p1 | -0.037 | [-0.190, +0.115] |
| dense_clutter | all | precision | -0.478 | [-0.499, -0.457] |
| dense_clutter | all | mota | -1.709 | [-1.817, -1.602] |
| dense_clutter | all | gospa_p1 | +5.115 | [+4.779, +5.452] |
| dense_clutter | range_supported | precision | +0.016 | [-0.007, +0.038] |
| dense_clutter | range_supported | mota | +0.025 | [-0.010, +0.059] |
| dense_clutter | range_supported | gospa_p1 | -0.152 | [-0.269, -0.034] |
| vision_dropout | all | precision | -0.100 | [-0.124, -0.075] |
| vision_dropout | all | mota | -0.163 | [-0.208, -0.119] |
| vision_dropout | all | gospa_p1 | +0.482 | [+0.324, +0.641] |
| vision_dropout | range_supported | precision | -0.001 | [-0.019, +0.017] |
| vision_dropout | range_supported | mota | +0.001 | [-0.027, +0.028] |
| vision_dropout | range_supported | gospa_p1 | -0.037 | [-0.138, +0.064] |
| sensor_disagreement_within_gate | all | precision | -0.265 | [-0.292, -0.239] |
| sensor_disagreement_within_gate | all | mota | -0.577 | [-0.641, -0.512] |
| sensor_disagreement_within_gate | all | gospa_p1 | +1.894 | [+1.681, +2.106] |
| sensor_disagreement_within_gate | range_supported | precision | -0.074 | [-0.107, -0.041] |
| sensor_disagreement_within_gate | range_supported | mota | -0.142 | [-0.197, -0.086] |
| sensor_disagreement_within_gate | range_supported | gospa_p1 | +0.645 | [+0.437, +0.854] |
