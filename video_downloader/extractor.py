"""Primary video extraction using yt-dlp.

yt-dlp supports 1000+ sites natively and handles most embedded players,
iframes, and JS-rendered video sources out of the box.
"""

import os
import yt_dlp


def extract_and_download(url: str, output_dir: str) -> list[str]:
    """Try to extract and download videos from a URL using yt-dlp.

    Returns a list of downloaded file paths.
    """
    os.makedirs(output_dir, exist_ok=True)

    downloaded_files: list[str] = []

    def _progress_hook(d):
        if d["status"] == "finished":
            path = d.get("info_dict", {}).get("filepath") or d.get("filename")
            if path:
                downloaded_files.append(path)

    opts = {
        "outtmpl": os.path.join(output_dir, "%(title).80s [%(id)s].%(ext)s"),
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "merge_output_format": "mp4",
        "quiet": False,
        "no_warnings": False,
        "progress_hooks": [_progress_hook],
        # Handle embedded / iframe players
        "extract_flat": False,
        # Follow redirects and embedded URLs
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    return downloaded_files


def probe_url(url: str) -> dict | None:
    """Extract video metadata without downloading. Returns info dict or None."""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except yt_dlp.utils.DownloadError:
        return None
