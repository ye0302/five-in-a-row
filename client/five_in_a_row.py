import re, sys, os

sys.path.append("/home/tarena/zhixuda/aid1909/my_project")
from client.button import RemindButton, ClickButton
from client.login_register import LoginAndRegister
from client.game_functions import *
from client.settings import Settings
from client.chessboard import Chessboard
from threading import Thread
from time import sleep
from client.bll import ClientCoreController
from client.model import Location


class GameView:
    def __init__(self):
        self.manager = ClientCoreController()
        self.ai_settings = Settings()
        self.game_is_alive = False
        self.own = None
        self.adverse = None

    def __do_login_or_register(self):
        """
            登录注册
        """
        lr = LoginAndRegister(self.manager)
        lr.login_and_register()
        self.own = lr.user
        return lr.is_online

    def run_game(self):
        """
            游戏入口
        :return:
        """
        if not self.__do_login_or_register():  # 登记注册
            return
        self.create_initial_window()
        while True:
            self.get_start_button()
            t = Thread(target=self.outplay)
            t.setDaemon(True)
            t.start()
            self.update_by_adverse()

    def update_by_adverse(self):
        while not self.game_is_alive:
            sleep(1)
        self.start()
        self.wait_destribute()  # 分配房间
        self.update_by_recv()  # 接受对方走棋，更新棋盘

    def outplay(self):
        """
            根据鼠标点击位置走棋
        """
        time = 45
        while True:
            result = self.uc.check_events(self.give_up_button, self.regret_game_button,
                                          self.game_is_alive, self.start_button)
            if result == "S" and not self.game_is_alive:
                self.manager.join_game()
                self.game_is_alive = True
                continue
            if result == "G":
                self.do_gove_up()
            if result == "R":
                pass
            if result and self.game_is_alive:
                self.manager.outplay(*result)
                self.draw_map()
            # if self.uc.time != time and self.game_is_alive:
            #     self.draw_map()
            #     time = self.uc.time

    def create_initial_window(self):
        """
            创建游戏的最初窗口
        """
        self.screen = pygame.display.set_mode(
            (self.ai_settings.screen_width, self.ai_settings.screen_height))
        pygame.display.set_caption("five in a row")
        self.chessboard = Chessboard(self.ai_settings, self.screen)
        self.uc = UpdateChess(self.ai_settings, self.screen, self.chessboard)
        self.get_give_up_button()
        self.get_regret_game_button()

    def get_start_button(self):
        self.screen_rect = self.screen.get_rect()
        self.start_button = ClickButton(self.screen, self.screen_rect.centerx, self.screen_rect.centery - 5, "Start")
        self.draw_map(self.start_button)

    def get_give_up_button(self):
        self.give_up_button = ClickButton(self.screen, 90, 760, "Give up", (128, 128, 128))

    def get_regret_game_button(self):
        self.regret_game_button = ClickButton(self.screen, 90, 720, "Regret game", (255, 136, 20))

    def start(self):
        wait_button = RemindButton(self.screen, "Waiting room")
        self.uc.create_own_scoreboard(self.own)
        self.draw_map(wait_button)

    def wait_destribute(self):
        """
            等待分配房间和先手棋
        """
        chess_color, self.adverse = self.manager.wait_destribute()
        button = self.create_remind_button(chess_color)
        self.uc.create_adverse_scoreboard(self.adverse)
        self.draw_map(button)
        sleep(2)


    def create_remind_button(self, chess_color):
        """
            根据分配的棋子颜色创建体现按钮
        :param chess_color:
        """
        self.uc.chess_color = chess_color
        self.uc.opposent_chess_color = 3 - chess_color
        if chess_color == 1:
            self.uc.can_discard = True
            button = RemindButton(self.screen, "Black discover")
        else:
            button = RemindButton(self.screen, "White chess")
        return button

    def update_by_recv(self):
        """
            接受对方走棋，更新棋盘
        """
        while self.game_is_alive:
            data = self.manager.opposite_outplay()
            if data[0] == "P":
                self.uc.add_oppose_chess(data[1])
                self.draw_map()
            elif data[0] == "O":
                self.do_end_status(data[1])

    def do_end_status(self, status):
        """
            处理结束状态
        """
        ending_button, is_quit = self.get_end_remind(status)
        self.game_is_alive = False
        if is_quit:
            self.draw_map(ending_button)
            sleep(3)
        else:
            over_list = self.manager.get_stop_position()
            self.uc.game_over(over_list)
            self.draw_over_map(ending_button)
        self.uc.do_end_status()

    def get_end_remind(self, status):
        """
            结束提醒按钮
        :param status:
        :return:
        """
        if status == "LOSE":
            ending_button = RemindButton(self.screen, "You lost")
            self.own.lose_count += 1
            return ending_button, False
        ending_button = RemindButton(self.screen, "You win")
        self.own.win_count += 1
        if status == "QWIN":
            return ending_button, True
        return ending_button, False

    def draw_map(self, button=None):
        """
            对方或己方走棋后更新地图
        """
        self.uc.update_screen(self.screen, self.ai_settings, self.chessboard, button,
                              self.give_up_button, self.regret_game_button, self.game_is_alive)

    def draw_over_map(self, ending_button):
        """
            凸显游戏结束的棋子位置，绘制三次
        """
        for i in range(3):
            self.draw_map(ending_button)
            sleep(0.5)
            self.uc.update_over_screen(ending_button)
            sleep(0.5)

    def do_gove_up(self):
        self.manager.gave_up()
        sleep(1)

    # def get_countdown_button(self):
    #     for item in self.uc.countdown()


if __name__ == '__main__':
    g = GameView()
    g.run_game()
