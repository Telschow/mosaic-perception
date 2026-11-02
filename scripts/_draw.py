"""Drawing helpers shared by the asset scripts: the bundled font and word wrapping."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def font(size: int, bold: bool = False):
    """DejaVu Sans from matplotlib's data directory, so text is the same on every machine."""
    import matplotlib
    from PIL import ImageFont

    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(str(Path(matplotlib.get_data_path()) / "fonts" / "ttf" / name), size)


def wrap(draw: Any, text: str, font: Any, width: int) -> list[str]:
    lines: list[str] = []
    line = ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if line and draw.textlength(trial, font=font) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    return [*lines, line]
