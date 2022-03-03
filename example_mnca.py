import rapid_life


rl = rapid_life.rapid_life(fullscreen=True)


rl.add_instruction(
  rules=[[3],[2,3]],
  neighborhood=[
    [1,1,1],
    [1,0,1],
    [1,1,1]
 ]
)


rl.add_instruction(
  rules=[[3],[2,3]],
  #rules=[[4],[3,4]],
  neighborhood=[
    [1,1,1,1,1],
    [1,1,1,1,1],
    [1,1,0,1,1],
    [1,1,1,1,1],
    [1,1,1,1,1],
 ]
)


rl.run()
