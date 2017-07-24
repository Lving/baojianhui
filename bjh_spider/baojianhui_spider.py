# -*- coding: utf-8 -*-
import time
import logging

import requests
from PIL import Image
import pytesseract
from lxml.etree import HTML


class BaoJianHui(object):
    """
    保监会爬虫
    """
    # todo: retry 应该这里，两次请求的每次请求都应该有cookie， 所以retry 一次返回None的原因在此，第二次的session不一致
    # todo: logging
    RETRIES = 3

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

    def __init__(self, proxies_enable=False):
        self.proxies_enable = proxies_enable


    def requests_get(self, url, timeout=15, proxies=None, cookies=None, headers=None):
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
        # if proxies == None:
            try:
                return requests.get(url, timeout=timeout, cookies=cookies, headers=headers)
            except Exception as e:
                # print(e)
                logging.error(e)
                return

        else:
            try:
                return requests.get(url, timeout=timeout, proxies=self.PROXY, cookies=cookies, headers=headers)
            except Exception as e:
                # print(e)
                logging.error(e)
                return


    def get_cookie(self):
        """
        :return: cookie对象， 验证码图片文件名
        """
        ts = int(time.time())

        val_url = 'http://iir.circ.gov.cn/web/servlet/ValidateCode?time={}'.format(ts)

        cookie_file = 'D:\\Code\\4_保监会\\captchas\\'+str(ts)+'.jpg'

        r = self.requests_get(val_url, headers=self.captcha_headers)

        # r = requests.get(val_url, headers=headers, timeout=12)

        with open(cookie_file, 'wb') as f:
            f.write(r.content)
        # 构造cookie
        # cookies = {}
        # cookies['UM_distinctid'] = '15ca5bfc8f564f-0365860665670f8-51a2f73-100200-15ca5bfc8f658a'
        # cookies['CNZZDATA1619462'] = 'cnzz_eid%3D2119936732-1497429142-%26ntime%3D1497511531'
        # for i in r.cookies:
        #     cookies[i.name] = i.value
        # print(r.cookies)
        return r.cookies, cookie_file

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
            return (dict(zip(key, detail)))
        # print('html is not expected')
        logging.warning('html is not excepted')
        return None

    def query(self, num_string):

        """
        :param num_string:
        :return:
        """

        for retry in range(self.RETRIES):
            cookies, cookies_file = self.get_cookie()
            captcha = self.captcha_recognition(cookies_file)
            url = 'http://iir.circ.gov.cn/web/baoxyx!searchInfoBaoxyx.html?certificate_code={}&evelop_code=&name=&valCode={}'.format(num_string, captcha)

            # 请求不成功 requests_get 返回None
            r = self.requests_get(url, cookies=cookies, headers=self.query_headers)
            # r = requests.get(url, cookies=cookies, headers=self.query_headers, timeout=12)

            if r:
                return self.parse(r.text)
            else:
                # print('attempt retry: %s' % (retry+1, ))
                logging.warning('attempt retry : %s' % (retry+1, ))
        else:
            return None


        # return r.text
        # print(self.parse(r.text))


# test
if __name__ == '__main__':
    bjh = BaoJianHui(proxies_enable=True)
    a = bjh.query('00201409130000000018')
    print(a)



# bjh = BaoJianHui()
# info1 = bjh.query('00201303140000011347')
# info2 = bjh.query('00200903320800001748')
# print(info1)
# print(info2)



