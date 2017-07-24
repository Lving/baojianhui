# -*- coding: utf-8 -*-
class BjhNumber(object):

    def __init__(self):
        """
        搜索的范围
        :param area_code: 行政区域码
        :param start_year: 起始年
        :param end_year:
        :param start_month: 起始月
        :param end_month:
        :param serial: 流水号
        """
        self.area_code = 130000
        self.start_year = 2016
        self.end_year = 2016
        self.start_month = 1
        self.end_month = 12
        self.serial = 1
        self.check_code = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.check_code += 1
        if self.check_code > 9:
            self.serial += 1
            self.check_code = 0

            if self.serial > 99:
                self.start_month += 1
                self.serial = 1

                if self.start_month > 12:
                    self.start_year += 1
                    self.start_month = 1

                    if self.start_year > 2017:
                        raise StopIteration

        return '00%s%02d%02d%s' % (self.start_year, self.start_month, self.serial, self.check_code)


import time
tt = BjhNumber()
for i in tt:
    time.sleep(0.7)
    print(i)