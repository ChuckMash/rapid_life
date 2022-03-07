# Big arrows
import rapid_life

rl = rapid_life.rapid_life(fullscreen=True, detect_endgame=False)
rl.display_color_mode = "neighborhood"
rl.endgame_style = "restart"
rl.add_instruction(rules=[[4], [3]], neighborhood=[[1, 1, 1], [1, 1, 1], [1, 1, 1]])
rl.add_instruction(rules=[[4], [4]], neighborhood=[[1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1]])
rl.run(randomize=True)

