import os
import sys

import pygame

sys.path.append("/home/tarena/zhixuda/aid1909/my_project")
from client.chess import Chess
from pygame.sprite import Group


class UpdateChess:
    def __init__(self, ai_settings, screen, chessboard):
        self.ai_settings = ai_settings
        self.screen = screen
        self.chessboard = chessboard
        self.white_chesses = Group()
        self.black_chesses = Group()
        self.over_chesses = Group()
        self.color_chesses = Group()
        self.map = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        self.chess_color = None
        self.opposent_chess_color = None
        self.can_discard = False
        self.can_regret = False
        self.time = 47
        self.get_color_chess()

    def add_oppose_chess(self, position):
        """
            创建对手棋子
        :param position: 对手棋子坐标
        """
        if position:
            y = position[0]
            x = position[1]
            new_chess = Chess(self.ai_settings, self.screen, self.chessboard, x, y, self.opposent_chess_color)
            self.black_chesses.add(new_chess)
            self.map[y][x] = 2
            self.can_discard = True
            self.can_regret = False
            self.time = 45

    def game_over(self, over_list):
        """
            根据游戏结束是棋子坐标创建结束位置棋子
        :param over_list: 棋子坐标列表
        """
        self.can_discard = False
        self.count = 0
        self.over_chesses.empty()
        for index_y, index_x in over_list:
            self.map[index_y][index_x] = 3
            new_chess = Chess(self.ai_settings, self.screen, self.chessboard, index_x, index_y, 3)
            self.over_chesses.add(new_chess)

    def check_events(self, click_button, game_status, regret_click_button, regret_time):
        """ 响应按键和鼠标事件 """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                os._exit(1)
            elif event.type == pygame.MOUSEBUTTONDOWN:  # 鼠标点击事件
                if event.button == 1:
                    return self.do_mouse_button_down(click_button, event, game_status, regret_click_button, regret_time)

    def do_mouse_button_down(self, click_button, event, game_status, regret_click_button, regret_time):
        """
            处理鼠标点击按钮事件
        :param click_button:
        :param game_status:
        :param event:
        :return:
        """
        for i in range(len(click_button)):
            if click_button[i].rect.collidepoint(*event.pos):
                result = self.do_normal_click(i, game_status, regret_time)
                if result:
                    return result
        result = self.do_regret_click(regret_click_button, event)
        if result:
            return result
        return self.add_chess(event, regret_time)

    def do_regret_click(self, regret_click_button, event):
        for i in range(len(regret_click_button)):
            if regret_click_button[i].rect.collidepoint(*event.pos) and self.time <= 45:
                if i == 0:
                    return "A"
                if i == 1:
                    return "D"

    def do_normal_click(self, i, game_status, regret_time):
        if i == 0 and not game_status:
            return "S"
        if game_status and regret_time == 8:
            if self.chess_color:
                if i == 1:
                    return "G"
                if i == 2 and not self.can_discard and self.can_regret:
                    return "R"
            if not self.chess_color and i == 3:
                return "Q"

    def add_chess(self, event, regret_time):
        """
            根据鼠标点击，如果点击位置没有棋子并且处于可下子状态，则增加棋子并返回索引
        :param event:鼠标点击事件
        :return:棋子位置索引坐标
        """
        index_x = round((event.pos[0] - 24 - self.chessboard.rect.left) / 32.57)
        index_y = round((event.pos[1] - 22 - self.chessboard.rect.top) / 32.57)
        if 0 <= index_x <= 14 and 0 <= index_y <= 14:
            if not self.map[index_y][index_x] and self.can_discard and regret_time == 8:
                new_chess = Chess(self.ai_settings, self.screen, self.chessboard, index_x, index_y, self.chess_color)
                self.white_chesses.add(new_chess)
                self.map[index_y][index_x] = 1
                self.can_discard = False
                self.can_regret = True
                self.time = 45
                return index_y, index_x

    def update_screen(self, ai_settings, map, list_button):
        """
            更新窗口
        :param ai_settings:
        :param map:
        :param list_button:
        :return:
        """
        self.screen.fill(ai_settings.bg_color)
        map.blitme()
        self.update_chess()
        self.update_button(list_button)
        pygame.display.flip()

    def update_button(self, list_button):
        for item in list_button:
            item.draw_button()

    def update_chess(self):
        """
            绘制棋子
        :return:
        """
        for chess in self.white_chesses.sprites():
            chess.draw_chess()
        for chess in self.black_chesses.sprites():
            chess.draw_chess()
        for chess in self.color_chesses.sprites():
            chess.draw_chess()
        for chess in self.over_chesses.sprites():
            if 0 < self.count < 200 or 400 < self.count < 600:
                chess.draw_chess()
            self.count += 1
            if self.count > 600:
                self.over_chesses.empty()

    def do_end_status(self):
        self.white_chesses.empty()
        self.black_chesses.empty()
        self.color_chesses.empty()
        for r in range(len(self.map)):
            for c in range(len(self.map[0])):
                self.map[r][c] = 0
        self.chess_color = None
        self.opposent_chess_color = None
        self.time = 47

    def do_opponent_agree(self, position):
        for chess in self.white_chesses:
            if self.index_is_same(chess, position):
                self.white_chesses.remove(chess)
                self.map[position[0]][position[1]] = 0
        self.can_discard = True
        self.can_regret = False

    def index_is_same(self, chess, position):
        return round((chess.rect.centerx - 24 - self.chessboard.rect.left) / 32.57) == position[1] and \
               round((chess.rect.centery - 22 - self.chessboard.rect.top) / 32.57) == position[0]

    def do_agree(self, position):
        for chess in self.black_chesses:
            if self.index_is_same(chess, position):
                self.black_chesses.remove(chess)
                self.map[position[0]][position[1]] = 0
        self.can_discard = False
        self.can_regret = True

    def get_color_chess(self):
        self.own_black_chess = Chess(self.ai_settings, self.screen, self.chessboard, 13.5, 17.4, 1)
        self.own_white_chess = Chess(self.ai_settings, self.screen, self.chessboard, 13.5, 17.4, 2)
        self.opponent_black_chess = Chess(self.ai_settings, self.screen, self.chessboard, 0, -3.5, 1)
        self.opponent_white_chess = Chess(self.ai_settings, self.screen, self.chessboard, 0, -3.5, 2)

    def add_color(self, chess_color):
        if chess_color == 1:
            self.color_chesses.add(self.own_black_chess)
            self.color_chesses.add(self.opponent_white_chess)
        else:
            self.color_chesses.add(self.own_white_chess)
            self.color_chesses.add(self.opponent_black_chess)
