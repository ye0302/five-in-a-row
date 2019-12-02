class UserModel:
    def __init__(self, name="", password="", qq_number=0, win_count=0, lose_count=0):
        self.name = name
        self.qq_number = qq_number
        self.password = password
        self.win_count = win_count
        self.lose_count = lose_count

    def __repr__(self):
        return "UserModel('%s','%s','%s',%s,%s)" % (self.name, self.password,
                                                self.qq_number, self.win_count, self.lose_count)
