"""
    数据模型
"""


class Location:
    def __init__(self, index_r=None, index_c=None):
        '''
            将坐标进行封装
        :param index_r:行索引
        :param index_c:列索引
        '''
        self.index_r = index_r
        self.index_c = index_c

    def __repr__(self):
        return "Location(%d,%d)" % (self.index_r, self.index_c)
