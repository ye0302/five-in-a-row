import pymysql


class DBModel:
    def __init__(self):
        self.db = pymysql.connect(user="root", password="123456", database="gobang", charset="utf8")
        self.cur = None

    def login(self, name, password):
        self.cur = self.db.cursor()
        sql = "select win_count,lose_count,password from users where name=%s"
        try:
            self.cur.execute(sql, [name])
        except Exception as e:
            print(e)
        result = self.cur.fetchone()
        self.cur.close()
        if not result:
            return b"F"
        if result[2] == password:
            return "OK", result[0:2]
        return b"PF"

    def register(self, name, passwd, qq_number):
        self.cur = self.db.cursor()
        sql = "select name from users where qq_number=%s union select name from users where name=%s"
        try:
            self.cur.execute(sql, [qq_number, name])
        except Exception as e:
            print(e)
        result = self.cur.fetchone()
        if not result:
            self.do_add_user(name, passwd, qq_number)
            self.cur.close()
            return
        self.cur.close()
        if result[0] == name:
            return b"NE"
        return b"QE"

    def do_add_user(self, name, passwd, qq_number):
        sql = "insert into users (name,qq_number,password) values (%s,%s,%s)"
        try:
            self.cur.execute(sql, [name, qq_number, passwd])
            self.db.commit()
            self.cur.close()
        except Exception as e:
            self.db.rollback()
            self.cur.close()
            print(e)

    def update_score(self, win_name, lose_name):
        self.cur = self.db.cursor()
        self.do_update("win_count", win_name)
        self.do_update("lose_count", lose_name)
        self.cur.close()

    def do_update(self, select_count, name):
        self.cur.execute("select %s from users where name= '%s'" % (select_count, name))
        count = self.cur.fetchone()[0] + 1
        sql = "update users set %s=%d where name= '%s'" % (select_count, count, name)
        try:
            self.cur.execute(sql)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(e)
