import os
import pygame

# -----------------------------
# Sound Engine (Singleton-style)
# -----------------------------
class SoundEngine:
    _initialized = False

    @classmethod
    def init(cls):
        if cls._initialized:
            return
        try:
            pygame.mixer.init()
            cls._initialized = True
        except Exception as e:
            print("Sound engine init failed:", e)
            cls._initialized = False

    @classmethod
    def play(cls, sound_path, volume=1.0):
        if not sound_path:
            return

        cls.init()
        if not cls._initialized:
            return

        if not os.path.exists(sound_path):
            print("Sound file not found:", sound_path)
            return

        try:
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(max(0.0, min(volume, 1.0)))
            sound.play()
        except Exception as e:
            print("Sound play error:", e)
