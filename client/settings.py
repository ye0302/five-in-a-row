import os,pygame

class Settings:

    def __init__(self):
        pygame.init()
        self.screen_width = 550
        self.screen_height = 800
        self.bg_color = (255, 255, 240)
        os.environ["SDL_VIDEO_WINDOW_POS"] = "%d,%d" % (700, 200)
