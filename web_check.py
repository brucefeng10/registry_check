#!/usr/bin/python3

import cv2
import hashlib
from PIL import Image
import os
import random
import csv
import logging
import time

import logging.config

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy import ProxyType
from reg_predict_one import predict_img
from bojindai_api import CNNPredictionBJD
from aitouzi_api import CNNPredictionATZ
from multiprocessing import Pool


logging.config.fileConfig('logging.conf')


# opt = webdriver.ChromeOptions()
# opt.add_argument('--headless')
# opt.add_argument("--proxy-server=http://202.20.16.82:10152")
# service_args = [
#   '--proxy=%s' % '180.118.86.115:9000',  # 代理 IP：prot  （eg：192.168.0.28:808）
#   '--proxy-type=http',      # 代理类型：http/https
#   '--load-images=no',      # 关闭图片加载（可选）
#   '--disk-cache=yes',      # 开启缓存（可选）
#   '--ignore-ssl-errors=true'  # 忽略https错误（可选）
# ]
#
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap['phantomjs.page.settings.userAgent'] = (
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36')
# dcap['browserName'] = 'Chrome'
driver = webdriver.PhantomJS(executable_path='C:\\ProgramAppFeng\\phantomjs\\bin\\phantomjs.exe', desired_capabilities=dcap,
                             service_args=['--ignore-ssl-errors=true'])
# driver = webdriver.PhantomJS(executable_path='/home/ai/fengxf/tools/phantomjs/bin/phantomjs', desired_capabilities=dcap,
#                              service_args=['--ignore-ssl-errors=true'])


class UnlabeledData(object):
    """通过爬虫截图的方式获取未标注的验证码数据。"""

    def __init__(self):
        self.password = 'mi_258_ma'

    def telephone_nums(self):
        # read telephone number
        with open('telephone_no.txt', 'r') as f:
            s = f.read()
            data = s.split('\n')

        return list(set(data))

    def aitouzi(self, pic_cnt):
        """爱投资"""
        prj_name = 'aitouzi'
        isExists = os.path.exists('{}_unlab'.format(prj_name))
        if not isExists:
            os.mkdir('{}_unlab'.format(prj_name))

        url = 'https://www.itouzi.com/forgetPwdStep1'
        driver.get(url)
        time.sleep(1)

        try_time = 0
        while try_time < pic_cnt:
            try_time += 1
            print('Count: ', try_time)

            t = str(time.time())
            md = hashlib.md5()
            md.update(t.encode('utf-8'))
            pic_name = md.hexdigest()

            driver.find_element_by_xpath('//img[@class="img-captch vcodeWrapper"]').click()
            time.sleep(0.5)

            driver.set_window_size(1920, 1080)
            driver.save_screenshot('./{}_unlab/xxxx_{}.png'.format(prj_name, pic_name))  # save1: screenshot(1920*1080)
            # continue
            time.sleep(0.5)

            image = Image.open('./{}_unlab/xxxx_{}.png'.format(prj_name, pic_name))
            # second try: screenshot image from (985, 460) to (1079, 499)
            image.crop((985, 460, 1079, 499)).save(
                './{}_unlab/xxxx_{}.png'.format(prj_name, pic_name))  # save2: screenshot(94*39)

    def yiqihao(self, pic_cnt):
        """一起好"""
        prj_name = 'yiqihao'
        phone_list = self.telephone_nums()
        phone_cnt = len(phone_list)
        isExists = os.path.exists('{}_unlab'.format(prj_name))
        if not isExists:
            os.mkdir('{}_unlab'.format(prj_name))

        url = 'https://www.yiqihao.com/user/getpwd?redirect=/'
        driver.get(url)
        time.sleep(1)

        phone_no = phone_list[random.randint(0, phone_cnt - 1)]

        driver.find_element_by_id('getpwd_account').send_keys(phone_no)
        driver.find_element_by_id('getpwd_newpassword').send_keys(self.password)
        driver.find_element_by_id('getpwd_newpassword2').send_keys(self.password)
        driver.find_element_by_id('resend').click()
        # driver.find_element_by_xpath('//img[@class="img-captch vcodeWrapper"]').click()
        time.sleep(0.5)

        try_time = 0
        while try_time < pic_cnt:
            try_time += 1
            print('Count: ', try_time)

            t = str(time.time())
            md = hashlib.md5()
            md.update(t.encode('utf-8'))
            pic_name = md.hexdigest()

            driver.find_element_by_xpath('//img[@class="captcha"]').click()
            time.sleep(0.5)
            driver.set_window_size(1920, 1080)
            driver.save_screenshot('./{}_unlab/xxxx_{}.png'.format(prj_name, pic_name))  # save1: screenshot(1920*1080)
            # continue
            time.sleep(0.5)

            image = Image.open('./{}_unlab/xxxx_{}.png'.format(prj_name, pic_name))
            # second try: screenshot image from (250, 234) to (350, 274)
            image.crop((250, 234, 350, 274)).save(
                './{}_unlab/xxxx_{}.png'.format(prj_name, pic_name))  # save2: screenshot(100*40)

            result = predict_img('./{}_unlab/xxxx_{}.png'.format(prj_name, pic_name))

            driver.find_element_by_xpath('//input[@class="inp"]').send_keys(str(result))
            driver.find_element_by_id('sms-captcha-submit').click()

            alert = driver.switch_to.alert  # 通过switch_to.alert切换到alert
            time.sleep(1)
            print(alert.text)  # text属性输出alert的文本
            alert.accept()  # alert“确认”
            time.sleep(1)


# aa = UnlabeledData()
# aa.yiqihao(2)
# driver.close()


def renrendai_login(phone_num):
    """输入手机号和验证码进行登录注册，需要手机端验证码"""

    t = str(time.time())
    md = hashlib.md5()
    md.update(t.encode('utf-8'))
    pic_name = md.hexdigest()

    isExists = os.path.exists('renrendai_pic')
    if not isExists:
        os.mkdir('renrendai_pic')
    isExists = os.path.exists('renrendai_fdbk')
    if not isExists:
        os.mkdir('renrendai_fdbk')

    url = 'https://www.renrendai.com/passport/index/register?registerSource=web_top&wpFromPos=topHeader'
    driver.get(url)
    time.sleep(1)

    # input telephone number(login name) and captcha
    driver.find_element_by_id('reg_username').clear()
    driver.find_element_by_id('reg_username').send_keys(str(phone_num))
    time.sleep(1)
    driver.find_element_by_xpath('//span[@class="verification is_validate"]').click()
    time.sleep(1)
    driver.set_window_size(1920, 1080)

    driver.save_screenshot('./renrendai_pic/{}.png'.format(pic_name))  # save1: screenshot(1920*1080)
    image = Image.open('./renrendai_pic/{}.png'.format(pic_name))

    # screenshot image from (960, 285) to (1070, 330)
    image.crop((1376, 280, 1460, 312)).save('./renrendai_pic/scr_{}.png'.format(pic_name))  # save2: screenshot(110*45)

    result = predict_img('./renrendai_pic/scr_{}.png'.format(pic_name))
    print('predict value',  result)
    #        try:
    #            os.rename('./crop_xinlang_2/{}.png'.format(i),'./crop_xinlang_2/{}.png'.format(str(result)))
    #        except:
    #            os.rename('./crop_xinlang_2/{}.png'.format(i),'./crop_xinlang_2/{}.png'.format(str('error')))

    # driver.find_element_by_id('reg_RandCode').clear()
    driver.find_element_by_id('reg_RandCode').send_keys(str(result))
    driver.find_element_by_xpath('//span[@class="verification is_validate"]').click()

    time.sleep(2)
    driver.save_screenshot('./renrendai_fdbk/{}.png'.format(pic_name))  # save3: feedback from website

    # judge a captcha validity by the feedback from website(screenshot size)
    # 手机号注册了，且验证码预测成功
    if os.path.getsize('./renrendai_fdbk/{}.png'.format(pic_name)) > 0:
        # write(tele_no, '1')
        print(phone_num, 'succeed')
        # os.rename('./renrendai_pic/{}.png'.format(i), './crop_xinlang_2/{}.png'.format(str(result)))  # save4

    if os.path.getsize('./renrendai_fdbk/{}.png'.format(pic_name)) <= 210000:
        im = Image.open('./renrendai_fdbk/data_out' + str(pic_name) + '.png')
        box = (1070, 240, 1300, 320)
        region = im.crop(box)
        # print(tele_no, 'fail')
        region.save('./telephone/data_out-s' + str(pic_name) + '.png')  # save5
        if 3000 < os.path.getsize('./renrendai_fdbk/{}.png'.format(pic_name)) < 3500:
            # write(tele_no, '0')
            print(phone_num, 'fail-succeed')
            # os.rename('./renrendai_pic/{}.png'.format(pic_name), './renrendai_pic/{}.png'.format(str(result)+pic_name))
        else:
            # temp.append(tele_no)
            print(phone_num, 'fail-fail')
            # os.remove('./crop_xinlang_2/{}.png'.format(i))


def renrendai(phone_num):
    """
    人人贷网站（IP容易被封）：
    忘记密码：找回密码页面判断手机号是否注册，无需输入验证码
    """

    url = 'https://www.renrendai.com/user/findpwd/index'
    driver.get(url)
    time.sleep(1)
    # input telephone number(login name) and captcha
    # driver.find_element_by_id('reg_username').clear()
    driver.find_element_by_id('mobileOrEmail').send_keys(str(phone_num))
    driver.find_element_by_id('subNotLoginFindPswBt').click()
    time.sleep(5)
    # driver.set_window_size(1920, 1080)
    # driver.save_screenshot('./renrendai_pic/{}.png'.format('forget'))  # save1: screenshot(1920*1080)
    # hand = driver.window_handles  # 获取当前的所有句柄
    # print('hand', hand)  # 打印当前的所有句柄
    # driver.switch_to.window(hand[0])  # go to current web page
    # time.sleep(2)
    pageSource = driver.page_source
    if '用户不存在' in pageSource:
        # print(pageSource)
        return 0  # phone number not registered
    else:
        logging.info('renrendai registered no: ' + str(phone_num))
        return 1  # phone number registered


def bojindai(phone_num):
    """
    博金贷网站（IP不容易被封）：
    忘记密码：输入手机号和验证码进行找回密码，根据返回信息判断是否注册
    """

    prj_name = 'bojindai'

    isExists = os.path.exists('{}_pic'.format(prj_name))
    if not isExists:
        os.mkdir('{}_pic'.format(prj_name))

    url = 'https://www.bjdp2p.com/retrieve.page'
    driver.get(url)
    time.sleep(0.5)

    try_time = 0
    while try_time < 4:
        try_time += 1

        t = str(time.time())
        md = hashlib.md5()
        md.update(t.encode('utf-8'))
        pic_name = md.hexdigest()
        pic_name = 'xxxx_' + pic_name

        # input telephone number(login name) and captcha
        driver.find_element_by_id('phone').clear()
        driver.find_element_by_id('phone').send_keys(str(phone_num))
        # driver.find_element_by_xpath('//a[@class="a-yzm"]').click()
        # time.sleep(0.5)

        driver.set_window_size(1920, 1080)
        driver.save_screenshot('./{}_pic/{}.png'.format(prj_name, pic_name))  # save1: screenshot(1920*1080)
        # continue
        # time.sleep(0.5)
        image = Image.open('./{}_pic/{}.png'.format(prj_name, pic_name))
        if try_time <= 0:
            # first time visit: screenshot image from (1077, 486) to (1175, 518)
            image.crop((1077, 486, 1175, 518)).save(
                './{}_pic/{}.png'.format(prj_name, pic_name))  # save2: screenshot(98*32)
        else:
            # second try: screenshot image from (1077, 572) to (1175, 604)
            image.crop((1077, 572, 1175, 604)).save(
                './{}_pic/{}.png'.format(prj_name, pic_name))  # save2: screenshot(98*32)

        # jingjing ocr
        # result = predict_img('./{}_pic/{}.png'.format(prj_name, pic_name))
        # cnn prediction
        result = cnnm_bjd.make_prediction('./{}_pic/{}.png'.format(prj_name, pic_name))

        # print('predict value', result)

        driver.find_element_by_id('yzm1').clear()
        driver.find_element_by_id('yzm1').send_keys(str(result))
        driver.find_element_by_id('submitButton').click()
        time.sleep(0.5)

        feedbk_info = driver.find_element_by_id('error').get_attribute('innerText')

        if feedbk_info == '输入验证码错误':
            # os.remove('./{}_pic/{}.png'.format(prj_name, pic_name))
            driver.refresh()
            continue
        elif feedbk_info == '手机号不存在':
            os.rename('./{}_pic/{}.png'.format(prj_name, pic_name), './{}_pic/{}.png'.format(prj_name, pic_name.replace('xxxx_', str(result)+'_')))
            return 0
        elif feedbk_info == '':
            os.rename('./{}_pic/{}.png'.format(prj_name, pic_name),
                      './{}_pic/{}.png'.format(prj_name, pic_name.replace('xxxx_', str(result) + '_')))
            return 1  # 13917775476
        else:
            logging.info('bojindai feedback info {}: '.format(phone_num) + feedbk_info)
            print('feed_back_info', feedbk_info, pic_name)
            return 3

    return 2  # terrible captcha prediction


def tuodao(phone_num):
    """
    拓道金服：
    忘记密码：找回密码页面判断手机号是否注册，无需输入验证码
    """

    url = 'https://www.51tuodao.com/front/getPwd'
    driver.get(url)
    time.sleep(0.5)
    # input telephone number(login name) and captcha
    # driver.find_element_by_id('reg_username').clear()
    driver.find_element_by_id('phone').send_keys(str(phone_num))
    driver.find_element_by_id('nextStep').click()
    time.sleep(0.5)
    try:
        feedbk_info = driver.find_element_by_xpath('//div[@class="layui-layer-content layui-layer-padding"]').get_attribute('innerText')
        # logging.info('tuodao feedback info: ' + feedbk_info)
        if feedbk_info == '该手机未注册':
            # print(phone_num, feedbk_info)
            return 0
        else:
            logging.info('tuodao registered no: ' + str(phone_num))
            return 4
    except Exception as e:
        try:
            feedbk_info = driver.find_element_by_id('mPhone').get_attribute('innerText')
            print(phone_num, feedbk_info)
            # logging.info('tuodao feedback info: ' + feedbk_info)
            if feedbk_info[-4:] == phone_num[-4:]:  # 返回号码
                return 1  # 13905164979
        except Exception as e2:
            logging.info('tuodao possible registered no: ' + str(phone_num))
            logging.info(e2)
            return 3


def aitoujinrong(phone_num):
    """
    爱投金服：
    忘记密码：找回密码页面判断手机号是否注册，无需输入验证码
    """

    url = 'https://www.5aitou.com/retrievepass/index.htm'
    driver.get(url)
    time.sleep(0.5)
    # input telephone number(login name) and captcha
    # driver.find_element_by_id('reg_username').clear()
    driver.find_element_by_id('celphone').send_keys(str(phone_num))
    driver.find_element_by_id('verifyCode').click()
    time.sleep(0.5)
    try:
        feedbk_info = driver.find_element_by_id('celphone-error').get_attribute('innerText')
        # logging.info('aitoujinrong feedback info: ' + feedbk_info)
        if feedbk_info == '该手机号不存在':
            return 0
        else:
            logging.info('aitoujinrong registered no: ' + str(phone_num))
            return 3
    except Exception as e:
        logging.info('aitoujinrong possible registered no: ' + str(phone_num))
        logging.info(e)
        return 1


def aitouzi(phone_num):
    """
    爱投资：
    忘记密码：输入手机号和验证码进行找回密码，根据返回信息判断是否注册
    """

    prj_name = 'aitouzi'

    isExists = os.path.exists('{}_pic'.format(prj_name))
    if not isExists:
        os.mkdir('{}_pic'.format(prj_name))

    url = 'https://www.itouzi.com/forgetPwdStep1'
    driver.get(url)
    time.sleep(0.5)

    try_time = 0
    while try_time < 5:
        try_time += 1

        t = str(time.time())
        md = hashlib.md5()
        md.update(t.encode('utf-8'))
        pic_name = md.hexdigest()
        pic_name = 'xxxx_' + pic_name

        # input telephone number(login name) and captcha
        driver.find_element_by_id('phone').clear()
        driver.find_element_by_id('phone').send_keys(str(phone_num))
        # driver.find_element_by_xpath('//a[@class="a-yzm"]').click()
        time.sleep(0.5)

        driver.set_window_size(1920, 1080)
        driver.save_screenshot('./{}_pic/{}.png'.format(prj_name, pic_name))  # save1: screenshot(1920*1080)
        # continue
        time.sleep(0.5)
        image = Image.open('./{}_pic/{}.png'.format(prj_name, pic_name))

        # screenshot image from (985, 460) to (1079, 499)
        image.crop((985, 460, 1079, 499)).save(
            './{}_pic/{}.png'.format(prj_name, pic_name))  # save2: screenshot(94*39)

        # cnn prediction
        result = cnnm_atz.make_prediction('./{}_pic/{}.png'.format(prj_name, pic_name))

        # print('predict value', result)

        driver.find_element_by_id('valicode').clear()
        driver.find_element_by_id('valicode').send_keys(str(result))
        driver.find_element_by_id('submitBtn').click()
        time.sleep(1)

        feedbk_info = driver.find_element_by_id('stepError').get_attribute('innerText')

        if feedbk_info == '验证码不正确，请重新输入':
            # os.remove('./{}_pic/{}.png'.format(prj_name, pic_name))
            driver.refresh()
            continue
        elif feedbk_info == '手机号码未认证，请重新输入':
            os.rename('./{}_pic/{}.png'.format(prj_name, pic_name),
                      './{}_pic/{}.png'.format(prj_name, pic_name.replace('xxxx_', str(result) + '_')))
            return 0
        elif feedbk_info == '':
            try:
                driver.find_element_by_id('cardNum').click()
                os.rename('./{}_pic/{}.png'.format(prj_name, pic_name),
                          './{}_pic/{}.png'.format(prj_name, pic_name.replace('xxxx_', str(result) + '_')))
                return 1  # 13588720654
            except:
                return 3

        else:
            logging.info('aitouzi feedback info {}: '.format(phone_num) + feedbk_info)
            print('feed_back_info', feedbk_info, pic_name)
            return 3

    return 2  # terrible captcha prediction


def main():

    data_name = 'bojindai'
    phone_list = []
    with open('./phone_list/{}.csv'.format(data_name), 'rU') as f:
        reader = csv.reader(f)
        for v in reader:
            phone_list.append(v[0])
    print('Number of phones: ', len(phone_list))
    # phone_list = ['18650116312', '13588720654', '13905164979']
    # 0：未注册，1：注册，2：验证码多次识别错误，3：未知
    # result = [['phone_no', '博金贷', '拓道金服', '爱投金融']]
    result = []
    for i, phno in enumerate(phone_list):
        phno_result = [phno]
        # result = renrendai(phno)  # True: registered; False: not registered
        try:
            result1 = bojindai(phno)
            phno_result.append(result1)
            time.sleep(1)
        except Exception as e1:
            phno_result.append(3)
            logging.info(e1)
        # try:
        #     result2 = tuodao(phno)
        #     phno_result.append(result2)
        # except Exception as e2:
        #     phno_result.append(3)
        #     logging.info(e2)
        # try:
        #     result3 = aitoujinrong(phno)
        #     phno_result.append(result3)
        #     time.sleep(1)
        # except Exception as e3:
        #     phno_result.append(3)
        #     logging.info(e3)
        # try:
        #     result4 = aitouzi(phno)
        #     phno_result.append(result4)
        # except Exception as e4:
        #     phno_result.append(3)
        #     logging.info(e4)

        print('Result{}: '.format(i), phno_result)
        result.append(phno_result)
        # logging.info(phno + str(result))

        if i % 100 == 0:
            with open('./result/result_{}.csv'.format(data_name), 'w', newline='') as fps:
                writer = csv.writer(fps)
                for row in result:
                    writer.writerow(row)

    print('result', result)
    driver.close()

    if_write = True
    if if_write:
        with open('./result/result_{}.csv'.format(data_name), 'w', newline='') as fps:
            writer = csv.writer(fps)
            for row in result:
                writer.writerow(row)


def multi_process():
    data_name = 'data'
    phone_list = []
    with open('./phone_list/{}.csv'.format(data_name), 'rU') as f:
        reader = csv.reader(f)
        for v in reader:
            phone_list.append(v[0])

    phone_list = ['18650116312', '13588720654', '13905164979', '13689562456']
    # 0：未注册，1：注册，2：验证码多次识别错误，3：未知
    # result = [['phone_no', '博金贷', '拓道金服', '爱投金融']]
    result = []
    pool = Pool(8)
    for i, ph in enumerate(phone_list):
        res = pool.apply_async(func=aitouzi, args=(ph,))
        result.append(res)
    pool.close()
    pool.join()
    # for i, phno in enumerate(phone_list):
    #     phno_result = [phno]
        # result = renrendai(phno)  # True: registered; False: not registered
        # try:
        #     result1 = bojindai(phno)
        #     phno_result.append(result1)
        # except Exception as e1:
        #     phno_result.append(3)
        #     logging.info(e1)
        # try:
        #     result2 = tuodao(phno)
        #     phno_result.append(result2)
        # except Exception as e2:
        #     phno_result.append(3)
        #     logging.info(e2)
        # try:
        #     result3 = aitoujinrong(phno)
        #     phno_result.append(result3)
        # except Exception as e3:
        #     phno_result.append(3)
        #     logging.info(e3)
        # try:
        #     result4 = aitouzi(phno)
        #     phno_result.append(result4)
        # except Exception as e4:
        #     phno_result.append(3)
        #     logging.info(e4)
        #
        # print('Result{}: '.format(i), phno_result)
        # result.append(phno_result)
        # logging.info(phno + str(result))

    print('result', phone_list, result)
    for res in result:
        print(res.get())
    driver.close()

    if_write = False
    if if_write:
        with open('./result/result_{}.csv'.format(data_name), 'w', newline='') as fps:
            writer = csv.writer(fps)
            for row in result:
                writer.writerow(row)


if __name__ == '__main__':
    # read telephone number
    t0 = time.time()
    cnnm_bjd = CNNPredictionBJD()  # bojindai prediction api
    # cnnm_atz = CNNPredictionATZ()  # aitouzi prediction api
    main()

    t1 = time.time()
    print('total elapsed time: ', t1-t0)




