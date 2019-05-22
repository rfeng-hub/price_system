"""
爬去淘票票电影的电影票
Edit By RanFeng
"""
from lxml import etree
import time
import sys,os
sys.path.append(os.getcwd())
from database.cinema import mongo as tao_cinema
from database.ticket import mongo as tao_ticket
from setting import CINIMA_TAO_COLLECTION,TICKET_TAO_COLLECTION
from bs4 import BeautifulSoup as bs4
import requests

def req_url(cinema_url):
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"}
    if use_re_header and self.response_header:
        headers['cookie'] = self.citycode or self.extract_header()

    proxies = pr.get_proxy()

    res = self._req_url(url, headers=headers, proxies=proxies)
    if res:
        return res
    else:
        return self.req_url(url, error=error + 1, use_re_header=use_re_header, formobile=formobile)

def get_showInfo(cinema_url):
    """
    根据影院链接地址获取每部电影排片信息
    :param cinema_url: 电影院链接地址
    :return: 排片信息
    """
    content = req_url(cinema_url)
    assert content, '请求失败，请检查 /utils/req.py 中 req_url 函数是否工作正常'
    soup = bs4.BeautifulSoup(content, 'lxml')
    soup_film = soup.find('a', text=re.compile(movie_name))

    film_param = soup_film['data-param']

    return get_ticket_info(film_param)

get_showInfo('https://dianying.taobao.com/cinemaDetail.htm?cinemaId=5766&n_s=new')