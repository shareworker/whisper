import os
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class Workspace:
    root: Path

    @property
    def media_path(self) -> Path:
        return self.root / "media"

    @property
    def audio_path(self) -> Path:
        return self.root / "audio.wav"

    @property
    def original_srt_path(self) -> Path:
        return self.root / "original.srt"

    @property
    def original_vtt_path(self) -> Path:
        return self.root / "original.vtt"

    @property
    def translated_srt_path(self) -> Path:
        return self.root / "translated.srt"

    @property
    def translated_vtt_path(self) -> Path:
        return self.root / "translated.vtt"

    @property
    def bilingual_srt_path(self) -> Path:
        return self.root / "bilingual.srt"

    @property
    def bilingual_vtt_path(self) -> Path:
        return self.root / "bilingual.vtt"


def create_workspace(base_dir: str = "runs") -> Workspace:
    base = Path(base_dir)
    base.mkdir(parents=True, exist_ok=True)
    ws_dir = base / f"job-{uuid.uuid4().hex}"
    ws_dir.mkdir(parents=True, exist_ok=False)
    return Workspace(root=ws_dir)


def ensure_local_media(workspace: Workspace, local_video_path: str) -> Path:
    src = Path(local_video_path)
    if not src.exists():
        raise FileNotFoundError(f"Local video file not found: {local_video_path}")

    dst = workspace.media_path.with_suffix(src.suffix)
    shutil.copy2(src, dst)
    return dst


def set_media_path(workspace: Workspace, downloaded_media_path: str) -> Path:
    src = Path(downloaded_media_path)
    if not src.exists():
        raise FileNotFoundError(f"Downloaded media file not found: {downloaded_media_path}")

    dst = workspace.media_path.with_suffix(src.suffix)
    if src.resolve() == dst.resolve():
        return dst

    shutil.move(str(src), str(dst))
    return dst
