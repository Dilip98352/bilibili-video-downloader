from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
from threading import Thread

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

def download_video(url, path, result):
    try:
        ydl_opts = {
            'outtmpl': path,
            'format': 'best',
            'noplaylist': True,
            'quiet': True,
            'progress_hooks': [lambda d: result.update(d)]
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        result['error'] = str(e)

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    filename = "video.mp4"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    result = {}
    thread = Thread(target=download_video, args=(url, filepath, result))
    thread.start()
    thread.join()  # Wait for download to finish

    if 'error' in result:
        return jsonify({'error': result['error']}), 500

    return jsonify({'file': f'/download_file/{filename}'})


@app.route('/download_file/<filename>')
def download_file(filename):
    path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File not found", 404


if __name__ == '__main__':
    app.run(debug=True)
