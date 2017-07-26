# -*- coding: utf-8 -*-
# 多线程版本
import concurrent.futures
import os
import random
import time
import logging

import requests
import sys
from PIL import Image
import pytesseract
from lxml.etree import HTML


class BaoJianHui(object):
    """
    保监会爬虫
    """
    # todo: retry 应该这里，两次请求的每次请求都应该有cookie， 所以retry 一次返回None的原因在此，第二次的session不一致
    # todo: logging
    RETRIES = 5

    PROXY = {
        'http':'http://127.0.0.1:1080',
        'https':'http://127.0.0.1:1080'
    }

    # 获取验证码要带的headers
    captcha_headers = {
        'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Accept-Language': 'zh-CN'}

    # 接口查询时要带的headers
    query_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Accept-Language': 'zh-CN',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'http://iir.circ.gov.cn/web/',
        'Connection': 'Keep-Alive',
        'Host': 'iir.circ.gov.cn'
        # 'certificate_code': '00201312320800000075',
        # 'evelop_code': '',
        # 'valCode': val
    }

    def __init__(self, captchas_file='captchas', proxies_enable=False, thread_name=''):
        self.captchas_file = captchas_file+'\\'
        self.proxies_enable = proxies_enable
        self.thread_name = thread_name

    def random_user_agent(self):
        agents = [
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)',
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)',
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; WOW64; Trident/6.0)',
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)',
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; ARM; Trident/6.0)',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30;'
            ' .NET CLR 3.0.04506.648)',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; InfoPath.1',
            'Mozilla/4.0 (compatible; GoogleToolbar 5.0.2124.2070; Windows 6.0; MSIE 8.0.6001.18241)',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; EasyBits Go v1.0; InfoPath.1;'
            ' .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; '
            '.NET CLR 3.0.04506)'
        ]
        return random.choice(agents)

    def requests_get(self, url, timeout=15, cookies=None, headers=None):
        """
        :param url:
        :param timeout:
        :param proxies:
        :param retries:
        :param cookies:
        :param headers:
        :return: response 对象
        """
        if not self.proxies_enable:
            try:
                return requests.get(url, timeout=timeout, cookies=cookies, headers=headers)
            except Exception as e:
                # print(e)
                logging.error('{}: {}'.format(self.thread_name, e))
                return None

        else:
            try:
                return requests.get(url, timeout=timeout, proxies=self.PROXY, cookies=cookies, headers=headers)
            except Exception as e:
                # print(e)
                logging.error('{}: {}'.format(self.thread_name, e))
                return None

    def prepare_request(self):
        """
        :return: cookie对象， 验证码图片文件名
        """
        user_agent = self.random_user_agent()
        self.captcha_headers['User-Agent'] = user_agent

        ts = int(time.time())

        val_url = 'http://iir.circ.gov.cn/web/servlet/ValidateCode?time={}'.format(ts)

        current_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        cookie_file = os.path.join(current_path, self.captchas_file + str(ts) + '.jpg')

        r = self.requests_get(val_url, headers=self.captcha_headers)

        try:
            with open(cookie_file, 'wb') as f:
                f.write(r.content)
        except Exception as e:
            logging.error('{}: {}'.format(self.thread_name, e))

        return r.cookies, cookie_file, user_agent

    def captcha_recognition(self, img_name):
        """
        :param img_name: 验证码文件名
        :return: 识别的验证码
        """
        # 不down下来能不能识别到验证码
        time.sleep(0.1)
        img = Image.open(img_name)
        width, height = img.size
        box = (2, 2, width - 2, height - 2)
        new_img = img.crop(box)
        new_img = new_img.convert('L')
        gray_img = new_img.point(lambda i: 0 if i < 140 else 255)
        #gray_img.show()
        #gray_img.save('gray_' + img_name)
        config = '-psm 7'  # 声明只有一行内容
        captcha = pytesseract.image_to_string(gray_img, config=config)
        return captcha

    def parse(self, content):
        """
        html解析
        :param content:
        :return:
        """
        tree = HTML(content)
        # certificate_No: 资格证书号码
        # Practice_No: 执业证 编号
        key = ['name', 'gender', 'certificate_No', 'certificate_status', 'practise_No', 'practise_status',
               'expiration', 'business_domain', 'practise_area', 'company']

        trs = tree.xpath('/html/body/table[2]/tr/td//li[2]//tr//td')

        detail = [i.xpath('text()')[0] for i in trs]

        if len(detail) == len(key):
            return dict(zip(key, detail))
        # print('html is not expected')
        else:
            logging.warning('{}: {}'.format(self.thread_name, 'html is not excepted'))
            return None

    def query(self, num_string):

        """
        :param num_string:
        :return:
        """

        for retry in range(self.RETRIES):
            try:
                cookies, cookies_file, user_agent = self.prepare_request()
            except Exception as e:
                logging.error('{}:{}'.format(self.thread_name, e))
                continue

            try:
                captcha = self.captcha_recognition(cookies_file)
            except Exception as e:
                logging.error('{}: {}'.format(self.thread_name, e))
                continue

            self.query_headers['User-Agent'] = user_agent

            url = 'http://iir.circ.gov.cn/web/baoxyx!searchInfoBaoxyx.html?certificate_code={}&evelop_code=&name=&valCode={}'.format(num_string, captcha)
            # 请求不成功 requests_get 返回None
            # 非200的响应
            r = self.requests_get(url, cookies=cookies, headers=self.query_headers)
            # r = requests.get(url, cookies=cookies, headers=self.query_headers, timeout=12)
            # print(r.status_code)
            # print(r.text)

            if r and r.status_code == 200:  # 请求正确返回且状态码为200
                return self.parse(r.text)
            else:  # 请求出错或者状态码不正确
                time.sleep(10)
                logging.warning('{}: {}'.format(self.thread_name, 'attempt retry : %s' % (retry + 1,)))

        else:
            logging.warning('{}: {}'.format(self.thread_name, ' max retries'))
            return None


# test
if __name__ == '__main__':
    bjh1 = BaoJianHui(captchas_file='captchas1', proxies_enable=False, thread_name='Thread-1')
    bjh2 = BaoJianHui(captchas_file='captchas2', proxies_enable=False, thread_name='Thread-2')

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        a = executor.submit(bjh1.query, '00201409130000000018')
        b = executor.submit(bjh2.query, '00200903320800001648')

        print(a.result())
        print(b.result())





    # import os
    # import sys
    # print(sys.argv)
    # print(os.path.dirname(os.path.abspath(sys.argv[0])))
    # print(os.getcwd())




# bjh = BaoJianHui()
# info1 = bjh.query('00201303140000011347')
# info2 = bjh.query('00200903320800001748')
# print(info1)
# print(info2)



