import rapid_life

rl=rapid_life.rapid_life(res=(320,200), display_res=(1920,1200), fullscreen=False, detect_endgame=True, use_umat=False)
rl.draw_on = 1
rl.discard_first_n = 2
rl.run()
