"""Smoke test: the Streamlit app imports and renders without a browser (issue #33).

Uses Streamlit's in-process test harness, so no server and no browser are
started. The data-preparation logic itself is covered by
``test_app_data_prep``; this test only proves the wiring holds together.
"""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

_APP = Path(__file__).resolve().parents[2] / "app" / "streamlit_app.py"


def test_app_renders_and_runs_a_short_simulation() -> None:
    app = AppTest.from_file(str(_APP), default_timeout=60)
    app.run()
    assert not app.exception, app.exception
    assert app.title[0].value == "Mosaic: Multi-Sensor Perception Workbench"

    seed_slider = app.sidebar.slider[0]
    assert seed_slider.value == 1
    assert seed_slider.max == 24

    app.sidebar.selectbox[0].select("nominal")
    app.sidebar.slider[1].set_value(2.0)
    app.sidebar.slider[2].set_value(1)
    app.button[0].click().run()

    assert not app.exception, app.exception
    assert len(app.dataframe) == 1
    assert len(app.get("plotly_chart")) == 1
    captions = [caption.value for caption in app.caption]
    assert any("Simulated data" in caption for caption in captions)
    assert any("limitations" in caption.lower() for caption in captions)
