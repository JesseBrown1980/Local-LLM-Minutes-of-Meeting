from mongoengine import Document, StringField, FileField, ReferenceField, DateTimeField
from datetime import datetime

class User(Document):
    username = StringField(required=True, unique=True)
    password = StringField(required=True)  # Should be hashed
    email = StringField(required=True, unique=True)
    created_at = DateTimeField(default=datetime.utcnow)

class AudioTask(Document):
    task_id = StringField(required=True, unique=True)
    user = ReferenceField(User, required=True)
    audio_file = FileField()
    transcription_text = StringField()
    summary_text = StringField()
    status = StringField(default='PENDING')
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)