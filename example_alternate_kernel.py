import rapid_life

rl = rapid_life.rapid_life()

#rl.update_kernel( [[0,1,0,0],[1,1,0,0],[1,1,0,0],[1,1,0,0],[0,1,1,0]] ) # cascade
#rl.update_kernel( [[0,0,1,0,1],[0,1,0,0,0],[0,1,0,1,0],[0,1,0,0,0],[0,1,0,0,1]] ) # Slow Blob Growth
rl.update_kernel( [[0,0,0,0,0],[0,0,0,0,0],[1,0,0,0,1],[1,1,1,1,1],[0,1,1,1,0]] ) # bubbler

rl.run(fullscreen=True)
