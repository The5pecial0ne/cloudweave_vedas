from time import sleep
from flask import Flask, send_from_directory, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
def index():
    """Serve the HTML page with the video player."""
    return render_template('index.html')

@app.route('/video/<string:video_dir>/<string:file_name>')
def stream(video_dir: str, file_name: str):
    if file_name == 'output.m3u8':
        sleep(5)
    base_dir: str = './videos/'
    return send_from_directory(base_dir + video_dir, file_name)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
