"""
Speech Recognition and Text-to-Speech Module for Embodied Agent

This module provides functions for recording audio, recognizing speech from audio files,
playing audio files, and converting text to speech.

"""

import os
import wave
import time
import tempfile
import numpy as np
from typing import Optional, Tuple
import subprocess
from config import AUDIO_CONFIG, PATHS

# Try to import optional dependencies with graceful fallbacks
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    print("PyAudio not available, speech recording will be simulated")
    PYAUDIO_AVAILABLE = False

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    print("Speech Recognition not available, using text placeholders")
    SR_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    print("gTTS not available, text-to-speech will produce placeholder files")
    GTTS_AVAILABLE = False

# Constants
TEMP_DIR = PATHS.get("temp_dir", "temp/")
AUDIO_DIR = PATHS.get("audio_dir", "assets/audio/")

# Ensure temporary directory exists
os.makedirs(TEMP_DIR, exist_ok=True)

def record(duration: int = 5, output_file: str = "temp/speech.wav") -> str:
    """
    Records audio from the microphone for a specified duration.
    
    Args:
        duration: Recording duration in seconds
        output_file: Path to save the recorded audio file
        
    Returns:
        Path to the recorded audio file
    """
    print(f"Recording for {duration} seconds...")
    
    if not PYAUDIO_AVAILABLE:
        print("Simulating audio recording (PyAudio not installed)")
        time.sleep(duration)  # Simulate recording time
        # Copy sample file if available, otherwise create empty file
        sample_path = os.path.join(AUDIO_DIR, "sample_speech.wav")
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as src, open(output_file, "wb") as dst:
                dst.write(src.read())
        else:
            # Create an empty WAV file
            with wave.open(output_file, "wb") as wf:
                wf.setnchannels(AUDIO_CONFIG.get("channels", 1))
                wf.setsampwidth(2)  # 2 bytes = 16 bits
                wf.setframerate(AUDIO_CONFIG.get("sample_rate", 16000))
                wf.writeframes(b"")
        return output_file
    
    # Real recording with PyAudio
    p = pyaudio.PyAudio()
    
    # Get configuration from config.py
    channels = AUDIO_CONFIG.get("channels", 1)
    sample_rate = AUDIO_CONFIG.get("sample_rate", 16000)
    chunk_size = AUDIO_CONFIG.get("chunk_size", 1024)
    format_val = pyaudio.paInt16
    
    # Open a recording stream
    stream = p.open(format=format_val,
                   channels=channels,
                   rate=sample_rate,
                   input=True,
                   frames_per_buffer=chunk_size)
    
    # Record audio
    frames = []
    for i in range(0, int(sample_rate / chunk_size * duration)):
        data = stream.read(chunk_size)
        frames.append(data)
    
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Save the recorded audio to a WAV file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    wf = wave.open(output_file, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format_val))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    print(f"Recording saved to {output_file}")
    return output_file


def speech_recognition(audio_file: str = "temp/speech.wav") -> str:
    """
    Performs speech recognition on an audio file.
    
    Args:
        audio_file: Path to the audio file to recognize
        
    Returns:
        Recognized text from the audio file
    """
    print("Recognizing speech...")
    
    if not SR_AVAILABLE or not os.path.exists(audio_file):
        print("Speech recognition not available or file doesn't exist")
        return "This is simulated speech recognition text."
    
    # Initialize the recognizer
    recognizer = sr.Recognizer()
    
    # Load the audio file
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
    
    # Try to recognize speech using Google Speech Recognition
    try:
        text = recognizer.recognize_google(audio_data)
        print(f"Recognized: {text}")
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return "I couldn't understand what was said. Please try again."
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return "Sorry, the speech recognition service is unavailable at the moment."


def play_wav(file_path: str) -> None:
    """
    Plays a WAV audio file.
    
    Args:
        file_path: Path to the WAV file to play
    """
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Audio file not found: {file_path}")
        return
    
    print(f"Playing audio: {file_path}")
    
    # Try to use different methods to play audio based on platform
    try:
        # First try platform-specific commands
        if os.name == 'posix':  # Linux/Mac
            os.system(f"aplay {file_path}")
        elif os.name == 'nt':  # Windows
            os.system(f"start /min powershell -c (New-Object Media.SoundPlayer '{file_path}').PlaySync();")
        else:
            if PYAUDIO_AVAILABLE:
                # Fallback to PyAudio if available
                wf = wave.open(file_path, 'rb')
                p = pyaudio.PyAudio()
                
                # Open a stream
                stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                               channels=wf.getnchannels(),
                               rate=wf.getframerate(),
                               output=True)
                
                # Read and play chunks of data
                chunk_size = AUDIO_CONFIG.get("chunk_size", 1024)
                data = wf.readframes(chunk_size)
                while data:
                    stream.write(data)
                    data = wf.readframes(chunk_size)
                
                # Clean up
                stream.stop_stream()
                stream.close()
                p.terminate()
            else:
                print("No suitable audio playback method available")
    except Exception as e:
        print(f"Error playing audio: {e}")


def tts(text: str, output_file: str = "temp/tts.wav", lang: str = "en") -> str:
    """
    Converts text to speech and saves it as an audio file.
    
    Args:
        text: Text to convert to speech
        output_file: Path to save the audio file
        lang: Language code for the speech
        
    Returns:
        Path to the generated audio file
    """
    print(f"Converting text to speech: '{text}'")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    if not GTTS_AVAILABLE:
        print("gTTS not available, creating placeholder file")
        # Create a simple sine wave as placeholder audio
        try:
            sample_rate = AUDIO_CONFIG.get("sample_rate", 16000)
            duration = min(2 + len(text) * 0.07, 10)  # Rough estimate of speech duration
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            note = np.sin(2 * np.pi * 440 * t) * 0.3  # 440 Hz sine wave
            audio = note * (2**15 - 1) / np.max(np.abs(note))
            audio = audio.astype(np.int16)
            
            with wave.open(output_file, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio.tobytes())
        except Exception as e:
            print(f"Error creating placeholder audio: {e}")
            # Create empty file if all else fails
            with open(output_file, 'wb') as f:
                pass
        return output_file
    
    try:
        # Create gTTS object
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # Save to file
        tts.save(output_file)
        return output_file
    except Exception as e:
        print(f"Error in text-to-speech conversion: {e}")
        return ""
