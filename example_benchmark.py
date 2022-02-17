import rapid_life
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

run_for = 1000

clock = pygame.time.Clock()
fps_log = []

life = rapid_life.rapid_life(res=(1920,1080), use_umat=True, fullscreen=True)
life.randomize_board()

for i in range(run_for):
  life.step_forward()
  #life.display_board()
  clock.tick()
  fps = clock.get_fps()

  if fps:
    fps_log.append(fps)

print("Average FPS:", sum(fps_log) / len(fps_log))


