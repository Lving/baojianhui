# -*- coding: utf-8 -*-
# rule test

# 证书类型： 00
# 给定年份: 2010
# 月份： 1-12
# 区域：130000
# 流水：00001-00100
# 校验码：0-9
import logging
import os
import pickle
from collections import deque
import time

import pymysql

from baojianhui_spider import BaoJianHui

bjh = BaoJianHui(proxies_enable=True)


class LengthError(Exception):
    def __init__(self):
        self.info = 'length of number is not correct'

    def __str__(self):
        return self.info


class PipeLine(object):
    def __init__(self):
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='dafy', charset='utf8')
        self.cur = self.conn.cursor()

    def process_dict(self, dict):
        table_name = 'baojianhui'
        col_str = ''
        row_str = ''
        # sql = "INSERT INTO {} ({}) VALUES ({})"
        for key in dict.keys():
            col_str = col_str + " " + key + ","
            row_str = "{}'{}',".format(row_str, dict[key])
        sql = "INSERT INTO {} ({}) VALUES ({})".format(table_name, col_str[1:-1], row_str[:-1])
        self.cur.execute(sql)
        self.conn.commit()

    def __del__(self):
        self.conn.close()


class BjhNumber(object):

    def __init__(self, area_code, start_year, end_year,
                 start_month=1, end_month=12, serial=1):
        """
        搜索的范围
        :param area_code: 行政区域码
        :param start_year: 起始年
        :param end_year:
        :param start_month: 起始月
        :param end_month:
        :param serial: 流水号
        """
        self.area_code = area_code
        self.start_year = start_year
        self.end_year = end_year
        self.start_month = start_month
        self.end_month = end_month
        self.serial = serial
        self.check_code = 0

        self.record_file = 'baojianhui_record.pickle'  # 记录的文件
        self.records = deque(maxlen=10)  #

    def __str__(self):
        return '00%s%02d%s%05d%s' % (self.start_year, self.start_month, self.area_code, self.serial, self.check_code)

    def check_record(self):
        """
        fire up
        检查运行记录，获取年，月，区域等信息
        没有， 使用默认
        将records与对象绑定，覆盖初始的记录
        第一次运行不用调用此方法， 暂停后需要调用此方法
        :return:
        """
        # if not os.path.exists(self.record_file):
        #     self.records = deque(maxlen=10)
        #     with open(self.record_file, 'wb') as f:
        #         pickle.dump(self.records, f)

        if os.path.exists(self.record_file):
            with open(self.record_file, 'rb') as f:
                self.records = pickle.load(f)

            last_run = self.records[-1]
            print(last_run)

            self.start_year = int(self.get_year(last_run))
            self.start_month = int(self.get_month(last_run))
            self.serial = int(self.get_serial(last_run))
            self.check_code = int(self.get_checkcode(last_run))

    def __iter__(self):
        return self

    def __next__(self):
        self.check_code += 1
        # todo: 出错的原因在于， 如果上次的checkcode为9的话，这里加1， 就出了问题
        #  写入deque, 并将deque记录下来

        if self.check_code > 9:
            self.serial += 1
            self.check_code = 0

            if self.serial > 99:
                self.start_month += 1
                self.serial = 0

                if self.start_month > 12:
                    self.start_year += 1
                    self.start_month = 1

                    if self.start_year > self.end_year:
                        raise StopIteration

        num = '00%s%02d%s%05d%s' % (self.start_year, self.start_month, self.area_code, self.serial, self.check_code)
        self.records.append(num)
        with open(self.record_file, 'wb') as f:
            pickle.dump(self.records, f)

        return '00%s%02d%s%05d%s' % (self.start_year, self.start_month, self.area_code, self.serial, self.check_code)

    def is_correct(self, bjh_number):
        if len(bjh_number) == 20:
            return True
        return False

    def get_year(self, bjh_number):
        if self.is_correct(bjh_number):
            return bjh_number[2:6]
        else:
            raise LengthError

    def get_month(self, bjh_number):
        if self.is_correct(bjh_number):
            return bjh_number[6:8]
        raise LengthError

    def get_areacode(self, bjh_number):
        if self.is_correct(bjh_number):
            return bjh_number[8:14]
        raise LengthError

    def get_serial(self, bjh_number):
        if self.is_correct(bjh_number):
            return bjh_number[14:19]
        raise LengthError

    def get_checkcode(self, bjh_number):
        if self.is_correct(bjh_number):
            return bjh_number[-1]
        raise LengthError



if __name__ == '__main__':
    bjh_number = BjhNumber(area_code='130000', start_year=2014,
                           end_year=2015)
    bjh_number.check_record()
    for i in bjh_number:
        print(i)
        time.sleep(0.3)




# def test():
#     for num in range(20, 30):
#         for cer in range(10):
#             number = '00201409130000%05d%s' % (num, cer)
#             print(number)
#             b = bjh.query(number)
#             if not b:
#                 print('not not existed')
#             else:
#                 print(b)


# dic = {'name': '荣星', 'gender': '女', 'certificate_No': '00201409130000000235',
#        'certificate_Status': '有效', 'Practise_No': '02000613020080002014022352',
#        'Practise_Status': '有效', 'Expiration': '2017-10-07', 'Business_Domain': '人身保险',
#        'Practise_Area': '河北省', 'Company': '泰康人寿保险股份有限公司唐山中心支公司'}
# print(process_dict(dic))


# 002010 12 410100000017  终于找到了这个 流水号1
# 002014 01 130000000011
# 002014 07 130000000022
# 以上两条基本推翻了 假设1
# 每月的流水号从0开始计数的话， 1月份理论上应该有2这个流水号
# 一月人少 看下9月份 有没有连续的流水号
# 00201409130000000018
# 00201409130000000059
# 00201409130000000083
# 00201409130000000155
# 00201409130000000180
# 00201401130000000011
# 002014011300000000710


# area_code = ['130100', '130200','130300', '130400','130500', '130600','130700', '130800','130900', '131000','131100']
# for num in area_code:
#     for cer in range(10):
#         number = '00201409%s00003%s' % (num, cer)
#         print(number)
#         try:
#             bjh.run(number)
#         except Exception as e:
#             print(e)



# 002014 02 130000 00003 3
# 002014 04 130000 00003 2