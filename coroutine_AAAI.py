#!/usr/bin/python3
import time
from lxml import etree
import aiohttp
import asyncio
import requests

urls = [
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16488',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16583',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16380',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16911',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16581',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16674',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16112',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/17343',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16659',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16449',
]
urls = ['https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16488'] * 10
titles = []
sem = asyncio.Semaphore(10) # 信号量，控制协程数，防止爬的过快
'''
提交请求获取AAAI网页,并解析HTML获取title
'''


async def get_title(url):
    with(await sem):
        # async with是异步上下文管理器
        async with aiohttp.ClientSession() as session:  # 获取session
            print('a')
            async with session.request('GET', url) as resp:  # 提出请求
                print('b')
                # html_unicode = await resp.text()
                # html = bytes(bytearray(html_unicode, encoding='utf-8'))
                html = await resp.read()  # 可直接获取bytes
                title = etree.HTML(html).xpath('//*[@id="title"]/text()')
                print(''.join(title))
                titles.append(title)
                return True


def main():
    loop = asyncio.get_event_loop()           # 获取事件循环
    tasks = [get_title(url) for url in urls]  # 把所有任务放到一个列表中
    loop.run_until_complete(asyncio.wait(tasks))  # 激活协程
    loop.close()  # 关闭事件循环


def get_title0(url,cnt):
    response = requests.get(url)  # 提交请求,获取响应内容
    html = response.content       # 获取网页内容(content返回的是bytes型数据,text()获取的是Unicode型数据)
    title = etree.HTML(html).xpath('//*[@id="title"]/text()') # 由xpath解析HTML
    print('第%d个title:%s' % (cnt,''.join(title)))


if __name__ == '__main__':
    t0 = time.time()
    main()  # 调用方
    # i = 0
    # for url in urls:
    #     i = i + 1
    #     start = time.time()
    #     get_title0(url, i)

    t1 = time.time()
    print('total elapsed time: ', t1 - t0)
    print(titles)

