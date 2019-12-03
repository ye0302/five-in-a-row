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
        self.uc.get_start_button()
        t = Thread(target=self.outplay)
        t.setDaemon(True)
        t.start()
        while True:
            self.update_by_adverse()

    def update_by_adverse(self):
        while not self.game_is_alive:
            sleep(0.2)
        self.start()
        self.wait_destribute()  # 分配房间
        self.update_by_recv()  # 接受对方走棋，更新棋盘

    def outplay(self):
        """
            根据鼠标点击位置走棋
        """
        while True:
            result = self.uc.check_events(self.give_up_button, self.regret_game_button,
                                          self.game_is_alive)
            if result == "S" and not self.game_is_alive:
                self.manager.join_game()
                self.uc.game_is_alive = self.game_is_alive = True
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
        self.uc.get_wait_button()

    def get_give_up_button(self):
        self.give_up_button = ClickButton(self.screen, 90, 760, "Give up", (128, 128, 128))

    def get_regret_game_button(self):
        self.regret_game_button = ClickButton(self.screen, 90, 720, "Regret game", (255, 136, 20))

    def start(self):
        self.uc.create_own_scoreboard(self.own)

    def wait_destribute(self):
        """
            等待分配房间和先手棋
        """
        chess_color, self.adverse = self.manager.wait_destribute()
        self.uc.get_remind_button(chess_color)
        self.uc.create_adverse_scoreboard(self.adverse)
        self.uc.update_countdown_button(self)
        sleep(3)

    def update_by_recv(self):
        """
            接受对方走棋，更新棋盘
        """
        while self.game_is_alive:
            data = self.manager.opposite_outplay()
            if data[0] == "P":
                self.uc.add_oppose_chess(data[1])
            elif data[0] == "O":
                self.do_end_status(data[1])

    def do_end_status(self, status):
        """
            处理结束状态
        """
        is_quit = self.get_end_remind(status)
        self.uc.game_is_alive = self.game_is_alive = False
        self.opposent_chess_color = self.uc.chess_color = None
        if is_quit:
            sleep(2)
        else:
            over_list = self.manager.get_stop_position()
            self.uc.game_over(over_list)
            sleep(2)
        self.uc.do_end_status()

    def get_end_remind(self, status):
        """
            结束提醒按钮
        :param status:
        :return:
        """
        self.uc.get_end_remind(status)
        if status == "LOSE":
            self.own.lose_count += 1
            return
        self.own.win_count += 1
        if status == "QWIN":
            return True

    def draw_map(self):
        """
            对方或己方走棋后更新地图
        """
        self.uc.update_screen(self.ai_settings, self.chessboard,
                              self.give_up_button, self.regret_game_button)




    def do_gove_up(self):
        self.uc.game_is_alive = self.game_is_alive = False
        self.opposent_chess_color = self.uc.chess_color = None
        self.uc.do_end_status()
        self.manager.gave_up()
        sleep(1)

    # def get_countdown_button(self):
    #     for item in self.uc.countdown()


if __name__ == '__main__':
    g = GameView()
    g.run_game()
