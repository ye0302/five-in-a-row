import sys
import tkinter as tk  # 使用Tkinter前需要先导入
import tkinter.messagebox

sys.path.append("/home/tarena/zhixuda/aid1909/my_project")
from client.user_model import UserModel
# from client.scoreboard import Scoreboard


class LoginAndRegister:
    def __init__(self, manegar):
        self.window = tk.Tk()
        self.window.title('欢乐五子棋')
        self.window.geometry('450x350+700+300')  # 这里的乘是小x
        self.__add_background()
        self.__add_label()
        self.__add_entry()
        self.manager = manegar
        self.user = UserModel()
        self.is_online = False

    def __add_entry(self):
        """
            添加用户登录的输入框
        """
        self.var_usr_name = tk.StringVar()
        entry_usr_name = tk.Entry(self.window, textvariable=self.var_usr_name, font=('arial', 14))
        entry_usr_name.place(x=130, y=180)
        self.var_usr_pwd = tk.StringVar()
        entry_usr_pwd = tk.Entry(self.window, textvariable=self.var_usr_pwd, font=('arial', 14), show='*')
        entry_usr_pwd.place(x=130, y=230)

    def __add_label(self):
        """
            设置标签
        """
        tk.Label(self.window, text='Welcome', font=('宋体', 16)).place(x=170, y=145)
        tk.Label(self.window, text='用户名:', font=('宋体', 14)).place(x=10, y=180)
        tk.Label(self.window, text='密码:', font=('宋体', 14)).place(x=10, y=230)

    def __add_background(self):
        """
            为初始窗口增加背景
        :return:
        """
        self.canvas = tk.Canvas(self.window, width=450, height=135, bg='green')
        self.image_file = tk.PhotoImage(file='./image/test.png')
        self.canvas.create_image(200, 0, anchor='n', image=self.image_file)
        self.canvas.pack(side='top')

    def usr_login(self):
        self.user.name = self.var_usr_name.get()
        self.user.password = self.var_usr_pwd.get()
        data = self.manager.do_login_or_register(self.user)
        if data == "F":
            self.do_unregister()
        elif data == "AL":
            tkinter.messagebox.showerror(message='该用户已登录')
        elif data[0] == "OK":
            self.do_succeed(data[1])
        else:
            tkinter.messagebox.showerror(message='密码错误,再试一次')

    def do_succeed(self, count):
        """
            注册成功处理
        :param count:
        """
        self.user.win_count = count[0]
        self.user.lose_count = count[1]
        self.window.destroy()
        self.is_online = True

    def do_unregister(self):
        """
            用户未注册处理
        """
        is_sign_up = tkinter.messagebox.askyesno('Welcome!', '你还没有注册,去注册?')
        if is_sign_up:
            self.usr_sign_up()

    def login_and_register(self):
        self.__create_button()  # login and sign up 按钮
        self.window.mainloop()  # 主窗口循环显示

    def click_login_entry(self, event):
        self.usr_login()

    def __create_button(self):
        """
            登录页面设置登录及注册按钮
        """
        btn_login = tk.Button(self.window, text='登录', command=self.usr_login)
        btn_login.place(x=120, y=290)
        self.window.bind("<Return>", self.click_login_entry)
        btn_sign_up = tk.Button(self.window, text='注册', command=self.usr_sign_up)
        btn_sign_up.place(x=250, y=290)

    def sign_to_Hongwei_Website(self):
        # 以下三行就是获取我们注册时所输入的信息
        self.user.name = self.list_value[0].get()
        self.user.qq_number = self.list_value[1].get()
        self.user.password = self.list_value[2].get()
        npf = self.list_value[3].get()
        if self.user.password != npf:
            tkinter.messagebox.showerror('Error', '密码输入不一致!')
        else:
            self.send_data_decide()

        # 定义长在窗口上的窗口

    def send_data_decide(self):
        """
            将用户信息发往服务器,并显示反馈
        :return:
        """
        data = self.manager.do_login_or_register(self.user)
        if data == "QE":
            tkinter.messagebox.showerror('Error', '用户已存在!')
        elif data == "NE":
            tkinter.messagebox.showerror('Error', '你的昵称太受欢迎了!')
        else:
            self.window_sign_up.destroy()
            self.window.destroy()
            self.is_online = True

    def usr_sign_up(self):
        self.window_sign_up = tk.Toplevel(self.window)
        self.window_sign_up.geometry('400x300+720+320')
        self.window_sign_up.title('注册窗口')
        self.create_register_label()

    def click_register_entry(self, event):
        self.sign_to_Hongwei_Website()

    def create_register_label(self):
        list_title = ['用户名: ', 'QQ号: ', '密码: ', '确认密码: ']
        self.list_value = []
        coordinate_label = [10, 10]
        coordinate_enter = [140, 10]
        distance = 50
        self.__get_enter_box(coordinate_enter, coordinate_label, distance, list_title, self.list_value,
                             self.window_sign_up)
        btn_comfirm_sign_up = tk.Button(self.window_sign_up, text='注册', command=self.sign_to_Hongwei_Website)
        self.window_sign_up.bind("<Return>", self.click_register_entry)
        btn_comfirm_sign_up.place(x=160, y=200)

    def __get_enter_box(self, coordinate_enter, coordinate_label, distance, list_title, list_value, window_sign_up):
        """
            创建注册输入框
        :param coordinate_enter:
        :param coordinate_label:
        :param distance:
        :param list_title:
        :param list_value:
        :param window_sign_up:
        """
        for i in range(len(list_title)):
            temp = tk.StringVar()
            tk.Label(window_sign_up, text=list_title[i]).place(x=coordinate_label[0], y=coordinate_label[1])
            tk.Entry(window_sign_up, textvariable=temp, show=[None, None, "*", "*"][i]).place(x=coordinate_enter[0],
                                                                                              y=coordinate_enter[1])
            list_value.append(temp)
            coordinate_label[1] += distance
            coordinate_enter[1] += distance
