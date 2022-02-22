import rapid_life

rl = rapid_life.rapid_life(fullscreen=True)

rl.add_instruction(
  rules=[13,2,10],
  neighborhood=[[1, 1, 1, 1, 1], [0, 1, 0, 0, 1], [1, 1, 0, 0, 1], [0, 1, 0, 0, 0], [0, 1, 1, 1, 1], [1, 0, 0, 1, 1]],
  anchor=[4,3]
)

rl.add_instruction(
  rules=[4,10,10],
  neighborhood=[[0, 0, 0, 1, 1, 1], [1, 1, 0, 1, 0, 1], [0, 0, 0, 1, 1, 1], [1, 0, 0, 1, 0, 1], [1, 1, 1, 0, 1, 0], [1, 0, 0, 1, 0, 1]],
  anchor=[5,5]
)

rl.add_instruction(
  rules=[12,5,8],
  neighborhood=[[1, 1, 0, 0, 0], [1, 1, 0, 1, 0], [0, 0, 1, 1, 1], [0, 1, 1, 1, 1], [1, 0, 0, 0, 0], [1, 1, 0, 0, 1], [0, 1, 0, 1, 1], [1, 1, 1, 0, 0]],
  anchor=[2,5]
)

rl.run()
