from flask import Flask, render_template, request, jsonify
import yt_dlp
import threading

app = Flask(__name__)

download_progress = {}

def download_video(url, task_id):
    ydl_opts = {
        'format': 'best[height<=720]',  # max 720p to avoid VIP-only
        'outtmpl': '%(title)s.%(ext)s',
        'progress_hooks': [lambda d: progress_hook(d, task_id)],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            download_progress[task_id]['status'] = 'Completed'
    except Exception as e:
        download_progress[task_id]['status'] = f'Error: {str(e)}'

def progress_hook(d, task_id):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%').strip()
        download_progress[task_id]['progress'] = percent
        download_progress[task_id]['status'] = 'Downloading...'
    elif d['status'] == 'finished':
        download_progress[task_id]['progress'] = '100%'
        download_progress[task_id]['status'] = 'Processing...'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    task_id = str(len(download_progress) + 1)
    download_progress[task_id] = {'progress': '0%', 'status': 'Queued'}

    thread = threading.Thread(target=download_video, args=(url, task_id))
    thread.start()

    return jsonify({'task_id': task_id})

@app.route('/progress/<task_id>')
def progress(task_id):
    info = download_progress.get(task_id, None)
    if info:
        return jsonify(info)
    return jsonify({'progress': '0%', 'status': 'Not found'})

if __name__ == '__main__':
    app.run(debug=True)
