import whisper

# Load once for performance
model = whisper.load_model("base")

def transcribe_audio(audio_path):
    result = model.transcribe(audio_path, task="translate")
    return result["text"]
