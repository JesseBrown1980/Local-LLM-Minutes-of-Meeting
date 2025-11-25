import os
from celery import current_app as celery

from models import AudioTask
from speech import get_speech_transcription
from summary import get_minutes_of_meeting

@celery.task(bind=True)
def process_audio(self, audio_path, filename, user_id):
    audio_task = None
    try:
        task_id = self.request.id
        audio_task = AudioTask.objects(task_id=task_id).first()
        
        self.update_state(state='STARTED', meta={'info': 'Processing Audio File.'})
        
        # Store audio file in MongoDB
        with open(audio_path, 'rb') as audio_file:
            audio_task.audio_file.put(audio_file, filename=filename)
        audio_task.status = 'PROCESSING'
        audio_task.save()
        
        # Transcribe audio
        text = get_speech_transcription(audio_path)
        audio_task.transcription_text = text
        audio_task.save()
        
        self.update_state(state='PROGRESS', meta={'info': 'Text extracted, Summarizing now.'})
        
        # Generate summary
        minutes_of_meeting = get_minutes_of_meeting(text)
        audio_task.summary_text = minutes_of_meeting
        audio_task.status = 'COMPLETED'
        audio_task.save()
        
        # Clean up local file
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        self.update_state(state='SUCCESS', meta={
            'info': 'Summary Ready.',
            'summary': minutes_of_meeting,
            'task_id': task_id
        })
        
        return {
            'summary': minutes_of_meeting,
            'task_id': task_id
        }
    except Exception as e:
        if audio_task:
            audio_task.status = 'FAILED'
            audio_task.save()
        print(f"Error in process_audio: {e}")
        self.update_state(state='FAILURE', meta={'info': str(e)})
        raise
