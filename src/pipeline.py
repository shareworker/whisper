import os
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Generator, List, Optional
from urllib.parse import quote

from faster_whisper import WhisperModel

from src.deepseek_client import DeepSeekClient
from src.subtitles import SubtitleSegment, write_srt, write_vtt
from src.workspace import Workspace, create_workspace, ensure_local_media, set_media_path


@dataclass(frozen=True)
class PipelineConfig:
    url: Optional[str]
    local_video_path: Optional[str]
    transcription_language: str
    model_size: str
    device: str
    compute_type: str
    deepseek_api_key: str
    deepseek_base_url: str
    deepseek_model: str
    translation_target: str
    proxy: Optional[str] = None


@dataclass(frozen=True)
class JobUpdate:
    status_markdown: str
    video_path: Optional[str]
    # VTT paths for web player
    original_vtt_path: Optional[str]
    translated_vtt_path: Optional[str]
    bilingual_vtt_path: Optional[str]
    # SRT paths for download
    original_srt_path: Optional[str]
    translated_srt_path: Optional[str]
    bilingual_srt_path: Optional[str]
    workspace_dir: str


def _run_command(args: List[str], restore_proxy: bool = False) -> None:
    # Copy environment
    env = os.environ.copy()
    
    # Remove NO_PROXY to avoid interfering with yt-dlp's proxy resolution
    if "NO_PROXY" in env:
        del env["NO_PROXY"]
    if "no_proxy" in env:
        del env["no_proxy"]
        
    proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(args)}\n\n{proc.stdout}")


def _download_with_ytdlp(url: str, workspace: Workspace, proxy: Optional[str] = None) -> Path:
    out_template = str(workspace.root / "source.%(ext)s")
    args = [
        "yt-dlp",
        "--no-playlist",
        "--force-ipv4",
        "--socket-timeout", "60",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "-o",
        out_template,
        url,
    ]
    if proxy:
        args.extend(["--proxy", proxy])

    _run_command(args)

    candidates = list(workspace.root.glob("source.*"))
    if not candidates:
        raise RuntimeError("yt-dlp did not produce an output file")

    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def _extract_audio(video_path: Path, audio_path: Path) -> None:
    args = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        str(audio_path),
    ]
    _run_command(args)


def _transcribe(cfg: PipelineConfig, audio_path: Path) -> List[SubtitleSegment]:
    language = None if cfg.transcription_language == "auto" else cfg.transcription_language

    model = WhisperModel(cfg.model_size, device=cfg.device, compute_type=cfg.compute_type)
    segments_iter, _info = model.transcribe(
        str(audio_path),
        language=language,
        vad_filter=True,
        beam_size=5,
    )

    segments: List[SubtitleSegment] = []
    for seg in segments_iter:
        segments.append(SubtitleSegment(start=float(seg.start), end=float(seg.end), text=(seg.text or "").strip()))

    return segments


def _translate_segments(
    cfg: PipelineConfig,
    segments: List[SubtitleSegment],
) -> List[SubtitleSegment]:
    client = DeepSeekClient(
        base_url=cfg.deepseek_base_url,
        api_key=cfg.deepseek_api_key,
        model=cfg.deepseek_model,
        proxy=cfg.proxy or "",
    )

    batch_size = 20
    translated_texts: List[str] = []
    texts = [s.text for s in segments]

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        translated_texts.extend(client.translate_batch(batch, cfg.translation_target))

    if len(translated_texts) != len(segments):
        raise RuntimeError("Translation output length mismatch")

    out: List[SubtitleSegment] = []
    for seg, zh in zip(segments, translated_texts):
        out.append(SubtitleSegment(start=seg.start, end=seg.end, text=zh))

    return out


def run_job(cfg: PipelineConfig) -> Generator[JobUpdate, None, None]:
    if not cfg.url and not cfg.local_video_path:
        raise ValueError("Provide either a URL or a local video file")

    workspace = create_workspace()

    yield JobUpdate(
        status_markdown="**Starting job...**",
        video_path=None,
        original_vtt_path=None,
        translated_vtt_path=None,
        bilingual_vtt_path=None,
        original_srt_path=None,
        translated_srt_path=None,
        bilingual_srt_path=None,
        workspace_dir=str(workspace.root),
    )

    if cfg.url:
        yield JobUpdate(
            status_markdown="**Downloading video...**",
            video_path=None,
            original_vtt_path=None,
            translated_vtt_path=None,
            bilingual_vtt_path=None,
            original_srt_path=None,
            translated_srt_path=None,
            bilingual_srt_path=None,
            workspace_dir=str(workspace.root),
        )
        downloaded = _download_with_ytdlp(cfg.url, workspace, cfg.proxy)
        video_path = set_media_path(workspace, str(downloaded))
    else:
        video_path = ensure_local_media(workspace, cfg.local_video_path or "")

    yield JobUpdate(
        status_markdown="**Extracting audio...**",
        video_path=str(video_path),
        original_vtt_path=None,
        translated_vtt_path=None,
        bilingual_vtt_path=None,
        original_srt_path=None,
        translated_srt_path=None,
        bilingual_srt_path=None,
        workspace_dir=str(workspace.root),
    )
    _extract_audio(video_path, workspace.audio_path)

    yield JobUpdate(
        status_markdown="**Transcribing (this may take a while)...**",
        video_path=str(video_path),
        original_vtt_path=None,
        translated_vtt_path=None,
        bilingual_vtt_path=None,
        original_srt_path=None,
        translated_srt_path=None,
        bilingual_srt_path=None,
        workspace_dir=str(workspace.root),
    )
    segments = _transcribe(cfg, workspace.audio_path)
    write_srt(workspace.original_srt_path, segments)
    write_vtt(workspace.original_vtt_path, segments)

    yield JobUpdate(
        status_markdown="**Transcription complete. Translating...**",
        video_path=str(video_path),
        original_vtt_path=str(workspace.original_vtt_path),
        translated_vtt_path=None,
        bilingual_vtt_path=None,
        original_srt_path=str(workspace.original_srt_path),
        translated_srt_path=None,
        bilingual_srt_path=None,
        workspace_dir=str(workspace.root),
    )

    translated_segments = _translate_segments(cfg, segments)
    write_srt(workspace.translated_srt_path, translated_segments)
    write_vtt(workspace.translated_vtt_path, translated_segments)

    # Create bilingual segments
    bilingual_segments: List[SubtitleSegment] = []
    for orig, trans in zip(segments, translated_segments):
        bilingual_segments.append(
            SubtitleSegment(
                start=orig.start,
                end=orig.end,
                text=f"{orig.text}\n{trans.text}"
            )
        )
    write_srt(workspace.bilingual_srt_path, bilingual_segments)
    write_vtt(workspace.bilingual_vtt_path, bilingual_segments)

    yield JobUpdate(
        status_markdown="**All Done!**",
        video_path=str(video_path),
        original_vtt_path=str(workspace.original_vtt_path),
        translated_vtt_path=str(workspace.translated_vtt_path),
        bilingual_vtt_path=str(workspace.bilingual_vtt_path),
        original_srt_path=str(workspace.original_srt_path),
        translated_srt_path=str(workspace.translated_srt_path),
        bilingual_srt_path=str(workspace.bilingual_srt_path),
        workspace_dir=str(workspace.root),
    )
