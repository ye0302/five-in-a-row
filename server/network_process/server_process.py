import ctypes
import inspect
import json
import os
import random
from multiprocessing import Process, Queue, Value
from select import *
from signal import *
from socket import *
from threading import Thread
from time import sleep
from server.logic.dbmodel import DBModel
from server.logic.gobang import GameCoreController
from server.logic.model import Location
from server.network_process.user_model import UserModel

signal(SIGCHLD, SIG_IGN)


class GobandServer:
    def __init__(self, host, post):
        self.__addr = (host, post)
        self.__get_sockfd()
        self.__login_user = {}  # 用于记录登录的玩家
        self.__list_room_connfd = []  # 用于记录加入房间的人数，以及房间内玩家的通信
        self.__list_room_user = []  # 用于记录房间内玩家的分数等状态
        self.__list_username = []  # 用于记录登录玩家的姓名，防止再次登录
        self.__ep = epoll()
        self.__dict_user = {}
        self.__manager = GameCoreController()
        self.__user_previous_record = []
        self.dm = DBModel()

    def __get_sockfd(self):
        """
            创建设置监听套接字
        """
        self.__sockfd = socket()
        self.__sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.__sockfd.bind(self.__addr)
        self.__sockfd.listen(5)

    def main(self):
        self.__ep.register(self.__sockfd, EPOLLIN)
        self.__dict_user[self.__sockfd.fileno()] = self.__sockfd
        while True:
            try:
                events = self.__ep.poll()
            except KeyboardInterrupt:
                os._exit(1)
            for fd, event in events:
                if fd == self.__sockfd.fileno():
                    self.__accept_user_join()
                else:
                    self.headle_user_request(fd)

    def headle_user_request(self, fd):
        """
            处理用户请求
        :param fd:客户连接套接字的文件描述符
        """
        connfd = self.__dict_user[fd]
        data = self.__get_data(connfd)
        if not data:
            return
        self.__join_room(connfd, data)
        self.__handle_end_user(connfd, data)
        user = self.__login_or_register(connfd, data)
        if user:
            self.__login_user[connfd] = user
            self.__list_username.append(user.name)

    def __handle_end_user(self, connfd, data):
        """
            房间内用户玩完一局以后的状态处理
        :param data:
        :return:
        """
        if data[0] == "CH":
            if data[1] == "1":
                self.__ep.register(int(data[2]), EPOLLIN)
                user = eval(data[3])
                self.__login_user[self.__dict_user[int(data[2])]].win_count = user.win_count
                self.__login_user[self.__dict_user[int(data[2])]].lose_count = user.lose_count
            elif data[1] == "0":
                self.__delete_user(connfd, data)

    def __delete_user(self, connfd, data):
        if len(data) == 2:
            del self.__dict_user[connfd.fileno()]
            return
        self.__list_username.remove(self.__login_user[self.__dict_user[int(data[2])]].name)
        del self.__login_user[self.__dict_user[int(data[2])]]
        del self.__dict_user[int(data[2])]

    def __join_room(self, connfd, data):
        if data[0] == "J":
            self.__list_room_connfd.append(connfd)
            self.__list_room_user.append(self.__login_user[connfd])
            if len(self.__list_room_connfd) == 2:
                self.__create_room()

    def __get_data(self, connfd):
        data = connfd.recv(1024)
        if not data:
            self.do_user_disconnect(connfd)
            return
        data = (data.decode()).split(" ")
        return data

    def do_user_disconnect(self, connfd):
        """
            处理用户掉线
        :param connfd:
        :return:
        """
        self.__ep.unregister(connfd)
        if connfd in self.__list_room_connfd:
            self.__list_room_connfd.remove(connfd)
            self.__list_room_user.remove(self.__login_user[connfd])
        if connfd in self.__login_user:
            self.__list_username.remove(self.__login_user[connfd].name)
            del self.__login_user[connfd]
        del self.__dict_user[connfd.fileno()]
        connfd.close()

    def __accept_user_join(self):
        """
            接收用户连接
        """
        c, addr = self.__sockfd.accept()
        self.__ep.register(c, EPOLLIN)
        self.__dict_user[c.fileno()] = c

    def __login_or_register(self, c, data):
        """
            处理用户登录、注册
        :param c: 客户端链接套接字
        :return: 登记或注册成功返回True
        """
        if data[0] == "L":
            return self.__login(c, data)
        if data[0] == "S":
            return self.__register(c, data)

    def __register(self, c, data):
        """
            处理用户注册
        :param c: 客户端链接套接字
        :param data: 用户对象格式的字符串
        :return: 注册成功返回True
        """
        user = eval(data[1])
        result = self.dm.register(user.name, user.password, user.qq_number)
        if not result:
            c.send(b"OK")
            sleep(0.1)
            data = json.dumps((0, 0))
            c.send(data.encode())
            return user
        c.send(result)

    def __login(self, c, data):
        """
            处理用户登录
        :param c: 客户端链接套接字
        :param data: 用户对象格式的字符串
        :return: 登录成功返回True
        """
        user = eval(data[1])
        if user.name in self.__list_username:
            c.send(b"AL")
            return
        result = self.dm.login(user.name, user.password)
        if result[0] == "OK":
            c.send(b"OK")
            sleep(0.1)
            user.win_count = result[1][0]
            user.lose_count = result[1][1]
            data = json.dumps(result[1])
            c.send(data.encode())
            return user
        c.send(result)

    def __create_room(self):
        """
            为两位玩家分配房间
        :return:
        """
        for item in self.__list_room_connfd:
            self.__ep.unregister(item)
        p = Process(target=self.__do_play)
        p.start()
        self.__list_room_connfd.clear()
        self.__list_room_user.clear()

    def __do_play(self):
        """
            进行游戏
        """
        self.__create_s_communicate_mian_process()
        choise_first, other = self.__destribute_chess_color()
        ep = epoll()
        for use in self.__list_room_connfd:
            ep.register(use, EPOLLIN)
        while True:
            try:
                events = ep.poll()
            except KeyboardInterrupt:
                os._exit(1)
            for fd, event in events:
                if self.__list_room_connfd[0].fileno() == fd:
                    self.__handle(choise_first, 0, ep)
                elif self.__list_room_connfd[1].fileno() == fd:
                    self.__handle(other, 1, ep)

    def __destribute_chess_color(self):
        """
            分配先手
        :return: int：用户1,2棋子颜色对应的数字
        """
        choise_first = random.randint(1, 2)
        other = 3 - choise_first
        self.__list_room_connfd[0].send(("B %s %s" % (choise_first, self.__list_room_user[1].__repr__())).encode())
        self.__list_room_connfd[1].send(("B %s %s" % (other, self.__list_room_user[0].__repr__())).encode())
        print("分配先手")
        return choise_first, other

    def __handle(self, value, index, ep):
        """
            根据用户信息处理走棋，悔棋，退出和游戏结束逻辑
        :param value: 走棋者棋子颜色对应的数字
        :param index: 走棋者索引
        :param ep: epoll对象
        """
        data = self.__list_room_connfd[index].recv(1024)
        if not data:
            self.__quit(index)
        msg = (data.decode()).split(" ")
        if msg[0] == "P":
            self.__discard(data, index, msg, value)
        if msg[0] == "G":
            self.__do_give_up(index)

    def __discard(self, data, index, msg, value):
        """
            用户走棋
        :param data: 用户发送经转发内容
        :param index:走棋者索引
        :param msg: 走棋位置
        :param value: 走棋者棋子颜色对应的数字
        """
        self.__user_previous_record.append(msg[1])
        self.__list_room_connfd[index - 1].send(data)
        self.__manager.map_write(msg[1], value)
        if self.__manager.list_same_location:
            self.__is_game_over(index)
            os._exit(1)

    def __is_game_over(self, index):
        """
            一方赢棋，游戏结束逻辑处理
        :param data: 赢家最后一部棋子位置
        :param index: 赢家的索引
        """
        print("游戏结束")
        sleep(0.1)
        self.__list_room_connfd[index].send(b"O WIN")
        self.__list_room_connfd[index - 1].send(b"O LOSE")
        self.__update_score(index)
        self.__send_over_position()
        self.__back_login_status([1, 1])

    def __send_over_position(self):
        """
            获取结束位置，并发送到客户端
        """
        sleep(0.1)
        end_position = [item.__repr__() for item in self.__manager.list_same_location]
        for item in self.__list_room_connfd:
            item.send(("%s %s %s %s %s" % tuple(end_position)).encode())

    def __update_score(self, index):
        """
            更新用户输、赢数据
        :param index: 赢者的索引
        """
        self.__list_room_user[index].win_count += 1
        self.__list_room_user[index - 1].lose_count += 1
        self.dm.update_score(self.__list_room_user[index].name, self.__list_room_user[index - 1].name)

    def __quit(self, index):
        self.__update_score(index - 1)
        self.__list_room_connfd[index - 1].send(b"O QWIN")
        status = [1, 1]
        status[index] = 0
        self.__back_login_status(status)
        os._exit(1)

    def __do_give_up(self, index):
        self.__update_score(index - 1)
        self.__list_room_connfd[index - 1].send(b"O QWIN")
        self.__back_login_status([1, 1])
        os._exit(1)

    def __create_s_communicate_mian_process(self):
        self.s = socket()
        self.s.connect(self.__addr)

    def __back_login_status(self, status):
        for i in range(2):
            self.s.send(("CH %d %s %s" % (
                status[i], self.__list_room_connfd[i].fileno(), self.__list_room_user[i].__repr__())).encode())
            sleep(0.1)
        self.s.send(b"CH 0")


if __name__ == '__main__':
    host = "0.0.0.0"
    post = 9876
    c = GobandServer(host, post)
    c.main()
