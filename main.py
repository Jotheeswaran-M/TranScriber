import pyaudio
import wave
import os
import time
import whisper
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
KEEP_AUDIO = True  # Keep audio files for debugging
CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
recording = False
audio_frames = []

def list_audio_devices():
    p = pyaudio.PyAudio()
    devices = []
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0:
            devices.append((i, dev['name']))
    p.terminate()
    return devices

def select_audio_device():
    devices = list_audio_devices()
    if not devices:
        logger.error("No input devices found. Please check microphone or install VB-Audio Virtual Cable.")
        return None
    logger.info("Available audio devices:")
    for idx, name in devices:
        logger.info(f"  {idx}: {name}")
    # Default to first device; modify to use VB-Audio if needed
    return devices[0][0]

def record_audio(filename, device_index=None):
    global recording, audio_frames
    p = pyaudio.PyAudio()
    
    if device_index is None:
        device_index = select_audio_device()
        if device_index is None:
            p.terminate()
            return None
    
    try:
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=CHUNK
        )
        logger.info("Recording... Press Enter to stop.")
        audio_frames = []
        while recording:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                audio_frames.append(data)
            except Exception as e:
                logger.error(f"Error reading audio stream: {e}")
                break
        
        # Save audio to file
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        if not audio_frames:
            logger.error("No audio data recorded. Check input device.")
            return None
        
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(audio_frames))
        wf.close()
        
        logger.info(f"Audio saved to: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Recording failed: {e}")
        p.terminate()
        return None

def transcribe_audio(audio_path):
    try:
        # Try Whisper small, fall back to tiny
        try:
            model = whisper.load_model("small")
            logger.info("Using Whisper small model")
        except RuntimeError:
            logger.warning("Failed to load small model, falling back to tiny")
            model = whisper.load_model("tiny")
        
        result = model.transcribe(audio_path, fp16=False)
        transcription = result["text"].strip()
        
        if not transcription:
            logger.warning("Transcription is empty. Audio may be silent or too noisy.")
        
        # Save transcription
        transcript_path = audio_path.replace(".wav", ".txt")
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(transcription)
        
        if not KEEP_AUDIO:
            os.remove(audio_path)
            logger.info(f"Deleted audio file: {audio_path}")
        
        return transcription, transcript_path
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return None, None

def main():
    global recording, audio_frames
    recording = True
    
    # Select audio device
    device_index = select_audio_device()
    if device_index is None:
        logger.error("Exiting due to no input device.")
        return
    
    # Generate unique filename
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    audio_filename = os.path.join(DATA_DIR, f"meeting_{timestamp}.wav")
    
    # Record audio
    audio_path = None
    try:
        audio_path = record_audio(audio_filename, device_index)
        if not audio_path:
            logger.error("Recording failed. Check microphone or audio settings.")
            return
    except KeyboardInterrupt:
        recording = False
        logger.info("Recording stopped by user.")
        # Ensure audio is saved even on interrupt
        if audio_frames:
            try:
                wf = wave.open(audio_filename, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(audio_frames))
                wf.close()
                logger.info(f"Audio saved to: {audio_filename}")
                audio_path = audio_filename
            except Exception as e:
                logger.error(f"Failed to save audio on interrupt: {e}")
    
    # Transcribe audio
    if audio_path and os.path.exists(audio_path):
        logger.info("Transcribing...")
        transcription, transcript_path = transcribe_audio(audio_path)
        if transcription:
            logger.info(f"Transcription saved to: {transcript_path}")
            logger.info(f"Transcription: {transcription[:200]}...")
        else:
            logger.error("Transcription failed. Check audio file or Whisper model.")
    else:
        logger.error("No audio file available for transcription.")
    
    # Clear memory
    audio_frames = []

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        recording = False
        logger.info("Stopped by user.")