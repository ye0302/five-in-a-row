import pygame
from pygame.sprite import Sprite


class Chess(Sprite):
    """ 一个对飞船发射的子弹进行管理的类 """

    def __init__(self, ai_settings, screen, map, index_x, index_y, index):
        super().__init__()
        self.screen = screen
        self.ai_settings = ai_settings
        file_list = ["./image/black.png", "./image/white.png", "./image/over_chess.png"]
        file = file_list[index - 1]
        self.image = pygame.image.load(file)
        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()
        self.rect.centerx = index_x * 32.57 + 24 + map.rect.left
        self.rect.centery = index_y * 32.57 + 22 + map.rect.top

    def draw_chess(self):
        """ 在屏幕上绘制子弹 """
        self.screen.blit(self.image, self.rect)
