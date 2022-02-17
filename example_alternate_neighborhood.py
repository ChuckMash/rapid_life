import rapid_life


rl = rapid_life.rapid_life(fullscreen=True)

#rl.add_instruction(neighborhood=[[0,1,0,0],[1,1,0,0],[1,1,0,0],[1,1,0,0],[0,1,1,0]] ) # cascade
#rl.add_instruction(neighborhood=[[0,0,1,0,1],[0,1,0,0,0],[0,1,0,1,0],[0,1,0,0,0],[0,1,0,0,1]] ) # Slow Blob Growth
rl.add_instruction(neighborhood=[[0,0,0,0,0],[0,0,0,0,0],[1,0,0,0,1],[1,1,1,1,1],[0,1,1,1,0]] ) # bubbler

rl.run()
