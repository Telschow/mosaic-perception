"""Adapter that runs TrackEval's reference CLEAR/ID metrics on fixed sequences.

Dev/test-only: TrackEval is a development dependency and is never imported by
the package. The adapter bypasses TrackEval's MOTChallenge file/dataset layer
(git-era ``np.float``/``np.int`` aliases) and calls the reference metric
implementations directly on an in-memory data dict, which is the documented
input shape of ``CLEAR.eval_sequence`` and ``Identity.eval_sequence``.
"""

from __future__ import annotations

import contextlib
import io
import warnings
from typing import Any

import numpy as np

from .sequences import FixedSequence

TRACKEVAL_REPOSITORY = "https://github.com/JonathonLuiten/TrackEval"
TRACKEVAL_COMMIT = "12c8791b303e0a0b50f753af204249e622d0281a"
CLEAR_THRESHOLD = 0.5

_REFERENCES = ("int", "float", "bool")


@contextlib.contextmanager
def _legacy_numpy_aliases():
    """Restore the numpy aliases TrackEval still uses (removed in numpy 1.24)."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        missing = [name for name in _REFERENCES if not hasattr(np, name)]
        for name in missing:
            setattr(np, name, {"int": int, "float": float, "bool": bool}[name])
    try:
        yield
    finally:
        for name in missing:
            delattr(np, name)


def _box(position: tuple[float, float], size: float) -> np.ndarray:
    half = size / 2.0
    return np.array([position[0] - half, position[1] - half, size, size], dtype=float)


def _iou_matrix(gt_boxes: np.ndarray, tracker_boxes: np.ndarray) -> np.ndarray:
    """Axis-aligned IoU, the similarity TrackEval's CLEAR matching consumes."""
    if len(gt_boxes) == 0 or len(tracker_boxes) == 0:
        return np.zeros((len(gt_boxes), len(tracker_boxes)), dtype=float)
    gt = np.atleast_2d(gt_boxes)
    trk = np.atleast_2d(tracker_boxes)
    top_left = np.maximum(gt[:, None, :2], trk[None, :, :2])
    bottom_right = np.minimum(
        gt[:, None, 2:] + gt[:, None, :2], trk[None, :, 2:] + trk[None, :, :2]
    )
    wh = np.clip(bottom_right - top_left, 0.0, None)
    intersection = wh[..., 0] * wh[..., 1]
    gt_area = gt[:, 2] * gt[:, 3]
    trk_area = trk[:, 2] * trk[:, 3]
    union = gt_area[:, None] + trk_area[None, :] - intersection
    return np.divide(intersection, union, out=np.zeros_like(intersection), where=union > 0)


def build_trackeval_data(sequence: FixedSequence) -> dict[str, Any]:
    """Translate fixed sequences into TrackEval's documented data dict."""
    gt_label: dict[str, int] = {}
    tracker_label: dict[str, int] = {}
    gt_ids: list[np.ndarray] = []
    tracker_ids: list[np.ndarray] = []
    gt_dets: list[np.ndarray] = []
    tracker_dets: list[np.ndarray] = []
    similarities: list[np.ndarray] = []

    for state in sequence.states:
        gt_boxes = []
        gt_index = []
        for object_id, obj in state.objects.items():
            gt_label.setdefault(object_id, len(gt_label))
            gt_index.append(gt_label[object_id])
            gt_boxes.append(_box((obj.position.x, obj.position.y), sequence.box_size))

        snapshots = [s for s in sequence.snapshots if round(s.time, 9) == round(state.time, 9)]
        trk_boxes = []
        trk_index = []
        for snapshot in snapshots:
            tracker_label.setdefault(snapshot.track_id, len(tracker_label))
            trk_index.append(tracker_label[snapshot.track_id])
            trk_boxes.append(_box((snapshot.state[0], snapshot.state[1]), sequence.box_size))

        gt_array = np.asarray(gt_boxes, dtype=float).reshape(-1, 4)
        trk_array = np.asarray(trk_boxes, dtype=float).reshape(-1, 4)
        gt_ids.append(np.asarray(gt_index, dtype=int))
        tracker_ids.append(np.asarray(trk_index, dtype=int))
        gt_dets.append(gt_array)
        tracker_dets.append(trk_array)
        similarities.append(_iou_matrix(gt_array, trk_array))

    num_gt_dets = int(sum(len(ids) for ids in gt_ids))
    num_tracker_dets = int(sum(len(ids) for ids in tracker_ids))
    return {
        "num_timesteps": len(sequence.states),
        "num_gt_ids": len(gt_label),
        "num_tracker_ids": len(tracker_label),
        "num_gt_dets": num_gt_dets,
        "num_tracker_dets": num_tracker_dets,
        "gt_ids": gt_ids,
        "tracker_ids": tracker_ids,
        "gt_dets": gt_dets,
        "tracker_dets": tracker_dets,
        "tracker_confidences": [np.ones(len(ids), dtype=float) for ids in tracker_ids],
        "similarity_scores": similarities,
    }


def trackeval_version() -> str:
    from importlib.metadata import PackageNotFoundError, version

    try:
        return version("trackeval")
    except PackageNotFoundError:
        return "unknown"


def run_trackeval(sequence: FixedSequence) -> dict[str, float | int]:
    """Run the reference CLEAR and ID metrics on one fixed sequence."""
    data = build_trackeval_data(sequence)
    with _legacy_numpy_aliases(), contextlib.redirect_stdout(io.StringIO()):
        # TrackEval prints optional-dataset import errors on package import.
        from trackeval.metrics import CLEAR, Identity

        clear = CLEAR({"THRESHOLD": CLEAR_THRESHOLD, "PRINT_CONFIG": False})
        identity = Identity({"THRESHOLD": CLEAR_THRESHOLD, "PRINT_CONFIG": False})
        clear_result = clear.eval_sequence(data)
        identity_result = identity.eval_sequence(data)
    return {
        "mota": float(clear_result["MOTA"]),
        "clr_tp": int(clear_result["CLR_TP"]),
        "clr_fn": int(clear_result["CLR_FN"]),
        "clr_fp": int(clear_result["CLR_FP"]),
        "idsw": int(clear_result["IDSW"]),
        "idf1": float(identity_result["IDF1"]),
        "idp": float(identity_result["IDP"]),
        "idr": float(identity_result["IDR"]),
    }
