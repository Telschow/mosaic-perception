"""Paired-difference statistics on hand-made values."""

from __future__ import annotations

import numpy as np
import pytest
from scipy import stats

from mosaic_perception.evaluation.statistics import paired_difference


def test_paired_difference_mean_and_t_interval():
    baseline = [1.0, 2.0, 3.0, 4.0, 5.0]
    treatment = [0.8, 1.9, 2.7, 3.9, 4.6]  # differences: -0.2, -0.1, -0.3, -0.1, -0.4
    result = paired_difference(baseline, treatment)
    diffs = np.array([-0.2, -0.1, -0.3, -0.1, -0.4])
    expected_half = stats.t.ppf(0.975, 4) * diffs.std(ddof=1) / np.sqrt(5)
    assert result.n == 5
    assert result.mean == pytest.approx(diffs.mean())
    assert result.low == pytest.approx(diffs.mean() - expected_half)
    assert result.high == pytest.approx(diffs.mean() + expected_half)
    assert result.high < 0  # interval excludes zero: treatment is lower


def test_pairs_with_an_undefined_side_are_dropped():
    result = paired_difference([1.0, None, 3.0, 4.0], [0.9, 2.0, None, 3.8])
    assert result.n == 2
    assert result.mean == pytest.approx((-0.1 + -0.2) / 2)


def test_single_pair_has_a_mean_but_no_interval():
    result = paired_difference([1.0], [0.5])
    assert result.n == 1
    assert result.mean == pytest.approx(-0.5)
    assert result.low is None and result.high is None


def test_no_defined_pairs_gives_all_none():
    result = paired_difference([None, 1.0], [2.0, None])
    assert result.n == 0
    assert result.mean is None and result.low is None and result.high is None


def test_identical_differences_give_a_degenerate_interval():
    result = paired_difference([1.0, 2.0, 3.0], [0.9, 1.9, 2.9])
    assert result.mean == pytest.approx(-0.1)
    assert result.low == pytest.approx(-0.1)
    assert result.high == pytest.approx(-0.1)


def test_length_mismatch_is_rejected():
    with pytest.raises(ValueError):
        paired_difference([1.0, 2.0], [1.0])


def test_non_finite_values_are_treated_as_undefined():
    result = paired_difference(
        [1.0, float("nan"), 3.0, 4.0, float("inf")], [0.9, 2.0, 2.7, float("nan"), 1.0]
    )
    assert result.n == 2
    assert result.mean == pytest.approx((-0.1 + -0.3) / 2)
    assert np.isfinite(result.low) and np.isfinite(result.high)
