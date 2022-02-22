import rapid_life

rl = rapid_life.rapid_life(fullscreen=True)

rl.add_instruction()
rl.add_instruction( rules=[20,1,5], neighborhood=[[0],[1]], anchor=[0,0])

rl.run()
