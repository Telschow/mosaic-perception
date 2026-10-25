"""Paired-difference statistics over seeds."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from scipy import stats

CONFIDENCE = 0.95


@dataclass(frozen=True)
class PairedDifference:
    """Mean of (treatment - baseline) over seeds with a two-sided t interval."""

    n: int
    mean: float | None
    low: float | None
    high: float | None


def paired_difference(
    baseline: Sequence[float | None], treatment: Sequence[float | None]
) -> PairedDifference:
    """Paired difference (treatment - baseline) with a 95% t interval.

    Pairs where either side is undefined or non-finite are dropped. With fewer than two
    pairs there is a mean but no interval; with none, everything is ``None``.
    The interval treats seeds as independent samples; it is a descriptive
    summary of seed-to-seed variation, not a claim about other worlds.
    """
    if len(baseline) != len(treatment):
        raise ValueError("baseline and treatment must have the same length")
    pairs = [
        (b, t)
        for b, t in zip(baseline, treatment, strict=True)
        if b is not None and t is not None and np.isfinite(b) and np.isfinite(t)
    ]
    differences = np.array([t - b for b, t in pairs], dtype=float)
    n = int(differences.size)
    if n == 0:
        return PairedDifference(0, None, None, None)
    mean = float(differences.mean())
    if n < 2:
        return PairedDifference(n, mean, None, None)
    half = float(stats.t.ppf(0.5 + CONFIDENCE / 2, n - 1) * differences.std(ddof=1) / np.sqrt(n))
    return PairedDifference(n, mean, mean - half, mean + half)
