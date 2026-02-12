# Video Downloader

A CLI tool that takes a webpage URL, finds video content within it (including embedded players), and downloads the video to a local folder.

## How It Works

The app uses a two-stage extraction pipeline:

1. **yt-dlp (primary)** — Handles 1000+ sites natively including YouTube, Vimeo, Twitter, TikTok, and most embedded players. Supports HLS/DASH streams, authentication, and format selection.

2. **Playwright browser fallback** — For pages yt-dlp can't parse, a headless Chromium browser renders the page with full JavaScript execution. It then:
   - Intercepts network requests for video streams (`.mp4`, `.m3u8`, `.mpd`, etc.)
   - Scrapes `<video>` and `<source>` elements from the rendered DOM
   - Checks `data-src`, `data-video-src` and similar attributes used by custom players
   - Discovers `<iframe>` embeds and attempts extraction on each

## Setup

```bash
pip install -r video_downloader/requirements.txt
playwright install chromium
```

## Usage

```bash
# Basic usage — downloads to video_downloader/downloads/
python -m video_downloader https://example.com/page-with-video

# Custom output directory
python -m video_downloader https://example.com/page-with-video --output ./my_videos
```

## Output

Videos are saved as MP4 (when possible) to the output directory with filenames based on the video title.
