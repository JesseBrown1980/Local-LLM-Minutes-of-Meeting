from mongoengine import Document, StringField, FileField, ReferenceField, DateTimeField
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(Document, UserMixin):
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    email = StringField(required=True, unique=True)
    created_at = DateTimeField(default=datetime.utcnow)

    # Add methods for password hashing
    def set_password(self, password):
        self.password = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    # Required for Flask-Login
    def get_id(self):
        return str(self.id)

class AudioTask(Document):
    task_id = StringField(required=True, unique=True)
    user = ReferenceField(User, required=True)
    audio_file = FileField()
    transcription_text = StringField()
    summary_text = StringField()
    status = StringField(default='PENDING')
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)