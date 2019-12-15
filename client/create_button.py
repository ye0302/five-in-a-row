from threading import Thread
from time import sleep

from client.button import Board, ClickButton, RemindButton, RegretBoard


class CreateButton:
    def __init__(self, screen, uc):
        self.__screen = screen
        self.__uc = uc
        self.__own_win_score = None
        self.__adverse_win_score = None
        self.list_button = []
        self.game_is_alive = None
        self.own_regret_count = 3
        self.__create_circulate_button()
        self.click_button = [self.start_button, self.give_up_button, self.regret_button, self.quit_button]
        self.regret_click_button = []
        self.__time_button = None
        self.regret_time = 8

    def __create_circulate_button(self):
        self.get_start_button()
        self.get_wait_button()
        self.get_initial_time_button()
        self.get_give_up_button()
        self.get_regret_button()
        self.get_quit_button()
        self.get_cannot_click_regret_button()

    def get_initial_time_button(self):
        self.own_time_button = Board(self.__screen, 240, 740, "countdown: 45", (33, 226, 15))
        self.adverse_time_button = Board(self.__screen, 240, 60, "countdown: 45", (33, 226, 15))

    def create_adverse_scoreboard(self, adverse):
        """
            创建对手成绩对象
        :param adverse:
        :return:
        """
        self.__adverse_win_score = Board(self.__screen, 100, 40, "win: %s" % adverse.win_count)
        self.adverse_lose_score = Board(self.__screen, 100, 80, "lose: %s" % adverse.lose_count)

    def create_own_scoreboard(self, user):
        """
            创建自己成绩对象
        :param adverse:
        :return:
        """
        self.__own_win_score = Board(self.__screen, 390, 720, "win: %s" % user.win_count)
        self.own_lose_score = Board(self.__screen, 390, 755, "lose: %s" % user.lose_count)

    def get_start_button(self):
        self.screen_rect = self.__screen.get_rect()
        self.start_button = ClickButton(self.__screen, self.screen_rect.centerx, self.screen_rect.centery - 5, "Start")

    def get_remind_button(self, chess_color):
        """
            根据分配的棋子颜色创建体现按钮
        :param chess_color:
        """
        self.__uc.chess_color = chess_color
        self.__uc.opposent_chess_color = 3 - chess_color
        if chess_color == 1:
            self.__uc.can_discard = True
            self.color_button = RemindButton(self.__screen, "Black discover")
        else:
            self.color_button = RemindButton(self.__screen, "White chess")

    def get_wait_button(self):
        self.wait_button = RemindButton(self.__screen, "Waiting room")

    def get_end_remind(self, status):
        if status == "LOSE":
            self.ending_button = RemindButton(self.__screen, "You lost")
        else:
            self.ending_button = RemindButton(self.__screen, "You win")
        self.list_button.append(self.ending_button)


    def get_give_up_button(self):
        self.give_up_button = ClickButton(self.__screen, 90, 760, "Give up", (128, 128, 128))

    def get_regret_button(self):
        self.regret_button = ClickButton(self.__screen, 90, 720, "Regret %d" % self.own_regret_count,
                                         (255, 136, 20))

    def get_cannot_click_regret_button(self):
        self.cannot_click_regret_button = ClickButton(self.__screen, 90, 720, "Regret", (128, 128, 128))

    def update_countdown_button(self, manager):
        t = Thread(target=self.countdown, args=(manager,))
        t.setDaemon(True)
        t.start()

    def countdown(self, manager):
        while self.__uc.time >= 0 and self.game_is_alive:
            if self.color_button in self.list_button and self.__uc.time<=45:
                self.list_button.remove(self.color_button)
            if self.regret_time == 8:
                if self.__time_button in self.list_button:
                    self.list_button.remove(self.__time_button)  #
                self.get_nowtime_button()
                if self.__time_button:
                    self.list_button.append(self.__time_button)
                self.__uc.time -= 1
            sleep(1)
        if self.__uc.can_discard and self.__uc.time < 0:
            self.do_over_time(manager)

    def get_nowtime_button(self):
        if self.__uc.time <= 45:
            if self.__uc.can_discard:
                if self.own_time_button in self.list_button:
                    self.list_button.remove(self.own_time_button)
                if self.adverse_time_button not in self.list_button:
                    self.list_button.append(self.adverse_time_button)
                self.__time_button = Board(self.__screen, 240, 740, "countdown: %d" % self.__uc.time, (33, 226, 15))
            else:
                if self.adverse_time_button in self.list_button:
                    self.list_button.remove(self.adverse_time_button)
                if self.own_time_button not in self.list_button:
                    self.list_button.append(self.own_time_button)
                self.__time_button = Board(self.__screen, 240, 60, "countdown: %d" % self.__uc.time, (33, 226, 15))

    def add_start_button(self):
        self.list_button.clear()
        self.list_button.append(self.start_button)

    def mv_start_button(self, user):
        if self.start_button in self.list_button:
            self.list_button.remove(self.start_button)
        self.add_wait_button(user)

    def add_wait_button(self, user):
        """
            添加等待标签并更新成绩
        """
        self.list_button.append(self.wait_button)
        self.list_button.append(self.quit_button)
        self.update_own_score(user)

    def update_own_score(self, user):
        if self.__own_win_score in self.list_button:
            self.list_button.remove(self.__own_win_score)
            self.list_button.remove(self.own_lose_score)
        self.create_own_scoreboard(user)
        self.list_button.append(self.__own_win_score)
        self.list_button.append(self.own_lose_score)

    def mv_wait_button(self, color, user):
        """
            移除等待标签并添加对方成绩，悔棋，认输，倒计时按钮
        :param list_button:
        :param color:
        :return:
        """
        self.list_button.remove(self.wait_button)
        self.list_button.remove(self.quit_button)
        self.get_remind_button(color)
        self.list_button.append(self.color_button)
        self.update_adverse_score(user)
        self.list_button.append(self.give_up_button)
        self.list_button.append(self.cannot_click_regret_button)



    def update_adverse_score(self, user):
        if self.__adverse_win_score in self.list_button:
            self.list_button.remove(self.__adverse_win_score)
            self.list_button.remove(self.adverse_lose_score)
        self.create_adverse_scoreboard(user)
        self.list_button.append(self.__adverse_win_score)
        self.list_button.append(self.adverse_lose_score)

    def do_over_time(self, manager):
        self.overtime_button = RemindButton(self.__screen, "Over time", 30)
        self.ending_button = RemindButton(self.__screen, "You lost", -30)
        self.list_button.append(self.overtime_button)
        self.list_button.append(self.ending_button)
        manager.do_gove_up()
        sleep(2)
        self.list_button.remove(self.overtime_button)
        self.list_button.remove(self.ending_button)

    def do_add_own_regret_button(self):
        t = Thread(target=self.get_own_regret_button)
        t.start()

    def get_own_regret_button(self):
        self.own_regret_button = RegretBoard(self.__screen, "Waiting for agree...", 80)
        self.list_button.append(self.own_regret_button)
        while self.regret_time >= 0:
            self.regret_time -= 1
            sleep(1)
        self.list_button.remove(self.own_regret_button)
        self.regret_time = 8

    def do_add_opponent_regret_button(self):
        t = Thread(target=self.get_opponent_regret_button)
        t.start()

    def get_opponent_regret_button(self):
        self.opponent_regret_button = RegretBoard(self.__screen, "opponent asks for regret", 200, 50)
        self.list_button.append(self.opponent_regret_button)
        self.agree_button = ClickButton(self.__screen, 350, 450, "Agree", (0, 255, 255))
        self.regret_click_button.append(self.agree_button)
        self.list_button.append(self.agree_button)
        self.get_disagree_button()
        self.regret_click_button.clear()
        self.list_button.remove(self.disagree_button)
        self.list_button.remove(self.agree_button)
        self.list_button.remove(self.opponent_regret_button)
        self.regret_time = 8

    def get_disagree_button(self):
        while self.regret_time >= 0:
            if len(self.regret_click_button) == 2:
                self.regret_click_button.remove(self.disagree_button)
                self.list_button.remove(self.disagree_button)
            self.disagree_button = ClickButton(self.__screen, 200, 450,
                                               "Disagree(%d)" % self.regret_time, (255, 182, 221))
            self.list_button.append(self.disagree_button)
            self.regret_click_button.append(self.disagree_button)
            self.regret_time -= 1
            sleep(1)

    def get_quit_button(self):
        self.quit_button = ClickButton(self.__screen, 90, 760, "Quit", (128, 128, 128))

    def add_regret_button(self):
        if self.cannot_click_regret_button in self.list_button:
            self.list_button.remove(self.cannot_click_regret_button)
        self.list_button.append(self.regret_button)

    def remove_regret_button(self):
        if self.regret_button in self.list_button:
            self.list_button.remove(self.regret_button)
        self.list_button.append(self.cannot_click_regret_button)
