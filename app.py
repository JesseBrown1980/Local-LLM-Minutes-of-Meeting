import os
from flask import Flask, render_template, request, redirect, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from mongoengine import connect
from models import User, AudioTask
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
from random_username.generate import generate_username

from celery import Celery
import logging
from utils import convert_to_wav

from global_variables import BASE_DATA_UPLOADED_RECORDINGS_DIRECTORY

logging.basicConfig(level=logging.DEBUG) #logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Reduce MongoDB logging
logging.getLogger('pymongo').setLevel(logging.WARNING)
logging.getLogger('mongoengine').setLevel(logging.WARNING)

# Connect to MongoDB
try:
    connect('Local-Minutes-Of-Meetings', host='mongodb://localhost:27017')
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
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
# Configure CORS
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, resources={
    r"/api/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True,
        "max_age": 120
    }
})
# Initialize JWT
app.config['JWT_SECRET_KEY'] = 'udgqiohqw9d7102e9o`==2e8djdpqiwdhqp;3534qwc08e2' 

# Set secret key for sessions
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "iuhys*IQ)XP546513cCOISXshcosxaoschapsa")

jwt = JWTManager(app)
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

@app.route('/api/tasks/upload', methods=['POST'])
@jwt_required()
def upload_file():
    try:
        current_user_id = get_jwt_identity() 
        logger.info(f"Current user {current_user_id}")
        user = User.objects(id=current_user_id).first()
    
        if not user:
            return jsonify({'error': 'User not found'}), 404
    
        logger.debug("Starting file upload process...")
        check_and_install_ffmpeg()

        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            return redirect(request.url)
        
        filename = secure_filename(file.filename)
        
        # Create temporary file for processing
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(temp_path)
        
        # Convert to WAV for processing
        audio_path = convert_to_wav(temp_path)
        
        # Queue Celery task
        task = process_audio.delay(audio_path, filename, str(current_user.id))
        
        # Create AudioTask entry
        audio_task = AudioTask(
            task_id=task.id,
            user=current_user.id,
            status='PENDING'
        )
        audio_task.save()
        
        # Clean up temporary files
        os.remove(temp_path)
        if temp_path != audio_path:
            os.remove(audio_path)
            
        return jsonify({'task_id': task.id})
    except Exception as e:
        logger.exception("Error in upload_file")
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/auth/register', methods=['POST'])
def register():
    # Get and validate request data
    data = request.get_json()
    if not data:
        logger.error("No JSON data received")
        return jsonify({'error': 'No data provided'}), 400
    
     # Log registration attempt
    logger.info(f"Registration attempt for email: {data.get('email')}")

    # Check required fields
    if not all(k in data for k in ['email', 'password']):
        logger.error("Missing required fields")
        return jsonify({'error': 'Email and password are required'}), 400

    # Check if user already exists   
    if User.objects(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    username = generate_username()[0]
    try:
        # Create new user with hashed password
        user = User(
            username=username,
            email=data['email'],
        )
        user.set_password(data['password'])
        user.save()
        print("USER", user)
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'token': access_token,
            'user': {
                'id': str(user.id),
                'email': user.email
            }
        }), 201
    except Exception as e:
         # Log the full error
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Registration failed. Please try again.'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        # Get and validate request data
        data = request.get_json()
        if not data:
            logger.error("No JSON data received")
            return jsonify({'error': 'No data provided'}), 400
    
        # Check required fields
        if not all(k in data for k in ['email', 'password']):
            logger.error("Missing required fields")
            return jsonify({'error': 'Email and password are required'}), 400
    
        user = User.objects(email=data['email']).first()
    
        if user and user.check_password(data['password']):
            # Create access token
            access_token = create_access_token(identity=str(user.id))
            
            # Login user for session
            login_user(user)
            
            return jsonify({
                'token': access_token,
                'user': {
                    'id': str(user.id),
                    'email': user.email
                }
            })
    
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500


if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True)

