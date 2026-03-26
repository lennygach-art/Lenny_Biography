from flask import Flask, request, send_from_directory, jsonify, send_file
import mimetypes
import os
import subprocess
import webbrowser

app = Flask(__name__)
PORT = 5000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/movies-catalog")
def movies_page():
    return send_from_directory(os.path.join(BASE_DIR, "Movies"), "index.html")


@app.route("/Movies/<path:filename>")
def serve_movie_files(filename):
    return send_from_directory(os.path.join(BASE_DIR, "Movies"), filename)


@app.route("/style.css")
def serve_css():
    return send_from_directory(BASE_DIR, "style.css")


@app.route("/open-folder")
def open_folder():
    folder_path = request.args.get("path")
    if folder_path:
        subprocess.Popen(["explorer", folder_path])
        return "OK", 200
    return "Error", 400


@app.route("/list-contents")
def list_contents():
    folder_path = request.args.get("path")
    if not folder_path:
        return jsonify({"error": "Missing path"}), 400

    if not os.path.isdir(folder_path):
        return jsonify({"error": "Folder not found"}), 404

    try:
        files = sorted(os.listdir(folder_path))
        return jsonify({"files": files})
    except OSError as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/stream-video")
def stream_video():
    video_path = request.args.get("path")

    if not video_path or not os.path.exists(video_path):
        print(f"Error: Video not found at {video_path}")
        return "Video not found", 404

    guessed_type, _ = mimetypes.guess_type(video_path)
    return send_file(
        video_path,
        conditional=True,
        mimetype=guessed_type or "application/octet-stream",
    )


if __name__ == "__main__":
    subprocess.run(["python", "Movies/scanner.py"])
    webbrowser.open(f"http://localhost:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
