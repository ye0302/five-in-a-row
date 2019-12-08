import json
import re
import sys
from socket import *

sys.path.append("/home/tarena/zhixuda/aid1909/my_project")
from client.model import Location
from client.user_model import UserModel


class ClientCoreController:
    def __init__(self):
        self.__sockfd = socket()
        self.__addr = ("176.5.17.203", 9876)
        self.__user = None
        self.__sockfd.connect(self.__addr)

    def do_login_or_register(self, user):
        """
            登录注册
        """
        if user.qq_number:
            self.__sockfd.send(("S %s" % user.__repr__()).encode())
        else:
            self.__sockfd.send(("L %s" % user.__repr__()).encode())
        data = self.__sockfd.recv(128).decode()
        if data == "OK":
            self.__user = user
            msg = self.__sockfd.recv(128).decode()
            msg = json.loads(msg)
            self.__sockfd.send(b"")
            return data, tuple(msg)
        return data

    def join_game(self):
        self.__sockfd.send(b"J ")

    def wait_destribute(self):
        """
            等待分配对手
        """
        while True:
            data = self.__sockfd.recv(1024).decode()
            if not data:
                break
            data = data.split(" ", 2)
            if data[0] == "B":  # begin
                return int(data[1]), eval(data[2])

    def outplay(self, index_x, index_y):
        """
            将位置对象赋值，并发送服务器
        :param point: 位置对象
        :return: 如果成功返回True
        """
        point = Location(index_x, index_y)
        self.__sockfd.send(("P %s" % point.__repr__()).encode())

    def opposite_outplay(self):
        """
            接收客户端，如果对手走棋，将棋子位置赋值,如果对手悔棋，返回信息
        :return:
        """
        data = self.__sockfd.recv(1024).decode()
        if not data:
            sys.exit("结束服务")
        data = data.split(" ")
        if data[0] in "PAC":
            position = eval(data[1])
            return (data[0], (position.index_r, position.index_c))
        # if data[0] == "P":  # 对方走子
        #     position = eval(data[1])
        #     return ("P", (position.index_r, position.index_c))
        # elif data[0] == "A":  # 悔棋时棋子还原
        #     position = eval(data[1])
        #     return ("A", (position.index_r, position.index_c))
        # elif data[0] == "C":  # 对方申请悔棋
        #     position = eval(data[1])
        #     return ("C", (position.index_r, position.index_c))
        if data[0] == "O":  # 结束
            return ("O", data[1])
        if data[0] in "DG":
            return data[0]
        # if data[0] == "D":  # 对方不同意悔棋
        #     return "D"
        # if data[0] == "G":
        #     return "G"

    def get_stop_position(self):
        data = self.__sockfd.recv(1024).decode()
        return [(eval(item).index_r, eval(item).index_c) for item in data.split(" ")]

    def quit(self):
        self.__sockfd.send(b"Q")

    def gave_up(self):
        self.__sockfd.send(b"G ")

    def regret(self):
        self.__sockfd.send(b"C ")

    def agree(self):
        self.__sockfd.send(b"A ")

    def disagree(self):
        self.__sockfd.send(b"D ")

    def response(self, choise):
        if choise == "y":
            self.__sockfd.send(b"YES")
        else:
            self.__sockfd.send(b"NO")


if __name__ == '__main__':
    c = ClientCoreController()
    # c.mian()
