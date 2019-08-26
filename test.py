#!/usr/bin/python3

import glob
import csv
import string
import os
import time
import cv2
import requests
import hashlib
from reg_predict_one import predict_img


def test_pred():
    pics = glob.glob(r'C:\Bee\Python\Projects\ComputerVision\webCrawler\bojindai_screen\labeled\*.png')
    # pics = glob.glob(r'C:\Bee\Python\Projects\ComputerVision\any-captcha-jj\output\bojindai_test_fake\*.jpg')
    total_cnt = len(pics)
    print('test count: ', total_cnt)
    true_cnt = 0
    for pic in pics:
        pred = predict_img(pic)
        # real = pic[-41:-37]
        real = pic[-8:-4]
        print('real-predict: ', real, pred)
        if pred == real:
            true_cnt += 1
    print('Accuracy: ', true_cnt/total_cnt)


def label_bojindai():
    pics = glob.glob(r'C:\Bee\Python\Projects\ComputerVision\webCrawler\bojindai_screen\*.png')
    # pics = glob.glob(r'C:\Bee\Python\Projects\ComputerVision\any-captcha-jj\output\bojindai_test_fake\*.jpg')
    total_cnt = len(pics)
    chs = string.digits + string.ascii_lowercase
    print('possible characters: ', chs)
    print('test count: ', total_cnt)
    true_cnt = 0
    for pic in pics:
        true_cnt += 1
        pred = predict_img(pic)
        print('predict%s: ' % true_cnt, pred)
        if len(pred) == 4:
            if pred[0] in chs and pred[1] in chs and pred[2] in chs and pred[3] in chs:
                os.rename(pic, pic.replace('xxxx_', pred+'_'))


# label_bojindai()


def phone_split():
    with open('./phone_list/data.txt', 'r') as f:
        s = f.read()
        data = s.split('\n')

    xinye_phone = []
    with open('./phone_list/30642_for_feng.csv', 'rU') as xy:
        reader = csv.reader(xy)
        for row in reader:
            xinye_phone.append(row[0])
    print(xinye_phone[1])
    # distinct
    phone_list0 = list(set(xinye_phone))
    phone_list = []
    for p in phone_list0:
        if len(p) == 11:
            phone_list.append(p)

    print(len(phone_list))

    # split_cnt = 0
    # data = []
    # for j, no in enumerate(phone_list):
    #     data.append(no)
    #     if j == 3832 * (split_cnt+1)-1 or j == len(phone_list)-1:
    #         # print(type(data[0]))
    #         with open('./phone_list/data{}.csv'.format(split_cnt), 'w', newline='') as dt:
    #             writer = csv.writer(dt)
    #             for row in data:
    #                 writer.writerow([row])
    #
    #         split_cnt += 1
    #         data = []


def result_combine():
    result = [['phone_no', '博金贷', '拓道金服', '爱投金融']]
    for i in range(10):
        with open('./result/result_data{}.csv'.format(i), 'rU') as fr:
            reader = csv.reader(fr)
            next(reader)
            for v in reader:
                result.append(v)

    print('Total number of phone: ', len(result))
    with open('./result/result_data_0801.csv', 'w', newline='') as rs:
        writer = csv.writer(rs)
        for row in result:
            writer.writerow(row)


def label_pic():
    pics = glob.glob(r'C:\Bee\Python\Projects\registry_check\aitouzi_pic\batch\*.png')
    print('Number of pictures: ', len(pics))
    for i, pic in enumerate(pics):
        img = cv2.imread(pic)
        cv2.imshow('原始', img)
        cv2.waitKey(10)
        lab_value = input('Please label%s: ' % i)
        os.rename(pic, pic.replace(pic[-41:-36], lab_value + '_'))
        # break


# label_pic()

def auto_label():
    from aitouzi_api import CNNPredictionATZ
    cnnm_atz = CNNPredictionATZ()
    pics = glob.glob(r'C:\Bee\Python\Projects\ComputerVision\webCrawler\aitouzi_unlab\*.png')
    print('Number of pictures: ', len(pics))
    for i, pic in enumerate(pics):
        img = cv2.imread(pic)
        pred = cnnm_atz.make_prediction(pic)
        print(i, pred)
        cv2.imshow('原始', img)
        cv2.waitKey(10)
        lab_value = input('Please label%s: ' % i)
        if lab_value == '0':
            os.rename(pic, pic.replace('\\_', '\\' + pred + '_'))  # true prediction
        else:
            os.rename(pic, pic.replace('\\_', '\\' + lab_value + '_'))  # input label

# auto_label()


def cnn_label():
    from aitouzi_api import CNNPredictionATZ
    cnnm_atz = CNNPredictionATZ()
    pics = glob.glob(r'C:\Bee\Python\Projects\registry_check\aitouzi_pic\*.png')
    print('Number of pictures: ', len(pics))
    for i, pic in enumerate(pics):
        img = cv2.imread(pic)
        pred = cnnm_atz.make_prediction(pic)
        print(i, pred)
        os.rename(pic, pic.replace('xxxx_', pred + '_'))  # true prediction
# cnn_label()


def add_md5():
    pics = glob.glob(r'C:\Bee\Python\Projects\ComputerVision\webCrawler\bojindai_screen\labeled_test\*.png')
    for pic in pics:
        cont = pic[-8:-4]

        t = str(time.time())
        md = hashlib.md5()
        md.update(t.encode('utf-8'))
        pic_name = md.hexdigest()

        os.rename(pic, pic.replace(cont, cont+'_'+pic_name))


def find_invalid_characters():
    characters = string.digits + string.ascii_lowercase
    pic_dir = os.listdir(r'C:\Bee\Python\Projects\registry_check\aitouzi_pic')
    for pic in pic_dir:
        if pic[4] != '_':
            print(pic)
            continue
        for lt in pic[:4]:
            if lt not in characters:
                print(pic)
                break


def remove_same():
    characters = string.digits + string.ascii_lowercase
    pic_dir = os.listdir(r'C:\Bee\Python\Projects\registry_check\aitouzi_pic')
    exist_pics = set()
    for pic in pic_dir:
        if pic[:4] in exist_pics:
            os.remove(r'C:\Bee\Python\Projects\registry_check\aitouzi_pic\\' + pic)
        else:
            exist_pics.add(pic[:4])


from multiprocessing import Pool
import multiprocessing
# s = 0
def multiply(x):
    # global s
    s = x[0] * x[1]
    time.sleep(2)
    return s
def multiply1(x):
    # global s
    s = x * y
    time.sleep(2)
    return s
def multi_process():
    """Must be run in if __name__ == "__main__"."""
    a = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]
    a1 = [(1,), (2,), (3,), (4,), (5,), (6,), (7,), (8,)]
    t0 = time.clock()
    # result = []
    pool = Pool(8)
    result = pool.starmap(func=multiply1, iterable=a1)
    pool.close()
    pool.join()
    print(result)
    t1 = time.clock()
    print(t1-t0)


def multi_process1():
    """Must be run in if __name__ == "__main__"."""
    a = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]
    a1 = [(1,), (2,), (3,), (4,), (5,), (6,), (7,), (8,)]
    t0 = time.clock()
    # result = []
    cores = multiprocessing.cpu_count()
    print('cores cnt: ', cores)
    pool = multiprocessing.Pool(processes=cores)

    # method 1: map
    print(pool.map(multiply, a))  # prints [0, 1, 4, 9, 16]

    # # method 2: imap
    # for y in pool.imap(multiply, a):
    #     print(y)  # 0, 1, 4, 9, 16, respectively

    t1 = time.clock()
    print(t1-t0)

if __name__ == "__main_":

    multi_process1()
    pass

def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").content

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

# your spider code

def getHtml():
    # ....
    retry_count = 5
    proxy = get_proxy()
    print('proxy', proxy)
    while retry_count > 0:
        try:
            html = requests.get('https://blog.csdn.net/zpf_07/article/details/78030249', proxies={"http": "http://{}".format(proxy)})
            # 使用代理访问
            return html
        except Exception:
            retry_count -= 1
    # 出错5次, 删除代理池中代理
    delete_proxy(proxy)
    return None

# getHtml()


def check_ip():
    try:
        requests.get('http://wenshu.court.gov.cn/', proxies={"http": "183.129.207.86:11632"})
    except:
        print('connection failed')
    else:
        print('success')
# check_ip()


class C(object):
    def __init__(self, x):
        self._x = x

    # @property
    def showx(self):
        return self._x


def cross_combine():
    aitouzi, rest = {}, {}
    for i in range(8):
        with open(r'C:\Bee\Python\Projects\registry_check\result\result_data{}.csv'.format(i), 'rU') as fr:
            reader = csv.reader(fr)
            for row in reader:
                aitouzi[row[0]] = row[1:]

    with open(r'C:\Bee\Python\Projects\registry_check\result\result_30642_for_feng.csv', 'rU') as fr:
        reader = csv.reader(fr)
        for row in reader:
            aitouzi[row[0]].append(row[1])

    with open(r'C:\Bee\Python\Projects\registry_check\result\result_30642_0819.csv', 'w', newline='') as fw:
        writer = csv.writer(fw)
        for k, v in aitouzi.items():
            writer.writerow([k] + v)




