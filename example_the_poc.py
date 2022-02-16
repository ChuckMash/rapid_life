# Just the good stuff

import cv2, numpy as np

x,y = 1920,1080

board = cv2.UMat(np.uint8(np.random.choice([0,1], size=(y,x,1), p=[.2,.8])))
kernel = cv2.UMat(np.array([[1,1,1],[1,0,1],[1,1,1]], np.uint8))
transforms = [ cv2.UMat(np.zeros((y,x,1), np.uint8)) for i in range(7) ]

while True:
  cv2.filter2D    (board, -1, kernel, transforms[0])
  cv2.threshold   (transforms[0], 1, 1, cv2.THRESH_BINARY, transforms[1])
  cv2.threshold   (transforms[0], 2, 1, cv2.THRESH_BINARY, transforms[2])
  cv2.threshold   (transforms[0], 3, 1, cv2.THRESH_BINARY_INV, transforms[3])
  cv2.bitwise_and (transforms[1], board, transforms[4])
  cv2.bitwise_or  (transforms[4], transforms[2], transforms[5])
  cv2.bitwise_and (transforms[5], transforms[3], board)

  cv2.threshold(board, 0, 255, cv2.THRESH_BINARY, transforms[6])
  cv2.imshow('Rapid Life POC', transforms[6])
  if cv2.waitKey(1) == 27:
    break # esc to quit
