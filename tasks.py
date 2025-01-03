from celery import current_app as celery
from speech import get_speech_transcription
from summary import get_minutes_of_meeting
import time

print("CELERY", celery.conf.broker_url)

@celery.task(bind=True)
def process_audio(self, audio_path, filename):
    try:
        self.update_state(state='STARTED', meta={'info': 'Processing Audio File.', 'audio_path': audio_path, 'audio_filename': filename})
        time.sleep(10)
        
        print("Starting transcription...")
        text = get_speech_transcription(audio_path)
        print("Transcription complete.")  
        self.update_state(state='PROGRESS', meta={'info': 'Text extracted, Summarizing now.', 'audio_path': audio_path, 'audio_filename': filename})
        time.sleep(10)
        
        minutes_of_meeting = get_minutes_of_meeting(text)
        
        #output minutes of meeting to an xlsx file
        # output_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename.split('.')[0] + '.xlsx')
        # minutes_of_meeting.to_excel(output_filename, index=False)
        print(f"Minutes of Meeting: {minutes_of_meeting}")
        print(f"Audio Path: {audio_path}")
        print(f"Audio Filename: {filename}")
        self.update_state(state='SUCCESS', meta={'info': 'Summary Ready.', 'summary': minutes_of_meeting, 'audio_path': audio_path, 'audio_filename': filename})
        time.sleep(10)
        return {'summary': minutes_of_meeting, 'audio_path': audio_path, 'audio_filename': filename}
    except Exception as e:
        print(f"Error in process_audio: {e}")
        self.update_state(state='FAILURE', meta={'info': str(e)})
        raise
