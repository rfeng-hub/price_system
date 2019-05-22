"""
获取时光电影院链接地址等信息，作为基本信息保存到数据库
Edit by RanFeng
"""
import sys, os
sys.path.append(os.getcwd())
from database.cinema import mongo
from setting import CINEMA_SHI_COLLECTION
import requests
import re
from multiprocessing import Pool

base_url = 'http://theater.mtime.com/'
data_url = 'http://static1.mtime.cn/20190320160733/Utility/Data/TheaterListBoxData.m'  # 里面有时光网所有影院信息
shiguang = mongo(CINEMA_SHI_COLLECTION)

def jsonfy(s):
    #此函数将不带双引号的json的key标准化
    obj = eval(s, type('js', (dict,), dict(__getitem__=lambda s, n: n))())
    return obj

def parse_cinema(cityName, area):
    stringId = area['StringId']
    cinemas = area['Cinemas']['List']
    for cinema in cinemas:
        cinemaId = cinema['Id']
        cinemaName = cinema['NameCn']
        cinemaUrl = base_url + stringId + "/" + str(cinemaId)
        Cinema = {
            'city': cityName,
            'stringId': stringId,
            'cinemaId': cinemaId,
            'name': cinemaName,
            'url': cinemaUrl
        }
        print("  ", Cinema)
        shiguang.insert(Cinema)

def get_cinemas(city):
    """获取拼音首字母为a-b的城市总数"""
    cityName = city['NameCn']
    areas = city['Districts']['List']
    letter = re.match(r'\w', city['PinyinShort']) #匹配城市拼音首字母
    if letter != None and letter.group()<= 'b':
        print("城市：", cityName)
        print(" 影院：", )
        for area in areas: #解析出每个县城的影院信息
            parse_cinema(cityName, area)
        print()

def crawl():
    shiguang.delete()
    data = requests.get(data_url).text.replace("var threaterListBoxData = ", "").replace(";", "")  # 切掉字典数据之外多余的部分
    cinemas_data = jsonfy(data)  # 将不带双引号的json的key标准化

    pool = Pool()  # 建立进程池
    print(">>>>>>>>>>>>>>>>>>开始爬取时光影院信息>>>>>>>>>>>>>>>>>>>>")
    pool.map(get_cinemas, (city for city in cinemas_data['locations']['List']))
    pool.close()
    print("<<<<<<<<<<<<<<<<<时光影院信息爬取完成！<<<<<<<<<<<<<<<<<<<<\n\n\n")
    shiguang.disconnect()  # 断开连接
