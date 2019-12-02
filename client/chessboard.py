import pygame


class Chessboard:
    def __init__(self, ai_settings, screen):
        self.screen = screen
        self.ai_settings = ai_settings
        self.image = pygame.image.load('./image/timg.jpeg')
        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()
        self.rect.centerx = self.screen_rect.centerx  # 中央
        self.rect.centery = self.screen_rect.centery  # 底部

    def blitme(self):
        self.screen.blit(self.image, self.rect)
