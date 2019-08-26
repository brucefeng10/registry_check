
import json
import time
import requests

# from selenium import webdriver
# # from selenium.webdriver.common.keys import Keys
# from selenium.webdriver import ActionChains
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# from selenium.webdriver.common.keys import Keys
import time
# from bs4 import BeautifulSoup
# import pandas as pd
# import random
import os
import glob

######################################################################


class YDMHttp:

    apiurl = 'http://api.yundama.com/api.php'
    username = ''
    password = ''
    appid = ''
    appkey = ''

    def __init__(self, username, password, appid, appkey):
        self.username = username  
        self.password = password
        self.appid = str(appid)
        self.appkey = appkey

    def request(self, fields, files=[]):
        response = self.post_url(self.apiurl, fields, files)
        response = json.loads(response)
        return response
    
    def balance(self):
        data = {'method': 'balance', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey}
        response = self.request(data)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['balance']
        else:
            return -9001
    
    def login(self):
        data = {'method': 'login', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey}
        response = self.request(data)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['uid']
        else:
            return -9001

    def upload(self, filename, codetype, timeout):
        data = {'method': 'upload', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey, 'codetype': str(codetype), 'timeout': str(timeout)}
        file = {'file': filename}
        response = self.request(data, file)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['cid']
        else:
            return -9001

    def result(self, cid):
        data = {'method': 'result', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey, 'cid': str(cid)}
        response = self.request(data)
        return response and response['text'] or ''

    def decode(self, filename, codetype, timeout):
        cid = self.upload(filename, codetype, timeout)
        if (cid > 0):
            for i in range(0, timeout):
                result = self.result(cid)
                if (result != ''):
                    return cid, result
                else:
                    time.sleep(1)
            return -3003, ''
        else:
            return cid, ''

    def post_url(self, url, fields, files=[]):
        for key in files:
            files[key] = open(files[key], 'rb');
        res = requests.post(url, files=files, data=fields)
        return res.text

######################################################################

def get_api():

    username  = 'morris'
    password  = 'morris123'
    appid    = 7762                                     
    appkey   = '6fc83f42ecf5c8a4b43a0b8027b1dde0' 
    yundama = YDMHttp(username, password, appid, appkey)
    return yundama


# yundama = get_api()
# codetype  = 1004 #验证码格式
# timeout  = 60
# cid, result = yundama.decode('./aitouzi_unlab/abc.png', codetype, timeout)
# print(result)


if __name__ == '__main__':
    yundama = get_api()
    codetype = 1004  # 验证码格式
    timeout = 60
    pics = glob.glob(r'C:\Bee\Python\Projects\ComputerVision\webCrawler\aitouzi_unlab\*.png')
    # pics = ['./j8yc.png']
    print('Total pics: ', len(pics))
    for i, pic in enumerate(pics):
        # try:
        cid, result = yundama.decode(pic, codetype, timeout)
        print(i, pic, result)
        pic_n = pic.replace('_', result.lower() + '_')
        # pic_n = result.lower() + pic
        os.rename(pic, pic_n)
        # except Exception as e:
        #     print('failed: ', pic)
        #     continue
        break

