#!/usr/bin/env python3
"""
Solve audio CAPTCHAs using speech recognition.
Supports Whisper (local) and Google Speech API.
"""

import argparse
import sys
import os
import tempfile
import requests
from pathlib import Path

try:
    import speech_recognition as sr
except ImportError:
    print("Install: pip install SpeechRecognition")
    sys.exit(1)


def download_audio(url, output_path=None):
    """Download audio file from URL."""
    if output_path is None:
        output_path = tempfile.mktemp(suffix=".mp3")
    
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    
    with open(output_path, "wb") as f:
        f.write(response.content)
    
    return output_path


def convert_to_wav(audio_path):
    """Convert audio to WAV format if needed."""
    if audio_path.endswith(".wav"):
        return audio_path
    
    try:
        from pydub import AudioSegment
    except ImportError:
        print("Install pydub for audio conversion: pip install pydub")
        print("Also requires ffmpeg: sudo apt-get install ffmpeg")
        return audio_path
    
    wav_path = tempfile.mktemp(suffix=".wav")
    
    audio = AudioSegment.from_file(audio_path)
    audio.export(wav_path, format="wav")
    
    return wav_path


def solve_audio_captcha(audio_path, method="google", from_url=False, language="en-US"):
    """
    Solve audio CAPTCHA using speech recognition.
    
    Args:
        audio_path: Path to audio file or URL
        method: "google" (free, online) or "whisper" (local, more accurate)
        from_url: If True, download from URL first
        language: Language code (e.g., "en-US", "en-GB")
    
    Returns:
        dict: {"text": str, "success": bool, "method": str}
    """
    try:
        # Download if URL
        if from_url:
            audio_path = download_audio(audio_path)
        
        # Convert to WAV
        wav_path = convert_to_wav(audio_path)
        
        recognizer = sr.Recognizer()
        
        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)
        
        # Transcribe
        if method == "whisper":
            try:
                import whisper
                # Save audio temporarily for whisper
                temp_wav = tempfile.mktemp(suffix=".wav")
                with open(wav_path, "rb") as f:
                    with open(temp_wav, "wb") as wf:
                        wf.write(f.read())
                
                model = whisper.load_model("base")
                result = model.transcribe(temp_wav)
                text = result["text"].strip()
                
                # Cleanup
                if temp_wav != wav_path:
                    os.remove(temp_wav)
                
            except ImportError:
                print("Whisper not available, falling back to Google")
                text = recognizer.recognize_google(audio, language=language)
        else:
            # Google Speech Recognition (free tier)
            text = recognizer.recognize_google(audio, language=language)
        
        # Clean up temp files
        if from_url and os.path.exists(audio_path):
            os.remove(audio_path)
        
        return {
            "text": text,
            "success": True,
            "method": method
        }
    
    except sr.UnknownValueError:
        return {
            "text": "",
            "success": False,
            "error": "Could not understand audio"
        }
    except sr.RequestError as e:
        return {
            "text": "",
            "success": False,
            "error": f"Service error: {e}"
        }
    except Exception as e:
        return {
            "text": "",
            "success": False,
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Solve audio CAPTCHA")
    parser.add_argument("audio", help="Path to audio file or URL")
    parser.add_argument("--url", action="store_true", help="Download from URL")
    parser.add_argument("--method", choices=["google", "whisper"], 
                       default="google", help="Recognition method")
    parser.add_argument("--lang", default="en-US", help="Language code")
    
    args = parser.parse_args()
    
    result = solve_audio_captcha(
        args.audio,
        method=args.method,
        from_url=args.url,
        language=args.lang
    )
    
    if result["success"]:
        print(f"CAPTCHA text: {result['text']}")
        print(f"Method: {result['method']}")
    else:
        print(f"Failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
