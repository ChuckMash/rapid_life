import rapid_life
import socket
import time

res = (44,11)

ip = "192.168.1.105" # your WLED IP address
port = 21324

rl=rapid_life.rapid_life(res=res, detect_endgame=True)
rl.discard_first_n = 2
rl.default_rprob = 0.5
rl.randomize_board()

while not rl.stopped:
  rl.step_forward()
  #rl.display_board()
  data = rl.get_board()
  data = data.tolist()

  flip=False
  out_b = [2,2]
  for dat in data:
    if flip:
      dat.reverse()
    flip = not flip

    for da in dat:
      if da:
        out_b.extend([255,255,255])
      else:
        out_b.extend([0,0,0])

  clientSock = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
  clientSock.sendto(bytes(out_b), (ip, port))

  time.sleep(.03)
