"""Seed group is decided by set membership, not by the largest seed."""

from __future__ import annotations

from mosaic_perception.cli.main import seed_group


def test_development_seeds_are_labelled_development():
    assert seed_group(list(range(0, 25))) == "development"
    assert seed_group([3, 4, 5]) == "development"


def test_reserved_seeds_are_labelled_held_out():
    assert seed_group(list(range(25, 50))) == "held_out"


def test_mixed_or_out_of_range_seeds_are_custom():
    assert seed_group(list(range(10, 31))) == "custom"
    assert seed_group([100]) == "custom"
