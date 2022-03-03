# Just the good stuff, but shorter & faster
import cv2, numpy as np
import time

x,y = 1920,1080

board = cv2.UMat(np.uint8(np.random.choice([0,1], size=(y,x,1), p=[.2,.8])))
kernel = cv2.UMat(np.array([[1,1,1],[1,10,1],[1,1,1]], np.uint8))
transforms = [cv2.UMat(np.zeros((y,x,1), np.uint8)) for i in range(2) ]
lut = cv2.UMat(np.array([0,0,0,1,0,0,0,0,0,0,0,0,1,1]+[0]*242, np.uint8))

while True:
  cv2.filter2D(board, -1, kernel, transforms[0])
  cv2.LUT(transforms[0], lut, board)

  cv2.threshold(board, 0, 255, cv2.THRESH_BINARY, transforms[1])
  cv2.imshow('Rapid Life POC', transforms[1])
  if cv2.waitKey(1) == 27:
    break # esc to quit
