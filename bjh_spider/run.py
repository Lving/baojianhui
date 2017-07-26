# -*- coding: utf-8 -*-
import time

from baojianhui_spider import BaoJianHui
from bjh_numbers_enumerate import PipeLine, BjhNumber


spider = BaoJianHui(proxies_enable=True)
mysql = PipeLine()
bjh_ids = BjhNumber(area_code='130000', start_year=2014, end_year=2015)

# fire up
bjh_ids.check_record()

for num in bjh_ids:
    res = spider.query(num)
    print('result from %s: %s' % (num, res))
    if res:

        print('processing result from: %s' % num)
        mysql.process_dict(res)

        bjh_ids.find_one()  # 找到正确的号码， serial+1， 校验码清零。

    else:
        print('%s dropped' % num)
    # print(num)
    # time.sleep(0.3)
