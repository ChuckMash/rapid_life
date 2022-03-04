import time
import os
import random
from collections import deque
import cv2
import numpy as np
from hashlib import sha1



class rapid_life:

  def __init__(self, use_umat=True, res=(1920,1080), display_res=None, fullscreen=False, drawing=True, detect_endgame=False):
    ###
    self.display_name       = "Rapid Life"
    self.save_dir           = "./saves"
    self.draw_on            = 4          # Mouse button to draw with, set to -1 for always draw on mouse movement
    self.default_rprob      = 0.8        # default probability for random boards. Value can be 0.0 - 1.0
    self.drawing_radius     = 5          # how large to draw the circle
    self.drawing_thickness  = 1          # how thick the line of the circle, can be negative to infill
    self.drawing_line_type  = cv2.LINE_4 # cv2.LINE_4, cv2.LINE_18, cv2.LINE_AA (4, 8, 16)
    self.ar_bucket          = 25         # number of recent game frames to keep track of to comapre against for endgame state
    self.ar_match_limit     = 5          # number of times current game frame can appear in recent frames before calling an endgame
    self.save_endgames      = False      # will save the endgame state, usefull for validating endgame detection
    self.recording_fps      = 60         # FPS to use when recording
    self.discard_first_n    = 0          # disgard the first n number of game frames after board randomization
    self.display_every_nth  = 0          # only show every nth step for display, 0 is every frame.

    self.key_commands = { # function storage for keyboard commands, allows user to define new or override existing command callbacks
      27:  self.stop,             # ESC key, quits game
      32:  self.pause,            # Space Bar, pauses / unpauses game
      99:  self.clear,            # c key, clears game board entirely
      114: self.randomize_board,  # r key, randomizes game board entirely
      115: self.save_board,       # s key
      108: self.load_board,       # l key
      13:  self.toggle_record,    # enter to record / stop reccord
      110: self.step_and_display  # n key, next step when paused
      }

    ### Nothing to change here.
    self.start_time     = time.time()
    self.use_umat       = use_umat       # True/False for enable/disable cv2 UMat usage (GPU)
    self.res            = res            # (x,y) resolution
    self.fullscreen     = fullscreen     # True/False for fullscreen display
    self.drawing        = drawing        # True/False for enabling the draw on game board feature
    self.detect_endgame = detect_endgame # will try and detect if the game is over and reset. Somewhat lowers performance.
    self.endgame_style  = "quit"         # what to do at endgame restart or quit
    self.display_res    = display_res    # The resolution to display the board as, if different than processing res
    self.stopped        = False          # Full stop, set to True to quit
    self.paused         = False          # temp stop, pause game board progression
    self.displaying     = False
    self.do_clear       = False
    self.recording      = False
    self.video_out      = None
    self.board          = self.zero_value()
    self.frame_count    = 0
    self.t6_count       = 0
    self.recent_frames  = deque(maxlen=self.ar_bucket)
    self.latest_save    = None
    self.save_dir       = os.path.abspath(self.save_dir)+"/"
    self.instructions   = []
    self.change_res     = not display_res in [None, res]



  # Flag setting functions
  def pause(self): self.paused   = not self.paused
  def clear(self): self.do_clear = True
  def stop(self):
    self.stopped  = True
    if self.recording:
      self.stop_recording()



  # Instructions for the alternate approach to processing, much much faster
  def add_instruction(self, rules=[[3],[2,3]], offset=125, neighborhood=[[1,1,1],[1,0,1],[1,1,1]], anchor=(-1,-1), interval=1, count_offset=0):
    if len(rules) == 3: # Convert old style ruleset to new style
      if rules[0] <= rules[1]:
        birth=list(range(rules[1], rules[2]))
        survive=list(range(rules[0], rules[2]))
      elif rules[0] >= rules[1] <= rules[2]:
        birth=list(range(rules[1], rules[2]))
        survive=list(range(rules[1], rules[2]))
      elif rules[0] > rules[1] > rules[2]:
        print("invalid ruleset?")
        return False
      #print(rules, "becomes", [birth, survive])

    elif len(rules) == 2:
      birth = rules[0]
      survive = rules[1]

    # check out of bounds
    if any(i > offset for i in birth+survive):
      print("Birth/Survive settings cannot be higher than offset.")
      return

    data                 = {}
    data["id"]           = len(self.instructions)
    data["type"]         = 1
    data["neighborhood"] = neighborhood
    data["transforms"]   = [self.zero_value(), self.zero_value()]
    data["kernel"]       = np.array(data["neighborhood"], np.uint8)
    data["anchor"]       = (anchor[0], anchor[1])
    data["interval"]     = interval
    data["count_offset"] = count_offset

    # if anchor is default, find the actual location in kernel
    if data["anchor"] == (-1, -1):
      ks = np.array(data["kernel"].shape)
      hks = (ks-1)/2
      data["anchor"] = (int(round(hks[0])), int(round(hks[1])))

    # Set up the LUT
    lut = [0]*256
    for b in birth:
      lut[b] = 1
    for s in survive:
      lut[s+offset] = 1

    # Apply the offset to the anchor
    try:
      data["kernel"][data["anchor"]] = data["kernel"][data["anchor"]]+offset
    except Exception as e: # anchor is outside the kernel
      pass

    # add the lut
    data["LUT"] = np.array(lut, np.uint8)

    if self.use_umat:
      data["kernel"] = cv2.UMat(data["kernel"])
      data["LUT"]    = cv2.UMat(data["LUT"])

    self.instructions.append(data)



  # blank it all out
  def reset_board(self):
    self.board = self.zero_value()



  # Returns cv2 umat or np matrix. All zeros, the resolution of the game board
  def zero_value(self):
    val = np.zeros((self.res[1], self.res[0], 1), np.uint8)
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
    for i in range(self.discard_first_n):
      self.step_forward()



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

    if not self.instructions: # woops, we managed to start without any instructions
      self.add_instruction() # add default

    for inst in self.instructions:
      if (self.frame_count + inst["count_offset"]) % inst["interval"] == 0:

        # just the good stuff
        cv2.filter2D(self.board, -1, inst["kernel"], inst["transforms"][0], inst["anchor"])
        cv2.LUT(inst["transforms"][0], inst["LUT"], self.board)

    self.frame_count += 1

    if self.detect_endgame:
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
      if self.endgame_style == "quit":
        self.stop()
      elif self.endgame_style == "restart":
        self.randomize_board()



  # Returns cv2 display ready image, numpy matrix or UMat depending
  def get_image(self):
    if self.frame_count > self.t6_count: # only run this transform once per game step
      cv2.threshold(self.board, 0, 255, cv2.THRESH_BINARY, self.instructions[-1]["transforms"][-1]) # stash the converted image in the last slot
      self.t6_count = self.frame_count

    if self.recording:
      self.video_out.write( self.instructions[-1]["transforms"][-1] )

    return self.instructions[-1]["transforms"][-1]



  # Returns np matrix of game board
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
    if self.display_every_nth:
      if self.frame_count % self.display_every_nth != 0:
        return
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
      if self.change_res:
        options |= cv2.WINDOW_KEEPRATIO
      else:
        options |= cv2.WINDOW_AUTOSIZE # lets the window do whatever

    cv2.namedWindow(self.display_name, options)

    if self.fullscreen:
      cv2.setWindowProperty(self.display_name,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

    elif self.change_res:
      cv2.resizeWindow(self.display_name, self.display_res[0], self.display_res[1])

    if self.drawing:
      cv2.setMouseCallback(self.display_name, self.draw)

    self.displaying = True



  # destroys the display window
  def end_display(self):
    if self.displaying:
      cv2.destroyWindow(self.display_name)



  # This function deals with the callback for mouse events if drawing
  def draw(self, event, x, y, flags, param):
    if flags == self.draw_on or self.draw_on == -1:
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
      self.video_out = cv2.VideoWriter("output.mp4", fourcc, self.recording_fps, self.res, 0)
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



  # When paused, step forward one game tick
  def step_and_display(self):
    if not self.paused: # do nothing
      return
    self.paused=False
    self.step_forward()
    self.paused=True



  # Run and show the game
  def run(self, randomize=True, limit=0):
    if randomize:
      self.randomize_board()
    count = 0
    while not self.stopped:
      self.step_forward()
      self.display_board()
      if not limit:
        continue
      count += 1
      if count >= limit:
        return



  # Just run the game
  def sim(self, randomize=True, limit=0):
    if randomize:
      self.randomize_board()
    count = 0
    while not self.stopped:
      self.step_forward()
      if not limit:
        continue
      count += 1
      if count >= limit:
        return




if __name__ == "__main__":
  life = rapid_life()
  life.run()
