# -*- coding: utf-8 -*-
import requests
import time
from PIL import Image
import pytesseract
# http://iir.circ.gov.cn/web/
from lxml.etree import HTML

class BaoJianHui(object):

    def __init__(self):
        # self.ts = int(time.time())
        self.sess = requests.session()
        # self.img_name = 'val.jpg'

    def get_cookie(self):
        val_url = 'http://iir.circ.gov.cn/web/servlet/ValidateCode?time={}'.format(self.ts)
        headers = {
            'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Accept-Language': 'zh-CN'
        }

        r = self.sess.get(val_url, headers=headers)

        ts = time.time()
        cookie_file = str(ts)+'.jpg'

        with open(cookie_file, 'wb') as f:
            f.write(r.content)

        # 构造cookie
        # cookies = {}
        # cookies['UM_distinctid'] = '15ca5bfc8f564f-0365860665670f8-51a2f73-100200-15ca5bfc8f658a'
        # cookies['CNZZDATA1619462'] = 'cnzz_eid%3D2119936732-1497429142-%26ntime%3D1497511531'
        #
        # for i in r.cookies:
        #     cookies[i.name] = i.value
        #
        # return cookies

        return r.cookies, cookie_file

    def captcha_recognition(self, img_name):
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

    def query(self, num_string):

        cookies, cookie_file = self.get_cookie()

        captcha = self.captcha_recognition(cookie_file)

        headers = {
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

        url = 'http://iir.circ.gov.cn/web/baoxyx!searchInfoBaoxyx.html?certificate_code={}&evelop_code=&name=&valCode={}'.format(num_string, captcha)

        r = self.sess.get(url, cookies=cookies, headers=headers)

        # todo：增加判断的条件， 对返回的内容进行判断

        # return r.text

        return self.parse(r.text)

    def parse(self, content):
        tree = HTML(content)


        # certificate_No: 资格证书号码
        # Practice_No: 执业证 编号
        key = ['name', 'gender', 'certificate_No', 'certificate_Status', 'Practise_No', 'Practise_Status',
               'Expiration', 'Business_Domain', 'Practise_Area', 'Company']

        trs = tree.xpath('/html/body/table[2]/tr/td//li[2]//tr//td')

        detail = [i.xpath('text()')[0] for i in trs]

        if len(detail) == len(key):
            return (dict(zip(key, detail)))
        return






bjh = BaoJianHui()
info1 = bjh.query('00201303140000011347')
info2 = bjh.query('00200903320800001748')
print(info1)
print(info2)







# # post的地址
# post_uri = 'http://iir.circ.gov.cn/web/validateCodeAction!ValidateCode.html'
#
# uri = 'http://iir.circ.gov.cn/web/baoxyx!searchInfoBaoxyx.html?certificate_code=00201312320800000075&evelop_code=&name=&valCode={}'
#
# ts = int(time.time())
#
# val_uri = 'http://iir.circ.gov.cn/web/servlet/ValidateCode?time={}'.format(ts)
# # 验证码地址
#
# headers1 = {
#     'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
#     'Accept-Encoding': 'gzip, deflate',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
#     'Accept-Language': 'zh-CN',
#
# }
#
#
# sess = requests.session()
# r = sess.get(val_uri, headers=headers1)
# with open('val.jpg', 'wb') as f:
#     f.write(r.content)
#
# cookies = {}
# for i in r.cookies:
#     cookies[i.name] = i.value
#
# cookies['UM_distinctid'] = '15ca5bfc8f564f-0365860665670f8-51a2f73-100200-15ca5bfc8f658a'
# cookies['CNZZDATA1619462'] = 'cnzz_eid%3D2119936732-1497429142-%26ntime%3D1497511531'
#
# print(cookies)
#
# val = input('val code:')
#
# data = {
#     'certificate_code': '00201404330100018078',
#     'evelop_code': '',
#     'valCode': val
# }
#
# data_val = {
#     'validateCode': val,
#     'dateTime': int(time.time())
# }
#
# headers2 = {
#     'Accept': '*/*',
#     'Accept-Encoding': 'gzip, deflate',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
#     'Accept-Language': 'zh-CN',
#     'Content-Type': 'application/x-www-form-urlencoded',
#     'Referer': 'http://iir.circ.gov.cn/web/',
#     'Connection': 'Keep-Alive',
#     'Host': 'iir.circ.gov.cn'
#     # 'certificate_code': '00201312320800000075',
#     # 'evelop_code': '',
#     # 'valCode': val
#
# }
# # 这里是对验证码进行验证， 可以去掉
# # rr = sess.post(post_uri, headers=headers1, data=data_val, cookies=cookies)
# # print(rr.text)
#
# # rrr = sess.post(uri, headers=headers, data=data, cookies=cookies)
# rrr = sess.get(uri.format(val), cookies=cookies, headers=headers2, data=data)
# print(rrr.text)


