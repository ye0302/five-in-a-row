from server.logic.model import Location


class GameCoreController:
    """
        负责处理游戏的核心逻辑
    """

    def __init__(self):
        self.__map = [
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
        self.list_same_location = []

    @property
    def map(self):
        return self.__map

    def __get_same_point(self):
        '''
            将可消去元素的坐标加入列表
        '''
        for i in range(-1, 2):
            self.get_row_same_point(lambda r, c: Location(r, c), i)
            self.get_column_same_point(lambda r, c: Location(c, r), i)
            if self.list_same_location:
                return
        self.get_column_same_point(lambda r, c: Location(c, r),0)

    def map_write(self, point, value):
        position = eval(point)
        self.__map[position.index_r][position.index_c] = value
        self.__get_same_point()

    def get_column_same_point(self, func,N):
        '''
            统计列相邻元素相同的个数，将超过5个相连相同元素的坐标加入列表
        '''
        self.__square_matrix_transpose()
        self.get_row_same_point(func,N)
        self.__square_matrix_transpose()

    def __square_matrix_transpose(self):
        '''
            矩阵转置
        :param list_target:需要转置的方阵
        '''
        for r in range(1, len(self.__map)):
            for c in range(r):
                self.__map[r][c], self.__map[c][r] = self.__map[c][r], self.__map[r][c]

    def get_row_same_point(self, func, N):

        '''
            统计行向相邻元素相同的个数，将超过5个相连相同元素的坐标加入列表
        '''
        for r in range(len(self.__map)):
            count = 1
            for c in range(len(self.__map[0]) - 1):
                r -= N
                if r < 0 or r > len(self.__map):
                    break
                if self.__map[r + N][c] == 0:
                    count = 1
                    continue
                if self.__map[r + N][c] == self.__map[r][c + 1]:
                    count += 1
                    if count == 5:
                        for i in range(- 3, 2):
                            self.list_same_location.append(func(r - i * N + N, c + i))
                else:
                    count = 1


if __name__ == '__main__':

    m = GameCoreController()
    m.__get_same_point()
    for item in m.list_same_location:
        print(item.index_r, item.index_c)
