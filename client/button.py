import pygame.font


class Button:
    def __init__(self, screen):
        self.screen = screen
        self.screen_rect = screen.get_rect()

    def prep_msg(self, msg):
        self.msg_image = self.font.render(msg.encode(), True, self.text_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw_button(self):
        self.screen.blit(self.msg_image, self.msg_image_rect)


class RemindButton(Button):
    def __init__(self, screen, msg, y=0):
        super().__init__(screen)
        self.width, self.height = 200, 50
        self.text_color = (0, 255, 0)
        self.font = pygame.font.SysFont("Purisa", 48)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.right = self.screen_rect.right - 150
        self.rect.centery = self.screen_rect.centery - y
        self.prep_msg(msg)


class ClickButton(Button):
    def __init__(self, screen, x, y, msg, button_color=(255, 124, 221)):
        super().__init__(screen)
        self.width, self.height = 100, 30
        self.button_color = button_color
        self.text_color = (255, 255, 255)
        self.font = pygame.font.SysFont("Arial", 16)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.centerx = x
        self.rect.centery = y
        self.prep_msg(msg)

    def draw_button(self):
        self.screen.fill(self.button_color, self.rect)
        super().draw_button()


class Board(Button):
    def __init__(self, screen, x, y, msg, text_color=(0, 0, 0)):
        super().__init__(screen)
        self.width, self.height = 50, 18
        self.text_color = text_color
        self.font = pygame.font.SysFont("Arial", 24)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.left = x
        self.rect.bottom = y
        self.prep_msg(msg)


class RegretBoard(Button):
    def __init__(self, screen, msg, h, y=0):
        super().__init__(screen)
        self.width, self.height = 300, h
        self.text_color = (0, 0, 0)
        self.button_color = (244, 255, 243)
        self.font = pygame.font.SysFont("Arial", 24)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.centerx = self.screen_rect.centerx
        self.rect.centery = self.screen_rect.centery
        self.prep_msg(msg, y)

    def prep_msg(self, msg, y):
        super().prep_msg(msg)
        self.msg_image_rect.centery = self.rect.centery - y

    def draw_button(self):
        self.screen.fill(self.button_color, self.rect)
        super().draw_button()
