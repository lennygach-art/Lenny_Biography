from flask import Flask, request, send_from_directory, jsonify
import os, subprocess, webbrowser

app = Flask(__name__)
PORT = 5000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Route for the Master Portal (The landing page)
@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')

# 2. Route for the Movie Catalog page
@app.route('/movies-catalog')
def movies_page():
    return send_from_directory(os.path.join(BASE_DIR, 'Movies'), 'index.html')

# 3. Route to serve the JSON and CSS correctly
@app.route('/Movies/<path:filename>')
def serve_movie_files(filename):
    # This ensures that even if you are on the /movies-catalog page, 
    # it can still find 'movies.json' inside the Movies folder.
    return send_from_directory(os.path.join(BASE_DIR, 'Movies'), filename)

@app.route('/style.css')
def serve_css():
    return send_from_directory(BASE_DIR, 'style.css')

# 4. The "Bridge" for opening folders
@app.route('/open-folder')
def open_folder():
    folder_path = request.args.get('path')
    if folder_path:
        subprocess.Popen(['explorer', folder_path])
        return "OK", 200
    return "Error", 400

@app.route('/list-contents')
def list_contents():
    folder_path = request.args.get('path')
    if not folder_path:
        return jsonify({"error": "Missing path"}), 400

    if not os.path.isdir(folder_path):
        return jsonify({"error": "Folder not found"}), 404

    try:
        files = sorted(os.listdir(folder_path))
        return jsonify({"files": files})
    except OSError as exc:
        return jsonify({"error": str(exc)}), 500

if __name__ == "__main__":
    # Run the scanner inside the Movies subfolder
    subprocess.run(["python", "Movies/scanner.py"])
    webbrowser.open(f"http://localhost:{PORT}")
    app.run(port=PORT, debug=False)
