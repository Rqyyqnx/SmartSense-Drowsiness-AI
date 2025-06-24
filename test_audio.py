import pygame
import time

pygame.mixer.init()
sound = pygame.mixer.Sound("static/alert.wav")
sound.set_volume(1.0)

sound.play(loops=-1)  # Loop forever
time.sleep(10)        # Let it play for 10 seconds
sound.stop()          # Stop after that
