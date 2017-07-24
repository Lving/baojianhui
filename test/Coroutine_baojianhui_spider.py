# -*- coding: utf-8 -*-
# http://iir.circ.gov.cn/web/

import requests
import time
from PIL import Image
import pytesseract
from lxml.etree import HTML
import redis

PATH = "D:\\Code\\4_保监会\\captchas\\"


def __get_cookie(sess):
    ts = int(time.time())
    val_url = 'http://iir.circ.gov.cn/web/servlet/ValidateCode?time={}'.format(ts)
    headers = {
        'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Accept-Language': 'zh-CN'}

    cookie_file = PATH + str(ts) + '.jpg'

    r = sess.get(val_url, headers=headers)

    with open(cookie_file, 'wb') as f:
        f.write(r.content)
    # 构造cookie
    # cookies = {}
    # cookies['UM_distinctid'] = '15ca5bfc8f564f-0365860665670f8-51a2f73-100200-15ca5bfc8f658a'
    # cookies['CNZZDATA1619462'] = 'cnzz_eid%3D2119936732-1497429142-%26ntime%3D1497511531'
    # for i in r.cookies:
    #     cookies[i.name] = i.value
    return r.cookies, cookie_file


def __captcha_recognition(img_name):
    # 不down下来能不能识别到验证码
    time.sleep(0.1)
    img = Image.open(img_name)
    width, height = img.size
    box = (2, 2, width - 2, height - 2)
    new_img = img.crop(box)
    new_img = new_img.convert('L')
    gray_img = new_img.point(lambda i: 0 if i < 140 else 255)
    # gray_img.show()
    # gray_img.save('gray_' + img_name)
    config = '-psm 7'  # 声明只有一行内容
    captcha = pytesseract.image_to_string(gray_img, config=config)
    return captcha


def __parse():
    # consumer
    while True:
        content = yield
        tree = HTML(content)
        key = ['name', 'gender', 'certificate_No', 'certificate_Status', 'Practise_No', 'Practise_Status',
               'Expiration', 'Business_Domain', 'Practise_Area', 'Company']
        trs = tree.xpath('/html/body/table[2]/tr/td//li[2]//tr//td')
        detail = [i.xpath('text()')[0] for i in trs]
        if len(detail) == len(key):
            print(dict(zip(key, detail)))  # 或者其他入库的操作
        else:
            print('not matched')


def query(sess, con):
    """
    :param sess:  会话
    :param con: 消费者对象
    :return:
    """
    # producee
    next(con)  # fire up
    red = redis.Redis(host='10.8.15.30', port=7000, db=1)
    while True:
        cookies, cookies_file = __get_cookie(sess)
        captcha = __captcha_recognition(cookies_file)
        num_string = red.spop('baojianhui').decode()
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
        url = 'http://iir.circ.gov.cn/web/baoxyx!searchInfoBaoxyx.html?certificate_code={}&evelop_code=&name=&valCode={}'.format(
            num_string, captcha)
        try:
            r = sess.get(url, cookies=cookies, headers=headers, timeout=15)
        except Exception as e:
            print(e)
        else:
            con.send(r.text)


if __name__ == '__main__':
    sess = requests.session()
    con = __parse()
    query(sess, con)


