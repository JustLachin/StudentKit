"""
Audio Recorder for Voice Notes
"""

import wave
import pyaudio
import threading
from pathlib import Path
from datetime import datetime


class AudioRecorder:
    def __init__(self):
        self.is_recording = False
        self.audio = pyaudio.PyAudio()
        self.frames = []
        self.stream = None
        self.record_thread = None
        
        # Audio settings
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.chunk = 1024
    
    def start_recording(self):
        """Start recording audio"""
        if self.is_recording:
            return False
        
        self.is_recording = True
        self.frames = []
        
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        self.record_thread = threading.Thread(target=self._record)
        self.record_thread.start()
        return True
    
    def _record(self):
        """Recording thread function"""
        while self.is_recording:
            try:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
            except Exception:
                break
    
    def stop_recording(self, output_path=None):
        """Stop recording and save to file"""
        if not self.is_recording:
            return None
        
        self.is_recording = False
        
        if self.record_thread:
            self.record_thread.join()
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        # Generate filename if not provided
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"recordings/note_audio_{timestamp}.wav"
        
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save the recording
        with wave.open(output_path, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
        
        return output_path
    
    def cancel_recording(self):
        """Cancel recording without saving"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        if self.record_thread:
            self.record_thread.join()
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
    
    def cleanup(self):
        """Clean up audio resources"""
        if self.is_recording:
            self.cancel_recording()
        self.audio.terminate()
