import json
import os
from multiprocessing.dummy import Pool

import requests
from requests.exceptions import RequestException
import re


def get_one_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


def parse_one_page(html):
    # 换行
    pattern = re.compile(
        '<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p>'
        + '.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield {
            'index': item[0],
            'image': item[1],
            'title': item[2],
            'actor': item[3].strip()[3:],
            'time': item[4].strip()[5:],
            'score': item[5] + item[6]
        }


def save_image_file(url, path):
    '''
    保存电影封面
    '''
    ir = requests.get(url)
    if ir.status_code == 200:
        with open(path, 'wb') as f:
            f.write(ir.content)
            f.close()


def write_to_file(content):
    with open('result.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
        f.close()


def main(offset):
    url = 'http://maoyan.com/board/4?offset=' + str(offset)
    html = get_one_page(url)
    # 封面文件夹不存在则创建
    if not os.path.exists('covers'):
        os.mkdir('covers')
    for item in parse_one_page(html):
        print(item)
        write_to_file(item)
        save_image_file(item['image'], 'covers/' + '%03d' % int(item['index']) + item['title'] + '.jpg')


# if __name__ == '__main__':
#     for i in range(10):
#         main(i*10)
# 多线程
if __name__ == '__main__':
    pool = Pool()
    pool.map(main, [i * 10 for i in range(10)])
