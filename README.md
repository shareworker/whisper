# Whisper Subtitle Generator | Whisper 字幕生成器

[English](#english) | [中文](#chinese)

---

<a name="english"></a>
## English

### Introduction
A powerful web-based tool for generating subtitles from videos. It combines OpenAI's Whisper model for transcription and DeepSeek API for translation to produce high-quality bilingual subtitles.

### Features
- **Video Download**: Support for YouTube and other platforms via `yt-dlp`.
- **Local Support**: Process local video files directly.
- **Transcription**: High-accuracy speech-to-text using `faster-whisper`.
- **Translation**: AI-powered translation using DeepSeek API.
- **Dual-Mode**: Generates Original, Translated, and Bilingual subtitles automatically.
- **Live Preview**: Built-in video player with real-time subtitle preview and styling.
- **Format Support**: Export to standard SRT and VTT formats.

### Supported Platforms
- **Windows** (x64)
- **Linux** (x64, tested on Ubuntu 20.04+)

### Prerequisites
- Python 3.8+
- [FFmpeg](https://ffmpeg.org/download.html) (Must be in system PATH)
- DeepSeek API Key

### Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd whisper-subtitle-generator
   ```

2. Install system dependencies:

   **Windows:**
   - Download FFmpeg from https://ffmpeg.org/download.html and add to PATH
   - yt-dlp is installed via pip (step 3)

   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```

   **Linux (Fedora/RHEL):**
   ```bash
   sudo dnf install ffmpeg
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

1. Start the application:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to the displayed URL (usually `http://127.0.0.1:7860`).

3. Configure settings:
   - **Video Source**: Enter a URL or upload a local file.
   - **Language**: Select the source language (or use "auto").
   - **DeepSeek API**: Enter your API Key in the "Advanced" section (or set `DEEPSEEK_API_KEY` environment variable).

4. Click **Run**.

### Environment Variables
- `DEEPSEEK_API_KEY`: Your DeepSeek API key.
- `DEEPSEEK_BASE_URL`: Base URL for DeepSeek API (default: `https://api.deepseek.com`).
- `HTTP_PROXY` / `HTTPS_PROXY`: Proxy settings if needed.

### GPU Acceleration (Optional)
GPU acceleration significantly speeds up transcription. The application defaults to CUDA but falls back to CPU if unavailable.

**Windows:**
- Install NVIDIA drivers from https://www.nvidia.com/drivers
- CUDA toolkit is bundled with `faster-whisper` via CTranslate2

**Linux:**
```bash
# Install NVIDIA drivers (Ubuntu example)
sudo apt install nvidia-driver-535
# Verify installation
nvidia-smi
```

To use CPU instead, select "cpu" in the Device dropdown in the Advanced settings.

---

<a name="chinese"></a>
## 中文

### 简介
一个基于 Web 的强大视频字幕生成工具。结合了 OpenAI 的 Whisper 模型进行转写和 DeepSeek API 进行翻译，能够生成高质量的双语字幕。

### 功能特性
- **视频下载**：支持通过 `yt-dlp` 下载 YouTube 等平台的视频。
- **本地支持**：直接处理本地视频文件。
- **语音转写**：使用 `faster-whisper` 实现高精度语音转文字。
- **AI 翻译**：调用 DeepSeek API 进行智能翻译。
- **多模式生成**：自动生成“原文”、“译文”和“双语”三种字幕文件。
- **实时预览**：内置视频播放器，支持实时字幕预览和样式调整。
- **格式支持**：导出标准的 SRT 和 VTT 字幕格式。

### 支持平台
- **Windows** (x64)
- **Linux** (x64，已在 Ubuntu 20.04+ 测试)

### 前置要求
- Python 3.8+
- [FFmpeg](https://ffmpeg.org/download.html) (必须在系统 PATH 中)
- DeepSeek API Key

### 安装步骤

1. 克隆仓库：
   ```bash
   git clone <your-repo-url>
   cd whisper-subtitle-generator
   ```

2. 安装系统依赖：

   **Windows:**
   - 从 https://ffmpeg.org/download.html 下载 FFmpeg 并添加到 PATH
   - yt-dlp 通过 pip 安装（步骤 3）

   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```

   **Linux (Fedora/RHEL):**
   ```bash
   sudo dnf install ffmpeg
   ```

3. 安装 Python 依赖：
   ```bash
   pip install -r requirements.txt
   ```

### 使用方法

1. 启动应用：
   ```bash
   python app.py
   ```

2. 在浏览器中打开显示的地址（通常是 `http://127.0.0.1:7860`）。

3. 配置设置：
   - **视频源**：输入视频链接或上传本地文件。
   - **语言**：选择源语言（或使用 "auto" 自动检测）。
   - **DeepSeek API**：在 "Advanced"（高级）选项中输入 API Key（或者设置 `DEEPSEEK_API_KEY` 环境变量）。

4. 点击 **Run** 开始生成。

### 环境变量
- `DEEPSEEK_API_KEY`: 你的 DeepSeek API 密钥。
- `DEEPSEEK_BASE_URL`: DeepSeek API 的基础 URL（默认：`https://api.deepseek.com`）。
- `HTTP_PROXY` / `HTTPS_PROXY`: 如有需要，可设置代理。

### GPU 加速（可选）
GPU 加速可显著提升转写速度。应用默认使用 CUDA，如不可用则自动回退到 CPU。

**Windows:**
- 从 https://www.nvidia.com/drivers 安装 NVIDIA 驱动
- CUDA 工具包已通过 CTranslate2 随 `faster-whisper` 捆绑

**Linux:**
```bash
# 安装 NVIDIA 驱动（Ubuntu 示例）
sudo apt install nvidia-driver-535
# 验证安装
nvidia-smi
```

如需使用 CPU，请在高级设置的 Device 下拉菜单中选择 "cpu"。
