from flask import Flask, Response, request, abort
from yt_dlp import YoutubeDL
import requests

app = Flask(__name__)

YDL_OPTS = {
    "quiet": True,
    "noplaylist": True,
    "format": "best",
}

@app.route("/")
def index():
    return "Running"

@app.route("/video/<video_id>")
def video(video_id):
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        with YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(youtube_url, download=False)

        stream_url = info["url"]

        # Forward Range requests so seeking works
        headers = {}
        if "Range" in request.headers:
            headers["Range"] = request.headers["Range"]

        upstream = requests.get(
            stream_url,
            headers=headers,
            stream=True,
        )

        response_headers = {}
        for h in (
            "Content-Type",
            "Content-Length",
            "Content-Range",
            "Accept-Ranges",
        ):
            if h in upstream.headers:
                response_headers[h] = upstream.headers[h]

        return Response(
            upstream.iter_content(chunk_size=64 * 1024),
            status=upstream.status_code,
            headers=response_headers,
        )

    except Exception as e:
        abort(500, str(e))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)