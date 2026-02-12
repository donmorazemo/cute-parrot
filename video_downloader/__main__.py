"""CLI entry point: python -m video_downloader <URL> [--output DIR]"""

import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Download video content from a webpage URL.",
        epilog="Examples:\n"
        "  python -m video_downloader https://example.com/page-with-video\n"
        "  python -m video_downloader https://youtube.com/watch?v=xyz --output ./my_videos\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("url", help="Webpage URL containing video content")
    parser.add_argument(
        "-o",
        "--output",
        default=os.path.join(os.path.dirname(__file__), "downloads"),
        help="Output directory for downloaded videos (default: video_downloader/downloads/)",
    )
    args = parser.parse_args()

    output_dir = os.path.abspath(args.output)
    os.makedirs(output_dir, exist_ok=True)

    print(f"[*] Target URL : {args.url}")
    print(f"[*] Output dir : {output_dir}")
    print()

    # --- Stage 1: yt-dlp (handles most sites natively) ---
    print("[1/2] Trying yt-dlp extraction...")
    downloaded: list[str] = []
    try:
        from video_downloader.extractor import extract_and_download

        downloaded = extract_and_download(args.url, output_dir)
    except Exception as e:
        print(f"      yt-dlp failed: {e}")

    if downloaded:
        _print_results(downloaded)
        return

    # --- Stage 2: Browser fallback ---
    print()
    print("[2/2] yt-dlp found nothing — launching browser fallback...")
    try:
        from video_downloader.browser_fallback import extract_via_browser

        downloaded = extract_via_browser(args.url, output_dir)
    except ImportError:
        print(
            "      Playwright is not installed. Install it with:\n"
            "        pip install playwright && playwright install chromium"
        )
        sys.exit(1)
    except Exception as e:
        print(f"      Browser extraction failed: {e}")

    if downloaded:
        _print_results(downloaded)
    else:
        print()
        print("[!] No video content found on this page.")
        sys.exit(1)


def _print_results(files: list[str]):
    print()
    print(f"[+] Downloaded {len(files)} video(s):")
    for f in files:
        size_mb = os.path.getsize(f) / (1024 * 1024)
        print(f"    {f}  ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
