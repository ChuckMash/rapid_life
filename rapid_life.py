import time
import os
import random
from collections import deque
import cv2
import numpy as np
from hashlib import sha1



class rapid_life:

  def __init__(self, use_umat=True, res=(1920,1080), fullscreen=False, drawing=True, auto_restart=False):
    ###
    self.display_name       = "Rapid Life"
    self.save_dir           = "./saves"
    self.draw_on            = 4          # Mouse button to draw with
    self.default_rprob      = 0.8        # default probability for random boards. Value can be 0.0 - 1.0
    self.drawing_radius     = 5          # how large to draw the circle
    self.drawing_thickness  = 1          # how thick the line of the circle, can be negative to infill
    self.drawing_line_type  = cv2.LINE_4 # cv2.LINE_4, cv2.LINE_18, cv2.LINE_AA (4, 8, 16)
    self.ar_bucket          = 25         # number of recent game frames to keep track of to comapre against for endgame state
    self.ar_match_limit     = 5          # number of times current game frame can appear in recent frames before calling a game over
    self.save_endgames      = False      # will save the endgame state, usefull for validating auto_restart endgame detection
    self.kernel_rand_size   = [3, 7]     # for use with the experimentel kernel randomizer
    self.kernel_rand_square = True       # locks the kernel randomizer to be perfect square when selecting random values
    self.recording_fps      = 60         # FPS to use when recording


    self.key_commands = { # function storage for keyboard commands, allows user to define new or override existing command callbacks
      27:  self.stop,             # ESC key, quits game
      32:  self.pause,            # Space Bar, pauses / unpauses game
      99:  self.clear,            # c key, clears game board entirely
      114: self.randomize_board,  # r key, randomizes game board entirely
      115: self.save_board,       # s key
      108: self.load_board,       # l key
      8:   self.randomize_kernel, # backspace experimental kernel randomizer
      255: self.save_kernel,      # del saves current kernel
      13:  self.toggle_record     # enter to record / stop reccord
      }

    self.actual_kernel = [[1,1,1],[1,0,1],[1,1,1]] # default

    # Alternate kernels are supported experimentally
    #self.actual_kernel = [[0,1,0,0],[1,1,0,0],[1,1,0,0],[1,1,0,0],[0,1,1,0]] # cascade
    #self.actual_kernel = [[0,0,1,0,1],[0,1,0,0,0],[0,1,0,1,0],[0,1,0,0,0],[0,1,0,0,1]] # Slow Blob Growth

    ### Nothing to change here.
    self.start_time    = time.time()
    self.use_umat      = use_umat     # True/False for enable/disable cv2 UMat usage (GPU)
    self.res           = res          # (x,y) resolution
    self.fullscreen    = fullscreen   # True/False for fullscreen display
    self.drawing       = drawing      # True/False for enabling the draw on game board feature
    self.auto_restart  = auto_restart # will try and detect if the game is over and reset. Somewhat lowers performance.
    self.stopped       = False        # Full stop, set to True to quit
    self.paused        = False        # temp stop, pause game board progression
    self.displaying    = False
    self.do_clear      = False
    self.recording     = False
    self.video_out     = None
    self.board         = self.zero_value()
    self.kernel        = self.kernel_value()
    self.transforms    = [ self.zero_value() for i in range(7) ]
    self.frame_count   = 0
    self.t6_count      = 0
    self.recent_frames = deque(maxlen=self.ar_bucket)
    self.latest_save   = None
    self.save_dir      = os.path.abspath(self.save_dir)+"/"



  # Flag setting functions
  def stop(self):  self.stopped  = True
  def pause(self): self.paused   = not self.paused
  def clear(self): self.do_clear = True



  # blank it all out
  def reset_board(self):
    self.board      = self.zero_value()
    self.kernel     = self.kernel_value()
    self.transforms = [ self.zero_value() for i in range(7) ]



  # Returns cv2 umat or np matrix. All zeros, the resolution of the game board
  def zero_value(self):
    val = np.zeros((self.res[1], self.res[0], 1), np.uint8)
    if self.use_umat:
      return cv2.UMat(val)
    return val



  # Returns cv2 umat or np matrix of the generic GOL kernel
  def kernel_value(self):
    val = np.array(self.actual_kernel, np.uint8)
    if self.use_umat:
      return cv2.UMat(val)
    return val



  # Returns cv2 umat or np matrix of a randomized state size of game board
  def random_value(self, p=None):
    val = np.uint8(np.random.choice([0,1], size=(self.res[1], self.res[0], 1), p=[1-(p or self.default_rprob), (p or self.default_rprob)]))
    if self.use_umat:
      return cv2.UMat(val)
    return val



  # overrides the current game board state with randomized values
  def randomize_board(self, p=None):
    self.board = self.random_value(p=p)



  # experimental function for kernel randomization
  def randomize_kernel(self):
    if self.kernel_rand_square:
      kx = ky = random.randint(self.kernel_rand_size[0], self.kernel_rand_size[1])
    else:
      kx = random.randint(self.kernel_rand_size[0], self.kernel_rand_size[1])
      ky = random.randint(self.kernel_rand_size[0], self.kernel_rand_size[1])

    self.actual_kernel = np.uint8(np.random.choice([0,1], size=(kx, ky)))
    self.kernel = self.kernel_value()
    print("new kernel", np.array(self.actual_kernel, np.uint8).tolist() )
    self.randomize_board()



  # experimental function to save random kernels because they are neat
  def save_kernel(self):
    with open("kernels.dat", "a") as f:
      f.write(str(np.array(self.actual_kernel, np.uint8).tolist()))
      f.write("\n\n")



  # overrides the current game board state with all zeros
  def blank_board(self):
    self.board = self.zero_value()



  # Advances the game board one step.
  def step_forward(self):
    if self.do_clear:
      self.reset_board()
      self.do_clear = False

    if self.paused:
      time.sleep(.01) # meh
      self.frame_count += 1 # needed to show drawing while paused
      return

    # the good stuff
    cv2.filter2D    (self.board, -1, self.kernel, self.transforms[0])
    cv2.threshold   (self.transforms[0], 1, 1, cv2.THRESH_BINARY, self.transforms[1])
    cv2.threshold   (self.transforms[0], 2, 1, cv2.THRESH_BINARY, self.transforms[2])
    cv2.threshold   (self.transforms[0], 3, 1, cv2.THRESH_BINARY_INV, self.transforms[3])
    cv2.bitwise_and (self.transforms[1], self.board, self.transforms[4])
    cv2.bitwise_or  (self.transforms[4], self.transforms[2], self.transforms[5])
    cv2.bitwise_and (self.transforms[5], self.transforms[3], self.board)
    self.frame_count += 1

    if self.auto_restart:
      self.check_endgame()



  # Trys to see if the game is over
  # severe performance hit, alternative wanted
  def check_endgame(self):
    tmp_board = sha1(self.get_board()).hexdigest()
    self.recent_frames.append(tmp_board)
    n = self.recent_frames.count(tmp_board)
    if n >= self.ar_match_limit:
      print("detected endgame")
      if self.save_endgames:
        self.save_board()
      self.randomize_board()



  # returns cv2 display ready image, numpy matrix or umat depending
  def get_image(self):
    if self.frame_count > self.t6_count: # only run this transform once per game step
      cv2.threshold(self.board, 0, 255, cv2.THRESH_BINARY, self.transforms[6])
      self.t6_count = self.frame_count
    if self.recording:
      self.video_out.write( cv2.cvtColor(self.transforms[6], cv2.COLOR_GRAY2BGR) )
    return self.transforms[6]



  # returns np matrix of game board
  def get_board(self):
    if self.use_umat: # maybe use instance check instead
      return cv2.UMat.get(self.board) # store this somewhere in case we get it more than once
    return self.board



  # returns cv2 UMat of game board if umat is enabled
  def get_umat(self):
    if not self.use_umat: # maybe use instance check instead
      return False # use_umat is disabled
    return self.board



  # yields cv2 display ready images
  def yield_images(self):
    while not self.stopped:
      self.step_forward()
      yield self.get_image()



  # Displays the game board, or passed argument
  def display_board(self, image=None):
    if not self.displaying:
      self.init_display()
    if image is None:
      image = self.get_image()
    cv2.imshow(self.display_name, image)
    return self.parse_keyboard_response(cv2.waitKey(1))



  # Deals with key presses coming back from cv2.imshow
  def parse_keyboard_response(self, k):
    if k in self.key_commands:           # is there a command paired to this key
      if callable(self.key_commands[k]): # is this command actually callable
        self.key_commands[k]()           # call the command
    elif k != -1:
      print(k) # if we don't know the key, print it



  # Sets up for display
  def init_display(self):
    options = 0
    options |= cv2.WINDOW_GUI_NORMAL # disable right click menu

    if self.fullscreen:
      options |= cv2.WND_PROP_FULLSCREEN
    else:
      options |= cv2.WINDOW_AUTOSIZE # lets the window do whatever

    cv2.namedWindow(self.display_name, options)

    if self.fullscreen:
      cv2.setWindowProperty(self.display_name,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

    if self.drawing:
      cv2.setMouseCallback(self.display_name, self.draw)

    self.displaying = True



  # destroys the display window
  def end_display(self):
    if self.displaying:
      cv2.destroyWindow(self.display_name)



  # This function deals with the callback for mouse events if drawing
  def draw(self, event, x, y, flags, param):
    if flags == self.draw_on:
      self.board = cv2.circle(self.board, (x,y), self.drawing_radius, 1, self.drawing_thickness, self.drawing_line_type, 0)



  # Exports the game board state
  # Work in progress
  def save_board(self, f=None, type="basic"):
    types = ["basic", "png"]

    if type not in types:
      print("save type must be one the following: %s" % ','.join(types))
      return

    if not os.path.exists(self.save_dir):
      os.makedirs(self.save_dir)

    if type == "basic":
      filename = '%s%s_%s.dat' % (self.save_dir, self.start_time, self.frame_count)
      data = self.get_board().tolist()
      odata = ""
      for dat in data:
        odata += ''.join([str(i) for i in dat])
        odata += "\n"

      with open(filename,"w") as f:
        f.write(odata)

    elif type == "png":
      filename = '%s%s_%s.png' % (self.save_dir, self.start_time, self.frame_count)
      cv2.imwrite(filename, self.get_image())

    self.latest_save = filename



  # Imports the game board state
  # Work in progress
  def load_board(self, filename=None, type="basic"):
    types = ["basic"]
    if type not in types:
      print("load types must be one of the following: %s" % ','.join(types))
      return

    if filename is None:
      filename = self.latest_save

    if not filename:
      return

    if type == "basic":
      with open(filename, "r") as f:
        data = f.read().strip()
      data = [[int(i) for i in line] for line in data.split("\n")]
      odata = np.uint8(np.array(data, dtype=int))
      if self.use_umat:
        self.board = cv2.UMat(odata)
      else:
        self.board = odata



  # toggle the record video state
  def toggle_record(self):
    if not self.recording:
      self.start_recording()
    else:
      self.stop_recording()



  # Start recording video
  def start_recording(self):
    if not self.recording:
      print("start recording")
      self.recording = True
      fourcc = cv2.VideoWriter_fourcc(*'MP4V')
      self.video_out = cv2.VideoWriter("output.mp4", fourcc, self.recording_fps, self.res )
      return True
    else:
      print("already recording")
      return False



  # Stop recording video
  def stop_recording(self):
    if self.recording:
      print("stop recording")
      self.video_out.release()
      self.video_out = None
      self.recording = False
      return(True) # alternate idea, return the filename recorded
    else:
      print("already not recording....")
      return(False)



  # Run and show the game
  def run(self, randomize=True):
    if randomize:
      self.randomize_board()
    for image in self.yield_images():
      self.display_board()



  # Just run the game
  def sim(self, randomize=True):
    if randomize:
      self.randomize_board()
    while not self.stopped:
      self.step_forward()





if __name__ == "__main__":
  life = rapid_life()
  life.run()

