import rapid_life

rl=rapid_life.rapid_life()

rl.add_instruction(rules=[[], [4, 0]], neighborhood=[[0, 1, 0, 1, 0], [1, 1, 0, 1, 1], [0, 0, 0, 0, 0], [1, 1, 0, 1, 1], [0, 1, 0, 1, 0]])
rl.add_instruction(rules=[[0], [1, 3, 9]], neighborhood=[[0, 1, 1, 1, 0], [1, 0, 0, 0, 1], [1, 0, 0, 0, 1], [1, 0, 0, 0, 1], [0, 1, 1, 1, 0]])

rl.run()
