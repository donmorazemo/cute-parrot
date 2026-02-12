"""Browser-based fallback for pages where yt-dlp cannot find videos.

Uses Playwright to render the page with full JavaScript execution, then:
1. Intercepts network requests for video streams (.mp4, .m3u8, .mpd, etc.)
2. Scrapes <video> and <source> elements from the rendered DOM
3. Finds <iframe> embeds and recursively checks them via yt-dlp

Any discovered video URLs are then downloaded via yt-dlp or direct HTTP.
"""

import os
import re
import hashlib
from urllib.parse import urljoin, urlparse

import requests

VIDEO_EXTENSIONS = re.compile(
    r"\.(mp4|webm|m3u8|mpd|ts|mov|avi|mkv|flv|m4v)(\?|$)", re.IGNORECASE
)
VIDEO_MIME_TYPES = re.compile(r"^(video/|application/x-mpegurl|application/dash\+xml)")


def _hash_url(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:12]


def _filename_from_url(url: str) -> str:
    path = urlparse(url).path
    name = os.path.basename(path) or "video"
    if not re.search(r"\.\w{2,5}$", name):
        name += ".mp4"
    return name


def _download_direct(url: str, output_dir: str) -> str | None:
    """Download a direct video URL via HTTP streaming."""
    dest = os.path.join(output_dir, _filename_from_url(url))
    # Avoid collisions
    if os.path.exists(dest):
        base, ext = os.path.splitext(dest)
        dest = f"{base}_{_hash_url(url)}{ext}"

    try:
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            content_type = r.headers.get("content-type", "")
            if "text/html" in content_type:
                return None  # Not actually a video
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 256):
                    f.write(chunk)
        size = os.path.getsize(dest)
        if size < 10_000:  # Likely not a real video
            os.remove(dest)
            return None
        return dest
    except Exception:
        if os.path.exists(dest):
            os.remove(dest)
        return None


def _try_ytdlp(url: str, output_dir: str) -> str | None:
    """Attempt to download a single discovered URL via yt-dlp."""
    try:
        from video_downloader.extractor import extract_and_download

        files = extract_and_download(url, output_dir)
        return files[0] if files else None
    except Exception:
        return None


def extract_via_browser(url: str, output_dir: str) -> list[str]:
    """Render the page in a headless browser, find video sources, download them."""
    from playwright.sync_api import sync_playwright

    os.makedirs(output_dir, exist_ok=True)

    discovered_urls: set[str] = set()
    iframe_urls: set[str] = set()

    def _on_response(response):
        req_url = response.url
        content_type = response.headers.get("content-type", "")
        if VIDEO_EXTENSIONS.search(req_url) or VIDEO_MIME_TYPES.search(content_type):
            discovered_urls.add(req_url)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()
        page.on("response", _on_response)

        try:
            page.goto(url, wait_until="networkidle", timeout=30_000)
        except Exception:
            # Even on timeout, we may have captured network requests
            pass

        # Give lazy-loaded players a moment
        page.wait_for_timeout(3000)

        # Scrape <video> and <source> elements
        video_srcs = page.evaluate("""
            () => {
                const urls = new Set();
                document.querySelectorAll('video').forEach(v => {
                    if (v.src) urls.add(v.src);
                    if (v.currentSrc) urls.add(v.currentSrc);
                });
                document.querySelectorAll('video source').forEach(s => {
                    if (s.src) urls.add(s.src);
                });
                // Also check data attributes commonly used by custom players
                document.querySelectorAll('[data-src],[data-video-src],[data-video-url]').forEach(el => {
                    for (const attr of ['data-src', 'data-video-src', 'data-video-url']) {
                        const val = el.getAttribute(attr);
                        if (val && (val.includes('.mp4') || val.includes('.m3u8') || val.includes('.webm'))) {
                            urls.add(val);
                        }
                    }
                });
                return [...urls];
            }
        """)
        for src in video_srcs:
            if src:
                discovered_urls.add(urljoin(url, src))

        # Find iframes (potential embedded players)
        iframe_srcs = page.evaluate("""
            () => {
                return [...document.querySelectorAll('iframe')]
                    .map(f => f.src)
                    .filter(s => s && !s.startsWith('about:'));
            }
        """)
        for src in iframe_srcs:
            iframe_urls.add(urljoin(url, src))

        browser.close()

    downloaded: list[str] = []

    # Download discovered direct video URLs
    for video_url in discovered_urls:
        # For streaming formats (m3u8, mpd), use yt-dlp
        if re.search(r"\.(m3u8|mpd)(\?|$)", video_url, re.IGNORECASE):
            result = _try_ytdlp(video_url, output_dir)
        else:
            result = _download_direct(video_url, output_dir)
        if result:
            downloaded.append(result)

    # Try embedded iframe URLs through yt-dlp
    for iframe_url in iframe_urls:
        result = _try_ytdlp(iframe_url, output_dir)
        if result:
            downloaded.append(result)

    return downloaded
