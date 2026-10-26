"""Cross-check our MOTA, IDF1 and CLEAR counts against TrackEval (issue #30).

The expected numbers in ``tests/crosscheck/trackeval_reference.json`` were
produced by TrackEval's reference CLEAR and ID metric implementations
(version and commit recorded in that file) on the fixed sequences in
``tests/crosscheck/sequences.py``. The test runs our own evaluation pipeline
over the same sequences and requires agreement. Where a difference exists it
must be explained in ``docs/metrics.md`` rather than tolerated here.

The second test re-runs TrackEval live when it is installed (uv development
environment) so a stale fixture cannot pass; under a plain ``pip`` install the
TrackEval dependency is absent and it skips.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mosaic_perception.evaluation.metrics import TrackingEvaluator

from ..crosscheck.sequences import FixedSequence, fixed_sequences

_REFERENCE = json.loads(
    (Path(__file__).resolve().parents[1] / "crosscheck" / "trackeval_reference.json").read_text()
)

_FIELDS = ("mota", "clr_tp", "clr_fn", "clr_fp", "idsw", "idf1", "idp", "idr")


def _our_metrics(sequence: FixedSequence) -> dict:
    result = TrackingEvaluator().evaluate(
        sequence.snapshots,
        sequence.states,
        scenario_name=sequence.name,
        seed=0,
        method_name="crosscheck",
    )
    return {
        "mota": result.mota,
        "clr_tp": result.matched_samples,
        "clr_fn": result.unmatched_ground_truth_samples,
        "clr_fp": result.unmatched_track_samples,
        "idsw": result.identity_switches,
        "idf1": result.idf1,
        "idp": result.idp,
        "idr": result.idr,
    }


@pytest.mark.parametrize("sequence", fixed_sequences(), ids=lambda seq: seq.name)
def test_our_metrics_match_the_trackeval_reference(sequence: FixedSequence) -> None:
    reference = _REFERENCE["sequences"][sequence.name]
    ours = _our_metrics(sequence)
    for field in _FIELDS:
        if isinstance(reference[field], float):
            assert ours[field] == pytest.approx(reference[field], abs=1e-9), field
        else:
            assert ours[field] == reference[field], field


def test_recorded_reference_matches_pinned_trackeval() -> None:
    """Regenerating from the pinned TrackEval must reproduce the fixture."""
    pytest.importorskip("trackeval")
    from ..crosscheck.trackeval_harness import run_trackeval

    for sequence in fixed_sequences():
        live = run_trackeval(sequence)
        recorded = _REFERENCE["sequences"][sequence.name]
        for field in _FIELDS:
            if isinstance(recorded[field], float):
                assert live[field] == pytest.approx(recorded[field], abs=1e-12), (
                    sequence.name,
                    field,
                )
            else:
                assert live[field] == recorded[field], (sequence.name, field)
