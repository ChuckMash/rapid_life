import rapid_life

rl = rapid_life.rapid_life(fullscreen=True)

rl.add_instruction( rules=[2,3,4], neighborhood=[[1,1,1],[1,0,1],[1,1,1]], anchor=[1,1] )
rl.add_instruction( rules=[20,1,5], neighborhood=[[0],[1]], anchor=[0,0] )

rl.run()
