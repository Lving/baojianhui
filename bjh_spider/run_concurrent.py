# -*- coding: utf-8 -*-
# 类中加上线程名
# 让log 更加的丰富 线程+时间
import concurrent.futures


from baojianhui_spider_concurrent import BaoJianHui
from bjh_numbers_enumerate import PipeLine, BjhNumber

THREADS_NUM = 5
THREADS_POOL = []  # 线程, 存放并行处理的对象
ready_queue = []  # 待处理队列 临时

mysql = PipeLine()

bjh_nums = BjhNumber(area_code='130000', start_year=2014, end_year=2015)
# fire up
bjh_nums.check_record()

# 并行处理的对象放入线程池
for j in range(THREADS_NUM):
    bjh = BaoJianHui(captchas_file='captchas_%s' % (j+1,), proxies_enable=True, thread_name='Thread-%s' % (j+1, ))
    THREADS_POOL.append(bjh)

# https://docs.python.org/3/library/concurrent.futures.html
for num in bjh_nums:

    ready_queue.append(num)

    if len(ready_queue) == THREADS_NUM:
        with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS_NUM) as executor:
            future_to_num = {
                executor.submit(THREADS_POOL[i].query, ready_queue[i]): ready_queue[i] for i in range(THREADS_NUM)
            }

            for future in concurrent.futures.as_completed(future_to_num):
                data = future.result()
                if data:
                    print('processing result from: %s' % future_to_num[future])
                    mysql.process_dict(data)

                    bjh_nums.find_one()
                else:
                    print('%s dropped' % future_to_num[future])

        ready_queue = []  # 待处理列表清空











