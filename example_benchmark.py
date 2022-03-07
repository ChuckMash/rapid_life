import rapid_life
import cv2
import time
import platform


def benchmark(res=(1920,1080), steps=1000, display=False, use_umat=True, fullscreen=False):
  life = rapid_life.rapid_life(res=res, use_umat=use_umat, fullscreen=fullscreen)
  life.randomize_board()
  start_time = time.time()
  if display:
    life.run(randomize=False, limit=steps)
  else:
    life.sim(randomize=False, limit=steps)
  time_taken = time.time() - start_time

  print("\n----------------------------")
  print("UMat:",             life.use_umat)
  print("Display:",          display)
  print("Fullscreen:",       fullscreen)
  print("Resolution:",        life.res)
  print("Steps:",            steps)
  print("Calculated FPS:",   steps / time_taken)



if __name__ == "__main__":
  print("OpenCV:", cv2.__version__)
  print(platform.platform())
  print(platform.processor())

  benchmark(steps=1000)

  # Increase step count for more reliable benchmark
