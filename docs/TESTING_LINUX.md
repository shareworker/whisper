# Linux Testing Checklist

Manual verification steps for running Whisper Subtitle Generator on Linux.

## Prerequisites Check

- [ ] Python 3.8+ installed: `python3 --version`
- [ ] ffmpeg installed and in PATH: `ffmpeg -version`
- [ ] yt-dlp installed: `yt-dlp --version`
- [ ] (Optional) NVIDIA driver installed: `nvidia-smi`

## Installation Verification

```bash
# Clone and setup
git clone <repo-url>
cd whisper-subtitle-generator
pip install -r requirements.txt

# Run smoke tests
pytest tests/test_platform_smoke.py -v
```

## Functional Tests

### 1. Application Startup
- [ ] Run `python app.py`
- [ ] WebUI accessible at http://127.0.0.1:7860
- [ ] No errors in terminal output

### 2. Local Video Processing
- [ ] Upload a local video file (any short MP4)
- [ ] Select transcription language (or "auto")
- [ ] Enter DeepSeek API key in Advanced settings
- [ ] Click Run
- [ ] Verify: Status updates appear
- [ ] Verify: Video preview loads
- [ ] Verify: Subtitles display on video
- [ ] Verify: SRT/VTT files downloadable

### 3. URL Download (Optional - requires network)
- [ ] Enter a YouTube URL
- [ ] Click Run
- [ ] Verify: Download progress shown
- [ ] Verify: Processing completes successfully

### 4. Output Verification
- [ ] Check `runs/` directory for workspace folders
- [ ] Verify workspace contains:
  - `audio.wav`
  - `original.srt` / `original.vtt`
  - `translated.srt` / `translated.vtt`
  - `bilingual.srt` / `bilingual.vtt`
- [ ] Open SRT/VTT files - verify UTF-8 encoding and correct format

### 5. GPU/CPU Mode
- [ ] Test with Device: "cuda" (if GPU available)
- [ ] Test with Device: "cpu"
- [ ] Both modes should complete successfully

## Common Issues

| Issue | Solution |
|-------|----------|
| `ffmpeg: command not found` | `sudo apt install ffmpeg` |
| `yt-dlp: command not found` | `pip install yt-dlp` |
| CUDA not available | Select "cpu" in Device dropdown |
| Permission denied on `runs/` | `chmod 755 runs/` |

## Automated Smoke Test

```bash
# Quick verification
pytest tests/test_platform_smoke.py -v

# Expected: All tests pass
```
