import rapid_life


rl=rapid_life.rapid_life()

rl.add_instruction(rules=[[5], [0, 6, 7]], neighborhood=[[0, 1, 0, 1, 0], [1, 1, 0, 1, 1], [0, 0, 0, 0, 0], [1, 1, 0, 1, 1], [0, 1, 0, 1, 0]])
rl.add_instruction(rules=[[2], []], neighborhood=[[0, 1, 1, 1, 0], [1, 0, 0, 0, 1], [1, 0, 0, 0, 1], [1, 0, 0, 0, 1], [0, 1, 1, 1, 0]])


rl.run()
