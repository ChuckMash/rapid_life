import rapid_life
import cv2

rl = rapid_life.rapid_life(fullscreen=True)

rl.add_instruction( neighborhood=[[1,1,1],[1,0,1],[1,1,1]], anchor=[1,1] )
rl.add_instruction( rules=[[1,2,3,4],[1,2,3,4]], neighborhood=[[0],[1]], anchor=[0,0] )

rl.board = cv2.circle(rl.board, (960,1080), rl.drawing_radius, 1, rl.drawing_thickness, rl.drawing_line_type, 0)

rl.run(randomize=False)
