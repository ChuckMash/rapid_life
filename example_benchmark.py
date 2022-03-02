import rapid_life
import os
import cv2
import platform
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame


###
run_for = 1000
display = False
use_umat = True
###


clock = pygame.time.Clock()
fps_log = []

life = rapid_life.rapid_life(res=(1920,1080), use_umat=use_umat, fullscreen=True)
life.randomize_board()

for i in range(run_for):
  life.step_forward()
  if display:
    life.display_board()
  clock.tick()
  fps = clock.get_fps()

  if fps:
    fps_log.append(fps)

print("OpenCV:",      cv2.__version__)
print(platform.platform())
print(platform.processor())
print("UMat:",        life.use_umat)
print("display",      display)
print("Steps:",       run_for)
print("Average FPS:", sum(fps_log) / len(fps_log))

