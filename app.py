import os

# Clear proxy environment variables for Gradio's internal HTTP communication
# This prevents httpx/httpcore from being affected by system proxy settings
# Note: yt-dlp subprocess will have its own environment handling in pipeline.py
for key in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"]:
    os.environ.pop(key, None)
os.environ["NO_PROXY"] = "*"

from typing import Generator, Optional, Tuple, Any, Dict

import gradio as gr

from src.pipeline import PipelineConfig, run_job



CUSTOM_CSS = """
video::cue {
    background-color: transparent !important;
    text-shadow: 2px 2px 4px #000000, -2px -2px 4px #000000;
    font-size: var(--subtitle-font-size, 24px) !important;
    line-height: 0.9 !important;
    padding: 0 !important;
    margin: 0 !important;
}
"""

def build_demo() -> gr.Blocks:
    with gr.Blocks(title="Whisper Subtitle Generator") as demo:
        gr.Markdown("# Whisper Subtitle Generator")

        # State to store paths of generated subtitles
        subtitle_paths = gr.State(value={
            "Original": None,
            "Translated": None,
            "Bilingual": None
        })

        with gr.Row():
            url = gr.Textbox(label="Video URL (YouTube or other supported platforms)", placeholder="https://...")
            local_video = gr.File(label="Local Video File", file_types=["video"], type="filepath")

        with gr.Row():
            transcription_language = gr.Dropdown(
                label="Transcription Language",
                choices=[
                    "auto",
                    "en",
                    "zh",
                    "ja",
                    "ko",
                    "fr",
                    "de",
                    "es",
                    "ru",
                ],
                value="auto",
            )
            # Output Mode removed, replaced by dynamic track selection below

        with gr.Accordion("Subtitle Settings", open=True):
            with gr.Row():
                subtitle_track = gr.Radio(
                    label="Subtitle Track",
                    choices=["Original", "Translated", "Bilingual"],
                    value="Bilingual",
                    interactive=True
                )
            
            font_size = gr.Slider(minimum=12, maximum=48, value=24, step=1, label="Subtitle Font Size (px)")
            vertical_pos = gr.Slider(minimum=0, maximum=100, value=90, step=1, label="Vertical Position (%)")
            
            # JavaScript to update CSS variable for font size
            font_size.change(
                fn=None,
                inputs=font_size,
                outputs=None,
                js="(x) => { document.documentElement.style.setProperty('--subtitle-font-size', x + 'px'); }"
            )
            
            # JavaScript to update VTT cue position
            vertical_pos.change(
                fn=None,
                inputs=vertical_pos,
                outputs=None,
                js="""
                (pos) => {
                    const videos = document.querySelectorAll('video');
                    videos.forEach(video => {
                        if (!video.textTracks || video.textTracks.length === 0) return;
                        const track = video.textTracks[0];
                        const cues = track.cues;
                        if (!cues) return;
                        
                        for (let i = 0; i < cues.length; i++) {
                            cues[i].snapToLines = false;
                            cues[i].line = pos; 
                        }
                    });
                }
                """
            )

        with gr.Accordion("Advanced", open=False):
            model_size = gr.Dropdown(
                label="Whisper Model",
                choices=["small", "medium", "large-v3"],
                value="medium",
            )
            device = gr.Dropdown(label="Device", choices=["cuda", "cpu"], value="cuda")

            deepseek_base_url = gr.Textbox(
                label="DEEPSEEK_BASE_URL (optional override)",
                placeholder="If empty, reads from environment",
                value="",
            )
            proxy = gr.Textbox(
                label="HTTP Proxy",
                placeholder="e.g., http://127.0.0.1:7890 (affects download and translation)",
                value="",
            )
            deepseek_api_key = gr.Textbox(
                label="DEEPSEEK_API_KEY",
                placeholder="Enter your API key here (or set DEEPSEEK_API_KEY env var)",
                type="password",
                value="",
            )
            deepseek_model = gr.Textbox(label="DeepSeek model", value="deepseek-chat")
            translation_target = gr.Dropdown(label="Translate to", choices=["zh"], value="zh")

        run_btn = gr.Button("Run", variant="primary")

        status = gr.Markdown(label="Status")
        preview = gr.Video(label="Preview", include_audio=True)

        with gr.Row():
            out_srt = gr.File(label="Output SRT (Bilingual)", type="filepath")
            out_vtt = gr.File(label="Output VTT (Bilingual)", type="filepath")

        workspace_dir = gr.Textbox(label="Workspace Directory", interactive=False)

        def _update_video_subtitles(track: str, paths: Dict[str, Optional[str]], current_video: Any):
            """Update the video component with the selected subtitle track."""
            if not current_video:
                return None
            
            # current_video might be a dict or a string path depending on Gradio version/state
            # But gr.Video output expects a Video object or path.
            # If we just want to update subtitles, we return a new gr.Video update.
            
            video_path = current_video
            if isinstance(current_video, dict):
                video_path = current_video.get("video") or current_video.get("name")

            vtt_path = paths.get(track)
            
            return gr.Video(value=video_path, subtitles=vtt_path)

        subtitle_track.change(
            fn=_update_video_subtitles,
            inputs=[subtitle_track, subtitle_paths, preview],
            outputs=preview
        )

        def _run(
            url_value: str,
            local_video_value: Optional[str],
            transcription_language_value: str,
            track_value: str, # Current subtitle track selection
            model_size_value: str,
            device_value: str,
            deepseek_base_url_value: str,
            proxy_value: str,
            deepseek_api_key_value: str,
            deepseek_model_value: str,
            translation_target_value: str,
        ) -> Generator[Tuple[str, Any, Optional[str], Optional[str], str, Dict[str, Optional[str]]], None, None]:
            compute_type_value = "int8" if device_value == "cpu" else "float16"
            cfg = PipelineConfig(
                url=(url_value or None),
                local_video_path=local_video_value,
                transcription_language=transcription_language_value,
                model_size=model_size_value,
                device=device_value,
                compute_type=compute_type_value,
                deepseek_api_key=(deepseek_api_key_value or os.environ.get("DEEPSEEK_API_KEY", "")),
                deepseek_base_url=(deepseek_base_url_value or os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")),
                deepseek_model=deepseek_model_value,
                translation_target=translation_target_value,
                proxy=(proxy_value or None),
            )

            current_paths = {
                "Original": None,
                "Translated": None,
                "Bilingual": None
            }

            for update in run_job(cfg):
                # Update paths state
                if update.original_vtt_path: current_paths["Original"] = update.original_vtt_path
                if update.translated_vtt_path: current_paths["Translated"] = update.translated_vtt_path
                if update.bilingual_vtt_path: current_paths["Bilingual"] = update.bilingual_vtt_path

                # Determine which subtitle to show based on current track selection
                selected_vtt = current_paths.get(track_value)
                
                # If selected track is not ready yet, fallback to available ones in order of preference
                if not selected_vtt:
                     if current_paths["Original"]: selected_vtt = current_paths["Original"]

                # Construct Video component update
                video_update = gr.Video(
                    value=update.video_path,
                    subtitles=selected_vtt
                ) if update.video_path else None

                yield (
                    update.status_markdown,
                    video_update,
                    update.bilingual_srt_path, # Default outputs to bilingual
                    update.bilingual_vtt_path,
                    update.workspace_dir,
                    current_paths
                )

        run_btn.click(
            _run,
            inputs=[
                url,
                local_video,
                transcription_language,
                subtitle_track,
                model_size,
                device,
                deepseek_base_url,
                proxy,
                deepseek_api_key,
                deepseek_model,
                translation_target,
            ],
            outputs=[status, preview, out_srt, out_vtt, workspace_dir, subtitle_paths],
        )

    return demo


if __name__ == "__main__":
    demo = build_demo()
    demo.launch(allowed_paths=[os.path.abspath("runs")], css=CUSTOM_CSS)
