from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class SubtitleSegment:
    start: float
    end: float
    text: str


def _format_srt_timestamp(seconds: float) -> str:
    td = timedelta(seconds=max(0.0, seconds))
    total_ms = int(td.total_seconds() * 1000)
    hours = total_ms // 3600000
    minutes = (total_ms % 3600000) // 60000
    secs = (total_ms % 60000) // 1000
    ms = total_ms % 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def _format_vtt_timestamp(seconds: float) -> str:
    td = timedelta(seconds=max(0.0, seconds))
    total_ms = int(td.total_seconds() * 1000)
    hours = total_ms // 3600000
    minutes = (total_ms % 3600000) // 60000
    secs = (total_ms % 60000) // 1000
    ms = total_ms % 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{ms:03d}"


def _wrap_text(text: str, max_len: int = 80) -> str:
    # If text contains newlines (e.g. bilingual), process each line separately
    if "\n" in text:
        return "\n".join(_wrap_text(line, max_len) for line in text.split("\n"))

    t = " ".join((text or "").split())
    if len(t) <= max_len:
        return t

    words = t.split(" ")
    lines: List[str] = []
    current: List[str] = []
    cur_len = 0

    for w in words:
        add_len = len(w) + (1 if current else 0)
        if current and cur_len + add_len > max_len:
            lines.append(" ".join(current))
            current = [w]
            cur_len = len(w)
        else:
            current.append(w)
            cur_len += add_len

    if current:
        lines.append(" ".join(current))

    return "\n".join(lines)


def write_srt(path: Path, segments: Iterable[SubtitleSegment]) -> None:
    lines: List[str] = []
    for idx, seg in enumerate(segments, start=1):
        lines.append(str(idx))
        lines.append(f"{_format_srt_timestamp(seg.start)} --> {_format_srt_timestamp(seg.end)}")
        lines.append(_wrap_text(seg.text))
        lines.append("")

    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def write_vtt(path: Path, segments: Iterable[SubtitleSegment]) -> None:
    lines: List[str] = ["WEBVTT", ""]
    for seg in segments:
        lines.append(f"{_format_vtt_timestamp(seg.start)} --> {_format_vtt_timestamp(seg.end)}")
        lines.append(_wrap_text(seg.text))
        lines.append("")

    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
