"""
Sound Manager for Student Study Kit
Manages all sound effects from SND01-sine-sound-pack
"""

import os
from pathlib import Path
from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput


class SoundManager:
    def __init__(self, sound_pack_path="SND01-sine-sound-pack"):
        self.sound_pack_path = Path(sound_pack_path)
        self.players = {}
        self.loop_players = {}
        self.is_muted = False
        self.volume = 0.7
        
        # Sound file mappings
        self.sounds = {
            'button': 'button.wav',
            'caution': 'caution.wav',
            'celebration': 'celebration.wav',
            'disabled': 'disabled.wav',
            'notification': 'notification.wav',
            'progress_loop': 'progress_loop.wav',
            'ringtone_loop': 'ringtone_loop.wav',
            'select': 'select.wav',
            'swipe': 'swipe.wav',
            'tap': 'tap_01.wav',
            'toggle_on': 'toggle_on.wav',
            'toggle_off': 'toggle_off.wav',
            'transition_up': 'transition_up.wav',
            'transition_down': 'transition_down.wav',
            'type': 'type_01.wav'
        }
        
        # Pre-load all sounds
        self._load_sounds()
    
    def _load_sounds(self):
        """Pre-load all sound effects"""
        for sound_name, filename in self.sounds.items():
            sound_path = self.sound_pack_path / filename
            if sound_path.exists():
                # For one-shot sounds
                if 'loop' not in sound_name:
                    player = QMediaPlayer()
                    audio_output = QAudioOutput()
                    player.setAudioOutput(audio_output)
                    player.setSource(QUrl.fromLocalFile(str(sound_path.absolute())))
                    audio_output.setVolume(self.volume)
                    self.players[sound_name] = (player, audio_output)
                else:
                    # For loop sounds
                    player = QMediaPlayer()
                    audio_output = QAudioOutput()
                    player.setAudioOutput(audio_output)
                    player.setSource(QUrl.fromLocalFile(str(sound_path.absolute())))
                    player.setLoops(QMediaPlayer.Loops.Infinite)
                    audio_output.setVolume(self.volume)
                    self.loop_players[sound_name] = (player, audio_output)
    
    def play(self, sound_name):
        """Play a one-shot sound effect"""
        if self.is_muted:
            return
        
        if sound_name in self.players:
            player, _ = self.players[sound_name]
            player.setPosition(0)
            player.play()
    
    def start_loop(self, sound_name):
        """Start a looping sound (e.g., ringtone for exams)"""
        if self.is_muted:
            return
        
        if sound_name in self.loop_players:
            player, _ = self.loop_players[sound_name]
            player.setPosition(0)
            player.play()
    
    def stop_loop(self, sound_name):
        """Stop a looping sound"""
        if sound_name in self.loop_players:
            player, _ = self.loop_players[sound_name]
            player.stop()
    
    def stop_all_loops(self):
        """Stop all looping sounds"""
        for sound_name in self.loop_players:
            self.stop_loop(sound_name)
    
    def set_muted(self, muted):
        """Mute/unmute all sounds"""
        self.is_muted = muted
        if muted:
            self.stop_all_loops()
    
    def set_volume(self, volume):
        """Set volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        for player, audio_output in self.players.values():
            audio_output.setVolume(self.volume)
        for player, audio_output in self.loop_players.values():
            audio_output.setVolume(self.volume)
    
    # Convenience methods for specific events
    def play_button(self):
        self.play('button')
    
    def play_tap(self):
        self.play('tap')
    
    def play_select(self):
        self.play('select')
    
    def play_swipe(self):
        self.play('swipe')
    
    def play_toggle_on(self):
        self.play('toggle_on')
    
    def play_toggle_off(self):
        self.play('toggle_off')
    
    def play_notification(self):
        self.play('notification')
    
    def play_caution(self):
        self.play('caution')
    
    def play_celebration(self):
        self.play('celebration')
    
    def play_type(self):
        self.play('type')
    
    def play_transition_up(self):
        self.play('transition_up')
    
    def play_transition_down(self):
        self.play('transition_down')
    
    def start_ringtone_loop(self):
        """Start ringtone loop for exam alerts"""
        self.start_loop('ringtone_loop')
    
    def stop_ringtone_loop(self):
        """Stop ringtone loop"""
        self.stop_loop('ringtone_loop')
    
    def start_progress_loop(self):
        """Start progress loop for pomodoro"""
        self.start_loop('progress_loop')
    
    def stop_progress_loop(self):
        """Stop progress loop"""
        self.stop_loop('progress_loop')
