import rapid_life

rl = rapid_life.rapid_life(fullscreen=True)

rl.add_instruction(
  rules = [5, 6, 10],
  neighborhood = [[0, 0, 1], [0, 1, 1], [1, 1, 1], [0, 0, 0], [0, 1, 1], [1, 0, 1]],
  anchor = [2, 2]
)

rl.add_instruction(
  rules = [1, 4, 13],
  neighborhood = [[1, 1, 0, 0, 0, 1, 1, 1], [0, 1, 1, 0, 0, 1, 1, 1], [1, 1, 1, 1, 1, 0, 1, 1], [0, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 0, 1, 1, 1], [1, 1, 1, 1, 0, 1, 1, 0]],
  anchor = [1, 5]
)

rl.add_instruction(
  rules = [4, 6, 9],
  neighborhood = [[1, 0, 1, 0, 0, 1, 0], [0, 1, 1, 1, 1, 1, 0], [0, 1, 0, 0, 1, 1, 0], [0, 0, 1, 1, 1, 1, 1], [0, 0, 0, 0, 1, 1, 1]],
  anchor = [1, 1]
)

rl.run()
