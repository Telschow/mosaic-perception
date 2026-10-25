# Mosaic

A synthetic benchmark for comparing a range-bearing-only tracker against one that also fuses vision bearings, with ground truth used only for evaluation.

## Timing

**Capture time**:
When a sensor measured the world; the observation's geometry and observer pose refer to this instant.
_Avoid_: Measurement time, sample time

**Delivery time**:
When an observation becomes available to the tracker after any transport delay.
_Avoid_: Arrival time, receive time

**Processing epoch**:
A tracker step at which tracks are predicted forward and all due observations are processed.
_Avoid_: Frame, tick

**Observation age**:
The processing epoch minus the capture time.
_Avoid_: Latency, delay

**Staleness limit**:
The maximum observation age the tracker admits; older observations are rejected, never replayed.
_Avoid_: Timeout, out-of-sequence window

## Observation outcomes

**Generated**:
Produced by a sensor, before any delay.

**Delivered**:
Removed from the pending queue at a processing epoch; generated observations still pending at the end are not delivered.

**Gate-rejected**:
Delivered, evaluated against at least one track, and failed the chi-square gate for every track.
_Avoid_: Unassigned, dropped

**Lost competition**:
Passed the gate for some track but lost the one-to-one assignment.

**Applied**:
Used in a track update.
_Avoid_: Accepted, fused (ambiguous before assignment)

## Tracks and evaluation

**Unmatched confirmed track**:
A confirmed track that was never matched to a true object in any frame; many are duplicates near true objects.
_Avoid_: False track, ghost track

**Duplicate track**:
A second confirmed track near a true object that already has a matched track.

**Range-only baseline**:
The method that uses only the range-bearing sensor; vision observations never reach it.
_Avoid_: Baseline (alone), non-fused

**Fused method**:
The method that adds vision bearing observations to the same tracker.

**Development seeds**:
Seeds 0–24, usable for debugging and the checked-in benchmark.

**Held-out seeds**:
Seeds 25–49, reserved and not run for any checked-in result.
_Avoid_: Test seeds

## Sensor disagreement

**Gate-rejection experiment**:
The large-bias scenario, whose question is whether the gate keeps grossly inconsistent vision observations out of the track.

**Within-gate bias experiment**:
The small-bias scenario, whose question is what happens when biased vision observations pass the gate and are fused.
