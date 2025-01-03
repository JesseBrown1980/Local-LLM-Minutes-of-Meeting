import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import logging
from global_variables import SPEECH_MODEL_PATH

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_speech_transcription(audio_path):
    try:
        logger.debug("Initializing device and data types...")
        runnning_device = "cuda:0" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        logger.debug(f"Running device: {running_device}, Torch dtype: {torch_dtype}")

        logger.debug("Loading audio transcriber model...")
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            SPEECH_MODEL_PATH, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
        )
        model.to(runnning_device)
        logger.debug("Model loaded and moved to device.")

        logger.debug("Loading processor...")
        processor = AutoProcessor.from_pretrained(SPEECH_MODEL_PATH)
        logger.debug("Processor loaded.")

        logger.debug("Setting up speech pipeline...")
        speech_pipeline = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            max_new_tokens=128,
            chunk_length_s=20,
            batch_size=8,
            torch_dtype=torch_dtype,
            device=runnning_device,
        )
        
        logger.info("Starting transcription...")
        result = speech_pipeline(audio_path, return_timestamps=False)
        logger.info("Finished transcribing.")
        print(f"{result}")
        del speech_pipeline, model, processor
        torch.cuda.empty_cache()
        print(f"Transcription: {result['text']}")
        return result['text']
    except Exception as e:
        logger.exception("Error during speech transcription")
        raise