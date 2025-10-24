from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import subprocess

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download_video():
    url = request.form.get("url")
    if not url:
        return jsonify({"status": "error", "message": "Please provide a video URL."})

    filename = "%(title)s.%(ext)s"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    cmd = [
        "yt-dlp",
        url,
        "-f", "bv*+ba/best",
        "--merge-output-format", "mp4",
        "--newline",
        "-o", filepath
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    logs = []
    for line in process.stdout:
        logs.append(line.strip())

    process.wait()
    if process.returncode != 0:
        return jsonify({"status": "error", "message": "Download failed", "logs": logs})

    # Get the actual downloaded file
    downloaded_files = os.listdir(DOWNLOAD_FOLDER)
    latest_file = max([os.path.join(DOWNLOAD_FOLDER, f) for f in downloaded_files], key=os.path.getctime)

    return jsonify({"status": "success", "file": latest_file, "logs": logs})

@app.route("/downloads/<filename>")
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
