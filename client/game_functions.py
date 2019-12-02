import os
import sys
from threading import Thread
from time import sleep

import pygame

sys.path.append("/home/tarena/zhixuda/aid1909/my_project")
from client.chess import Chess
from client.button import Board
from pygame.sprite import Group


class UpdateChess:
    def __init__(self, ai_settings, screen, chessboard):
        self.ai_settings = ai_settings
        self.screen = screen
        self.chessboard = chessboard
        self.white_chesses = Group()
        self.black_chesses = Group()
        self.over_chesses = Group()
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
        self.own_score_list = []
        self.adverse_score_list = []
        # self.time = -1
        # self.get_initial_time_button()
        # self.time_button = self.own_time_button
        # self.update_countdown_button()

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
            self.time = 45

    def game_over(self, over_list):
        """
            根据游戏结束是棋子坐标创建结束位置棋子
        :param over_list: 棋子坐标列表
        """
        self.can_discard = False
        self.time = -1
        for index_y, index_x in over_list:
            self.map[index_y][index_x] = 3
            new_chess = Chess(self.ai_settings, self.screen, self.chessboard, index_x, index_y, 3)
            self.over_chesses.add(new_chess)

    def check_events(self, gameup, regret_game, game_status=True, start_button=None):
        """ 响应按键和鼠标事件 """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("游戏结束")
                os._exit(1)
            elif event.type == pygame.MOUSEBUTTONDOWN:  # 鼠标点击事件
                if event.button == 1:
                    return self.do_mouse_button_down(gameup, regret_game, game_status, event, start_button)

    def do_mouse_button_down(self, gameup, regret_game, game_status, event, start_button):
        """
            处理鼠标点击按钮事件
        :param gameup:
        :param regret_game:
        :param game_status:
        :param event:
        :param start_button:
        :return:
        """
        if not game_status:
            if start_button.rect.collidepoint(*event.pos):
                return "S"
        if game_status:
            if gameup.rect.collidepoint(*event.pos):
                return "G"
            if regret_game.rect.collidepoint(*event.pos):
                return "R"
        return self.add_chess(event)

    def add_chess(self, event):
        """
            根据鼠标点击，如果点击位置没有棋子并且处于可下子状态，则增加棋子并返回索引
        :param event:鼠标点击事件
        :return:棋子位置索引坐标
        """
        index_x = round((event.pos[0] - 24 - self.chessboard.rect.left) / 32.57)
        index_y = round((event.pos[1] - 22 - self.chessboard.rect.top) / 32.57)
        if 0 <= index_x <= 14 and 0 <= index_y <= 14:
            if not self.map[index_y][index_x] and self.can_discard:
                new_chess = Chess(self.ai_settings, self.screen, self.chessboard, index_x, index_y, self.chess_color)
                self.white_chesses.add(new_chess)
                self.map[index_y][index_x] = 1
                self.can_discard = False
                self.time = 45
                return index_y, index_x

    def update_screen(self, screen, ai_settings, map, start, giveup, regret_game, game_status):
        """
            更新窗口
        :param screen:
        :param ai_settings:
        :param map:
        :param start:
        :param giveup:
        :param regret_game:
        :param game_status:
        :return:
        """
        screen.fill(ai_settings.bg_color)
        map.blitme()
        self.update_chess()
        self.update_button(game_status, giveup, regret_game, start)
        self.drow_score()
        pygame.display.flip()

    def update_chess(self):
        """
            绘制棋子
        :return:
        """
        for chess in self.white_chesses.sprites():
            chess.draw_bullet()
        for chess in self.black_chesses.sprites():
            chess.draw_bullet()

    def update_button(self, game_status, giveup, regret_game, start):
        """
            绘制按钮
        :param game_status:
        :param giveup:
        :param regret_game:
        :param start:
        """
        if start:
            start.draw_button()
        if game_status:
            giveup.draw_button()
            regret_game.draw_button()
        # if self.chess_color:
        #     if self.can_discard:
        #         self.adverse_time_button.draw_button()
        #     else:
        #         self.own_time_button.draw_button()
        #     self.time_button.draw_button()

    def drow_score(self):
        """
            绘制成绩
        :return:
        """
        for item in self.own_score_list:
            item.draw_button()
        for item in self.adverse_score_list:
            item.draw_button()

    def create_adverse_scoreboard(self, adverse):
        """
            创建对手成绩对象
        :param adverse:
        :return:
        """
        self.adverse_score_list.clear()
        self.own_score_list.append(Board(self.screen, 100, 40, "win: %s" % adverse.win_count))
        self.own_score_list.append(Board(self.screen, 100, 80, "lose: %s" % adverse.lose_count))

    def create_own_scoreboard(self, user):
        """
            创建自己成绩对象
        :param adverse:
        :return:
        """
        self.own_score_list.clear()
        self.own_score_list.append(Board(self.screen, 390, 720, "win: %s" % user.win_count))
        self.own_score_list.append(Board(self.screen, 390, 755, "lose: %s" % user.lose_count))

    def update_over_screen(self, button):
        """
            绘制结束位置棋子
        :return:
        """
        for chess in self.over_chesses.sprites():
            chess.draw_bullet()
        button.draw_button()
        pygame.display.flip()

    def do_end_status(self):
        self.white_chesses.empty()
        self.black_chesses.empty()
        self.over_chesses.empty()
        for r in range(len(self.map)):
            for c in range(len(self.map[0])):
                self.map[r][c] = 0

    def countdown(self):
        while self.time != 0:
            if self.time > 0:
                if self.can_discard:
                    self.time_button = Board(self.screen, 240, 740, "countdown: %d" % self.time, (33, 226, 15))
                else:
                    self.time_button = Board(self.screen, 240, 60, "countdown: %d" % self.time, (33, 226, 15))
            sleep(1)
            self.time -= 1

    def update_countdown_button(self):
        t = Thread(target=self.countdown)
        t.setDaemon(True)
        t.start()

    def get_initial_time_button(self):
        self.own_time_button = Board(self.screen, 240, 740, "countdown: 45", (33, 226, 15))
        self.adverse_time_button = Board(self.screen, 240, 60, "countdown: 45", (33, 226, 15))

    def show(self):
        for line in self.map:
            for item in line:
                print(item, end=" ")
            print()
        print()
