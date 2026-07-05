import yt_dlp
import os
import re


class YouTubeDownloader:
    """Wrapper for yt-dlp to download video and audio from YouTube URLs.

    For cloud environments where YouTube blocks downloads (HTTP 403),
    the app falls back to fetching transcript-only via youtube-transcript-api.
    """

    # Realistic browser headers to avoid 403 blocks
    _USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    def __init__(self, output_dir="data/raw"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def fetch_metadata(self, url):
        """Fetches video title, channel, thumbnail and duration without downloading."""
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "http_headers": {"User-Agent": self._USER_AGENT},
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return {
            "video_id":     info.get("id", "unknown"),
            "title":        info.get("title", "Unknown Title"),
            "url":          url,
            "thumbnail_url": info.get("thumbnail", ""),
            "channel":      info.get("uploader", "Unknown"),
            "duration_sec": info.get("duration", 0),
        }

    def _ffmpeg_dir(self):
        """Returns the directory containing the ffmpeg binary."""
        import shutil
        ffmpeg_bin = shutil.which('ffmpeg')
        return os.path.dirname(ffmpeg_bin) if ffmpeg_bin else None

    def download_video(self, url, video_id="video"):
        """Downloads the video file for OCR processing.

        May fail with 403 Forbidden on cloud servers (AWS/GCP/Azure).
        Use fetch_transcript_only as fallback instead.
        """
        filename = f"{video_id}.mp4"
        out_path  = os.path.join(self.output_dir, filename)
        print(f"Downloading video [{video_id}] to {out_path}...")

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': out_path,
            'ffmpeg_location': self._ffmpeg_dir(),
            'overwrites': True,
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'http_headers': {"User-Agent": self._USER_AGENT},
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.path.exists(out_path):
            raise FileNotFoundError(f"Video download failed — file not found: {out_path}")
        return out_path

    def download_audio(self, url, video_id="audio"):
        """Downloads and converts to MP3 for Whisper transcription.

        May fail with 403 Forbidden on cloud servers (AWS/GCP/Azure).
        Use fetch_transcript_only as fallback instead.
        """
        base_name = f"{video_id}_audio"
        out_path  = os.path.join(self.output_dir, f"{base_name}.mp3")
        print(f"Downloading audio [{video_id}] to {out_path}...")

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(self.output_dir, base_name),
            'ffmpeg_location': self._ffmpeg_dir(),
            'overwrites': True,
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'http_headers': {"User-Agent": self._USER_AGENT},
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.path.exists(out_path):
            raise FileNotFoundError(f"Audio download failed — file not found: {out_path}")
        return out_path

    def fetch_transcript_only(self, video_id):
        """Fetch captions directly via YouTube API (no download needed).

        Uses the youtube-transcript-api package which works from cloud servers
        since it uses YouTube's public caption endpoints.
        Returns a list of {start, end, text} segments, or None on failure.
        """
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
        except ImportError:
            print("youtube-transcript-api not installed. Cannot fetch transcript.")
            return None

        try:
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id)
            raw = transcript.to_raw_data()
            if raw and isinstance(raw, list):
                return [
                    {
                        "start": seg.get("start", 0),
                        "end":   seg.get("start", 0) + seg.get("duration", 0),
                        "text":  seg.get("text", "").strip(),
                    }
                    for seg in raw if seg.get("text", "").strip()
                ]
            return None
        except Exception as e:
            print(f"Failed to fetch transcript via youtube-transcript-api for {video_id}: {e}")
            return None

    def fetch_subtitles_via_ytdlp(self, video_id):
        """Extract auto-generated subtitles using yt-dlp (no video download).

        This is a second fallback for videos without manual captions.
        Returns a list of {start, end, text} segments, or None on failure.
        """
        url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"Fetching subtitles via yt-dlp for {video_id}...")

        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitlesformat": "vtt",
                "skip_download": True,
                "subtitleslangs": ["en"],
                "http_headers": {"User-Agent": self._USER_AGENT},
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

            # Check if subtitles were downloaded
            import glob
            sub_files = glob.glob(os.path.join(self.output_dir, f"{video_id}*.vtt"))
            sub_files += glob.glob(os.path.join(self.output_dir, f"{video_id}*.srt"))

            if not sub_files:
                # Try accessing embedded subtitles from the info dict
                subs = info.get("subtitles", {}) or {}
                auto_subs = info.get("automatic_captions", {}) or {}
                print(f"  yt-dlp found subtitles: {list(subs.keys())}, auto-captions: {list(auto_subs.keys())}")
                return None

            # Parse the first subtitle file
            sub_path = sub_files[0]
            segments = []
            with open(sub_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse VTT or SRT format
            if sub_path.endswith(".vtt"):
                segments = self._parse_vtt(content)
            elif sub_path.endswith(".srt"):
                segments = self._parse_srt(content)

            # Clean up sub file
            try:
                os.remove(sub_path)
            except OSError:
                pass

            return segments

        except Exception as e:
            print(f"Failed to fetch subtitles via yt-dlp for {video_id}: {e}")
            return None

    def fetch_captions_from_info(self, video_id):
        """Extract captions from yt-dlp's info dict without downloading video.

        This fetches the caption URLs from the video metadata page and downloads
        them directly. Works even when video download is blocked (403).
        """
        url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"Fetching captions from video info for {video_id}...")

        try:
            # Extract info only - no download
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "writesubtitles": False,
                "writeautomaticsub": False,
                "http_headers": {"User-Agent": self._USER_AGENT},
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            # Collect all caption tracks
            all_captions = {}
            subtitles = info.get("subtitles") or {}
            auto_captions = info.get("automatic_captions") or {}

            # Prefer manual subtitles first, then auto-generated
            for lang in ["en", "en-GB", "en-US"]:
                if lang in subtitles and subtitles[lang]:
                    all_captions[lang] = subtitles[lang]
                elif lang in auto_captions and auto_captions[lang]:
                    all_captions[lang] = auto_captions[lang]

            # Pick any available language as fallback
            if not all_captions:
                for lang in subtitles:
                    all_captions[lang] = subtitles[lang]
                    break
            if not all_captions:
                for lang in auto_captions:
                    all_captions[lang] = auto_captions[lang]
                    break

            if not all_captions:
                print(f"  No captions found in video info for {video_id}")
                return None

            # Download the first available caption track (prefer VTT or SRT or JSON3)
            import requests
            lang = list(all_captions.keys())[0]
            tracks = all_captions[lang]

            # Find the best format: prefer vtt/srv3/json3 over plain text
            preferred_exts = ["vtt", "srv3", "json3", "srt", "ttml"]
            selected_url = None
            for ext in preferred_exts:
                for track in tracks:
                    if track.get("ext") == ext:
                        selected_url = track.get("url")
                        break
                if selected_url:
                    break
            if not selected_url and tracks:
                selected_url = tracks[0].get("url")

            if not selected_url:
                print(f"  No caption URL found for {video_id}")
                return None

            # Download the caption file
            resp = requests.get(selected_url, headers={"User-Agent": self._USER_AGENT})
            resp.raise_for_status()
            content = resp.text

            # Parse based on format
            segments = None
            if selected_url.endswith(".vtt") or "vtt" in selected_url:
                segments = self._parse_vtt(content)
            elif selected_url.endswith(".srv3") or "srv3" in selected_url or \
                 selected_url.endswith(".json3") or "json3" in selected_url:
                segments = self._parse_json3(content)
            elif selected_url.endswith(".srt") or "srt" in selected_url:
                segments = self._parse_srt(content)
            elif selected_url.endswith(".ttml") or "ttml" in selected_url or "xml" in selected_url:
                segments = self._parse_ttml(content)
            else:
                # Try VTT parser as default
                segments = self._parse_vtt(content)

            if segments:
                print(f"  Successfully extracted {len(segments)} caption segments via yt-dlp info")
            return segments

        except Exception as e:
            print(f"  Failed to extract captions from video info for {video_id}: {e}")
            return None

    @staticmethod
    def _parse_vtt(content):
        """Parse WebVTT subtitle content into segments."""
        segments = []
        lines = content.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            # Match timestamp line like "00:01:23.456 --> 00:01:25.789"
            if "-->" in line:
                parts = line.split("-->")
                if len(parts) == 2:
                    start_str = parts[0].strip().replace(",", ".")
                    end_str = parts[1].strip().replace(",", ".")
                    start = sum(float(x) * 60 ** (2 - j) for j, x in enumerate(start_str.split(":")))
                    end = sum(float(x) * 60 ** (2 - j) for j, x in enumerate(end_str.split(":")))
                    # Collect text lines until blank line
                    text_parts = []
                    i += 1
                    while i < len(lines) and lines[i].strip():
                        text_parts.append(lines[i].strip())
                        i += 1
                    text = " ".join(text_parts)
                    if text.strip():
                        segments.append({
                            "start": start,
                            "end": end,
                            "text": text.strip(),
                        })
            i += 1
        return segments

    @staticmethod
    def _parse_srt(content):
        """Parse SRT subtitle content into segments."""
        segments = []
        blocks = content.strip().split("\n\n")
        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) >= 3:
                # Line 2 is timestamp
                time_line = lines[1]
                if "-->" in time_line:
                    parts = time_line.split("-->")
                    start_str = parts[0].strip().replace(",", ".")
                    end_str = parts[1].strip().replace(",", ".")
                    start = sum(float(x) * 60 ** (2 - j) for j, x in enumerate(start_str.split(":")))
                    end = sum(float(x) * 60 ** (2 - j) for j, x in enumerate(end_str.split(":")))
                    text = " ".join(lines[2:]).strip()
                    if text:
                        segments.append({
                            "start": start,
                            "end": end,
                            "text": text,
                        })
        return segments

    @staticmethod
    def _parse_json3(content):
        """Parse YouTube JSON3 caption format."""
        import json as json_module
        segments = []
        try:
            data = json_module.loads(content)
            events = data.get("events", [])
            for event in events:
                start = event.get("tStartMs", 0) / 1000.0
                duration = event.get("dDurationMs", 0) / 1000.0
                segs = event.get("segs", [])
                text_parts = []
                for seg in segs:
                    utf8 = seg.get("utf8", "")
                    if utf8:
                        text_parts.append(utf8)
                text = " ".join(text_parts).strip()
                if text:
                    segments.append({
                        "start": start,
                        "end": start + duration,
                        "text": text,
                    })
        except Exception:
            pass
        return segments

    @staticmethod
    def _parse_ttml(content):
        """Parse TTML/XML subtitle content."""
        import re as re_module
        segments = []
        # Simple XML parsing for ttml
        import xml.etree.ElementTree as ET
        try:
            root = ET.fromstring(content)
            # Namespace handling
            ns = {"tt": "http://www.w3.org/ns/ttml"}
            for p in root.iter("{http://www.w3.org/ns/ttml}p"):
                begin = p.get("begin", "0s")
                end = p.get("end", "0s")
                # Parse time format like "00:01:23.456" or "123.456s"
                text = "".join(p.itertext()).strip()
                if text:
                    def parse_ttml_time(t):
                        t = t.strip()
                        if t.endswith("s"):
                            return float(t[:-1])
                        if t.endswith("ms"):
                            return float(t[:-2]) / 1000
                        parts = t.split(":")
                        if len(parts) == 3:
                            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                        return 0
                    s = parse_ttml_time(begin)
                    e = parse_ttml_time(end)
                    if e <= s:
                        e = s + 10
                    segments.append({"start": s, "end": e, "text": text})
        except Exception:
            pass
        return segments

    @staticmethod
    def extract_video_id(url):
        """Extract YouTube video ID from various URL formats."""
        patterns = [
            r"(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})",
            r"(?:embed/)([a-zA-Z0-9_-]{11})",
            r"(?:shorts/)([a-zA-Z0-9_-]{11})",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
