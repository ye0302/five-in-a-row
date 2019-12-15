import sys

sys.path.append("/home/tarena/zhixuda/aid1909/my_project")
from client.create_button import CreateButton
from client.login_register import LoginAndRegister
from client.game_functions import *
from client.settings import Settings
from client.chessboard import Chessboard
from threading import Thread, Lock, Event
from time import sleep
from client.bll import ClientCoreController
from client.model import Location


class GameView:
    def __init__(self):
        self.manager = ClientCoreController()
        self.ai_settings = Settings()
        self.own = None
        self.adverse = None
        self.dict_func = {"Q": self.do_quit, "G": self.do_gove_up, "R": self.do_own_regret, "A": self.agree,
                          "D": self.disagree}
        self.e = Event()

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
        self.create_butt.add_start_button()
        t = Thread(target=self.outplay)
        t.setDaemon(True)
        t.start()
        while True:
            self.update_by_adverse()

    def update_by_adverse(self):
        self.e.wait()
        self.e.clear()
        self.wait_destribute()  # 分配房间
        self.update_by_recv()  # 接受对方走棋，更新棋盘

    def outplay(self):
        """
            根据鼠标点击位置走棋
        """
        while True:
            result = self.uc.check_events(self.create_butt.click_button, self.create_butt.game_is_alive
                                          , self.create_butt.regret_click_button, self.create_butt.regret_time)
            if result == "S" and not self.create_butt.game_is_alive:
                self.manager.join_game()
                self.create_butt.game_is_alive = True
                self.create_butt.mv_start_button(self.own)
                self.e.set()
                continue
            func = self.dict_func.get(result)
            if func:
                func()
            elif result and self.create_butt.game_is_alive:
                if self.create_butt.own_regret_count > 0:
                    self.create_butt.add_regret_button()
                self.manager.outplay(*result)
            self.draw_map()

    def create_initial_window(self):
        """
            创建游戏的最初窗口
        """
        self.screen = pygame.display.set_mode(
            (self.ai_settings.screen_width, self.ai_settings.screen_height))
        pygame.display.set_caption("five in a row")
        self.chessboard = Chessboard(self.ai_settings, self.screen)
        self.uc = UpdateChess(self.ai_settings, self.screen, self.chessboard)
        self.create_butt = CreateButton(self.screen, self.uc)

    def wait_destribute(self):
        """
            等待分配房间和先手棋
        """
        chess_color, self.adverse = self.manager.wait_destribute()
        self.uc.add_color(chess_color)
        self.create_butt.mv_wait_button(chess_color, self.adverse)
        self.create_butt.update_countdown_button(self)
        # sleep(2)

    def update_by_recv(self):
        """
            接受对方走棋，更新棋盘
        """
        while self.create_butt.game_is_alive:
            data = self.manager.opposite_outplay()
            if data[0] == "P":
                self.uc.add_oppose_chess(data[1])
                if self.create_butt.own_regret_count > 0:
                    self.create_butt.remove_regret_button()
            elif data[0] == "O":
                self.do_end_status(data[1])
                break
            elif data[0] == "C":
                self.do_opponent_regret(data[1])
            elif data[0] == "A":
                self.do_opponent_agree(data[1])
            elif data[0] == "D":
                self.do_opponent_disagree()
            elif data[0] == "G":
                break

    def do_end_status(self, status):
        """
            处理结束状态
        """
        is_quit = self.get_end_remind(status)
        self.create_butt.game_is_alive = False
        if is_quit:
            sleep(2)
        else:
            over_list = self.manager.get_stop_position()
            self.uc.game_over(over_list)
            sleep(2)
        self.uc.do_end_status()
        self.create_butt.add_start_button()

    def get_end_remind(self, status):
        """
            结束提醒按钮
        :param status:
        :return:
        """
        self.create_butt.get_end_remind(status)
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
        self.uc.update_screen(self.ai_settings, self.chessboard, self.create_butt.list_button)

    def do_gove_up(self):
        self.create_butt.game_is_alive = False
        self.uc.can_discard = False
        self.create_butt.regret_time = -1
        self.uc.do_end_status()
        self.manager.gave_up()
        self.create_butt.add_start_button()
        sleep(0.1)
        self.create_butt.regret_time = 8

    def do_quit(self):
        self.manager.quit()
        self.create_butt.game_is_alive = False
        self.create_butt.add_start_button()

    def do_own_regret(self):
        self.manager.regret()
        self.uc.can_regret = False
        self.create_butt.remove_regret_button()
        self.create_butt.do_add_own_regret_button()

    def do_opponent_regret(self, position):
        self.position = position
        self.create_butt.get_opponent_regret_button()

    def agree(self):
        self.manager.agree()
        self.create_butt.regret_time = -1
        self.uc.do_agree(self.position)

    def do_opponent_agree(self, position):
        self.create_butt.regret_time = -1
        self.create_butt.own_regret_count -= 1
        self.create_butt.get_regret_button()
        self.uc.do_opponent_agree(position)

    def do_opponent_disagree(self):
        self.create_butt.regret_time = -1

    def disagree(self):
        self.create_butt.regret_time = -1
        self.manager.disagree()


if __name__ == '__main__':
    g = GameView()
    g.run_game()
