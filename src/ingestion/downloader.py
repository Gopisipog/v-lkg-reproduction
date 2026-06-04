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
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return [
                {
                    "start": seg["start"],
                    "end":   seg["start"] + seg["duration"],
                    "text":  seg["text"].strip(),
                }
                for seg in transcript
            ]
        except Exception as e:
            print(f"Failed to fetch transcript for {video_id}: {e}")
            return None

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
