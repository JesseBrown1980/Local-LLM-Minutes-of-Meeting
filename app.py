import os
from flask import Flask, render_template, request, redirect, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from mongoengine import connect
from models import User, AudioTask
import gridfs
import io

from celery import Celery
import logging
from utils import convert_to_wav

from global_variables import BASE_DATA_UPLOADED_RECORDINGS_DIRECTORY

# Connect to MongoDB
connect('meeting_minutes_db', host='mongodb://localhost:27017')

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def make_celery(app):
    broker_url = "amqp://Fairweather:test1234@127.0.0.1:5672/cherry_broker"
    celery = Celery(
        app.import_name,
        backend="redis://localhost:6379/0",
        broker=broker_url
    )
    celery.conf.update(app.config)
    celery.conf.update(
        broker_url=broker_url,
        result_backend='redis://localhost:6379/0',  # New style key
        broker_connection_retry=True,
        broker_connection_retry_on_startup=True,
        worker_hijack_root_logger=False,
        worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    )

    logger = logging.getLogger('celery')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s: %(levelname)s/%(processName)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    return celery

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = BASE_DATA_UPLOADED_RECORDINGS_DIRECTORY
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'wav', 'mp3'}
CORS(app)
# Update app config with broker URL
app.config.update(
    broker_url='amqp://Fairweather:test1234@127.0.0.1:5672/cherry_broker',  # New style key
    result_backend='redis://localhost:6379/0'  # New style key
)
celery = make_celery(app)
from tasks import process_audio

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def check_and_install_ffmpeg():
    """
    Function to check if ffmpeg is installed, and if not to install it as required by Ubuntu 22.04
    """
    try:
        # Check if ffmpeg is available
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("FFmpeg is already installed.")
    except FileNotFoundError:
        print("FFmpeg not found. Installing...")
        # Install FFmpeg on Ubuntu using apt
        subprocess.run(['sudo', 'apt', 'update'], check=True)
        subprocess.run(['sudo', 'apt', 'install', '-y', 'ffmpeg'], check=True)
        print("FFmpeg installation completed.")
        
        
@app.route('/check_task/<task_id>')
def check_task(task_id):
    task = process_audio.AsyncResult(task_id)
    response = {
        'status': task.state,
        'info': task.info.get('info', 'COMPLETED'),
        'filename': task.info.get('audio_filename', '')
    }
    return jsonify(response)

@app.route('/audio/<filename>')
def send_audio(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/results/<task_id>')
def results(task_id):
    task = process_audio.AsyncResult(task_id)
    if task.state == 'SUCCESS':
        result = task.result
        file_type = 'video' if result['audio_filename'].endswith(('.mp4', '.mov', '.avi')) else 'audio'
        return render_template('result.html', minutes_of_meeting=result['summary'], recording_status = "Completed", recording_filename = result['audio_filename'], audio_path=os.path.join('/audio', result['audio_filename']), file_type=file_type)
    return render_template('result.html', minutes_of_meeting=result['summary'], recording_status = "Unknown", recording_filename = result['audio_filename'], audio_path=os.path.join('/audio', "#"))

@app.route('/', methods=['GET'])
def index():
    print("INDEX route accessed")
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error rendering template: {e}")
        return "Error rendering template", 500

@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first()
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        logger.debug("Starting file upload process...")
        # Check and install ffmpeg if needed
        check_and_install_ffmpeg()

        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        logger.debug(f"Received file: {file.filename}")
        if file.filename == '' or not allowed_file(file.filename):
            return redirect(request.url)
        
        filename = secure_filename(file.filename)
        # Secure the filename and create upload folder if it doesn't exist
        filename = secure_filename(file.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        # Save file to the designated folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        logger.debug(f"File saved to: {file_path}")
        audio_path = convert_to_wav(file_path)
        logger.debug(f"Converted to WAV: {audio_path}")
        
        logger.debug("Attempting to queue Celery task...")
        task = process_audio.delay(audio_path, filename)
        logger.debug(f"Task queued successfully with ID: {task.id}")
        
        return jsonify({'task_id': task.id})
    except Exception as e:
        logger.exception("Error in upload_file")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True)

