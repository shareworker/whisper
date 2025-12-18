"""Cross-platform smoke tests for Whisper Subtitle Generator.

These tests verify that the application can run on both Windows and Linux
without requiring actual video processing or API calls.
"""

import os
import tempfile
from pathlib import Path

import pytest

from src.platform_utils import (
    Platform,
    check_external_tool,
    check_required_tools,
    get_platform,
    is_linux,
    is_windows,
)
from src.workspace import Workspace, create_workspace


class TestPlatformDetection:
    def test_get_platform_returns_valid_enum(self):
        plat = get_platform()
        assert plat in (Platform.WINDOWS, Platform.LINUX, Platform.UNKNOWN)

    def test_platform_helpers_are_mutually_exclusive(self):
        assert not (is_windows() and is_linux())

    def test_current_platform_detected(self):
        plat = get_platform()
        if os.name == "nt":
            assert plat == Platform.WINDOWS
        elif os.name == "posix":
            assert plat in (Platform.LINUX, Platform.UNKNOWN)


class TestExternalTools:
    def test_check_external_tool_ffmpeg(self):
        result = check_external_tool("ffmpeg")
        if result is not None:
            assert Path(result).exists()

    def test_check_external_tool_ytdlp(self):
        result = check_external_tool("yt-dlp")
        if result is not None:
            assert Path(result).exists()

    def test_check_required_tools_returns_dict(self):
        tools = check_required_tools()
        assert isinstance(tools, dict)
        assert "ffmpeg" in tools
        assert "yt-dlp" in tools


class TestWorkspace:
    def test_create_workspace_creates_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = create_workspace(base_dir=tmpdir)
            assert ws.root.exists()
            assert ws.root.is_dir()

    def test_workspace_paths_are_valid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = create_workspace(base_dir=tmpdir)
            assert ws.audio_path.parent == ws.root
            assert ws.original_srt_path.parent == ws.root
            assert ws.original_vtt_path.parent == ws.root
            assert ws.translated_srt_path.parent == ws.root
            assert ws.translated_vtt_path.parent == ws.root
            assert ws.bilingual_srt_path.parent == ws.root
            assert ws.bilingual_vtt_path.parent == ws.root

    def test_workspace_uses_pathlib(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = create_workspace(base_dir=tmpdir)
            assert isinstance(ws.root, Path)
            assert isinstance(ws.audio_path, Path)


class TestSubtitleWriting:
    def test_write_srt_creates_file(self):
        from src.subtitles import SubtitleSegment, write_srt

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.srt"
            segments = [SubtitleSegment(start=0.0, end=1.0, text="Hello")]
            write_srt(path, segments)
            assert path.exists()
            content = path.read_text(encoding="utf-8")
            assert "Hello" in content

    def test_write_vtt_creates_file(self):
        from src.subtitles import SubtitleSegment, write_vtt

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.vtt"
            segments = [SubtitleSegment(start=0.0, end=1.0, text="Hello")]
            write_vtt(path, segments)
            assert path.exists()
            content = path.read_text(encoding="utf-8")
            assert "WEBVTT" in content
            assert "Hello" in content
