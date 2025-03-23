#pip install azure-cognitiveservices-speech
#pip install ffmpeg-python
#pip install tk
import azure.cognitiveservices.speech as speechsdk
import ffmpeg
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading

# Replace with your Azure Speech API Key and Region
SPEECH_KEY = "DaWaZpALfWnwwPFDe2sGhd4Kon8NztpJQ8bvdbHM5fJRJzemH5dbJQQJ99BCACYeBjFXJ3w3AAAYACOGiDi5"
SPEECH_REGION = "eastus"

def extract_audio(file_path):
    """Extracts audio from video or audio file using FFmpeg."""
    audio_path = "temp_audio.wav"
    
    # Check if the input is video or audio file, and adjust extraction accordingly
    if file_path.endswith(('.mp4', '.avi', '.mov', '.mkv')):  # For video files
        ffmpeg.input(file_path).output(audio_path, format="wav", acodec="pcm_s16le", ar="16000", ac="1").run(overwrite_output=True)
    elif file_path.endswith(('.mp3', '.wav')):  # For audio files
        # Directly convert audio files to WAV
        ffmpeg.input(file_path).output(audio_path, format="wav", acodec="pcm_s16le", ar="16000", ac="1").run(overwrite_output=True)
    
    return audio_path

def transcribe_audio(audio_path, callback):
    """Transcribes audio using Azure Speech SDK with language detection."""
    # Set up speech configuration
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    
    # Enable language auto-detection
    auto_detect_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["en-US", "es-ES"])

    # Set up audio configuration for the file
    audio_config = speechsdk.AudioConfig(filename=audio_path)
    
    # Create a recognizer with language detection enabled
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config, auto_detect_source_language_config=auto_detect_config)

    transcription = []

    # This function gets called when a new part of speech is recognized
    def handle_final_result(evt):
        print(f"Recognized: {evt.result.text}")  # Debugging: print the recognized text
        transcription.append(evt.result.text)

    # This function gets called when the recognition session completes
    def on_completed(evt):
        recognizer.stop_continuous_recognition()
        full_transcript = " ".join(transcription)
        print(f"Full Transcription: {full_transcript}")  # Debugging: print the full result
        callback(full_transcript)
        os.remove(audio_path)  # Cleanup temp file

    # Set up events for recognition results and completion
    recognizer.recognized.connect(handle_final_result)
    recognizer.session_stopped.connect(on_completed)

    # Start the recognition
    recognizer.start_continuous_recognition()

def transcribe_video_or_audio():
    """Allows user to select a video/audio file and transcribes its full audio asynchronously."""
    file_path = filedialog.askopenfilename(title="Select Video/Audio File", filetypes=[("All Files", "*.*"), ("Video Files", "*.mp4;*.avi;*.mov;*.mkv"), ("Audio Files", "*.mp3;*.wav")])
    if not file_path:
        return

    audio_path = extract_audio(file_path)
    print(f"Extracted Audio Path: {audio_path}")  # Debugging: check audio path

    def display_transcription(result):
        messagebox.showinfo("Transcription", f"File Transcription:\n{result}")

    # Run transcription in a separate thread to prevent UI freezing
    threading.Thread(target=transcribe_audio, args=(audio_path, display_transcription), daemon=True).start()
    messagebox.showinfo("Processing", "Transcribing audio... Please wait.")

# Create UI
root = tk.Tk()
root.title("Speech-to-Text")

tk.Label(root, text="Choose an option:", font=("Arial", 14)).pack(pady=10)
tk.Button(root, text="📂 Upload Video/Audio for Full Transcription", font=("Arial", 12), command=transcribe_video_or_audio).pack(pady=10)

root.mainloop()