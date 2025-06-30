from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import os
import re

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

progress_data = {"progress": 0.0}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/progress")
def progress():
    return jsonify(progress_data)

# app.py (relevant section inside download route)
@app.route("/download", methods=["POST"])
def download():
    url = request.form["url"]
    format_type = request.form["format"]

    try:
        ydl_opts = {
            'quiet': True,
            'format': 'bestaudio/best' if format_type == 'mp3' else 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4' if format_type == 'mp4' else None,
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title).100s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }] if format_type == 'mp3' else [],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = re.sub(r'[\\/:*?"<>|]', '', info.get('title', 'download')).strip()
            filename = f"{title}.{format_type}"
            return jsonify({"status": "success", "filename": filename})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/get-file")
def get_file():
    filename = request.args.get("filename")
    path = os.path.join(DOWNLOAD_FOLDER, filename)
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="192.168.105.90", port=5000, debug=True)

