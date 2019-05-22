# from setting import CINEMA_SHI_COLLECTION,CINEMA_MAO_COLLECTION,CINEMA_NUO_COLLECTION,CINEMA_TAO_COLLECTION,CITY_COLLECTION
# from database.cities import mongo
#
# city = mongo(CITY_COLLECTION)
# shi = mongo(CINEMA_SHI_COLLECTION)
# mao = mongo(CINEMA_MAO_COLLECTION)
# nuo = mongo(CINEMA_NUO_COLLECTION)
# tao = mongo(CINEMA_TAO_COLLECTION)
#
# shi_cities = []
# mao_cities = []
# nuo_cities = []
# tao_cities = []
# cities = []
#
# for cinema in shi.findAll():
#     shi_cities.append(cinema['city'])
# for cinema in mao.findAll():
#     mao_cities.append(cinema['city'])
# for cinema in nuo.findAll():
#     nuo_cities.append(cinema['city'])
# for cinema in tao.findAll():
#     tao_cities.append(cinema['city'])
#
# cities = list(set(shi_cities).union(set(mao_cities)).union(set(nuo_cities)).union(set(tao_cities)))
# print(cities)




# from database.cities import mongo
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from lxml import etree
# import requests
# import re
# import json
# from database.cities import mongo
# from setting import CITY_COLLECTION
#
# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless') #无界面运行（无窗口）
# chrome_options.add_argument('--no-sandbox') #取消沙盒模式
# chrome_options.add_argument('--disable-gpu') #谷歌文档提到需要加上这个属性来规避bug
# driver = webdriver.Chrome(options=chrome_options)
# # driver = webdriver.Chrome()
# wait = WebDriverWait(driver, 10)
#
# def maoyan():
#     cinemas_url = 'https://maoyan.com/cinemas'
#
#     driver.get(cinemas_url)
#     actions = ActionChains(driver)
#     city_tag = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="city-name"]')))  # 定位城市
#     actions.click(city_tag).perform() #展开城市列表
#     html = driver.page_source
#     xpath_parser = etree.HTML(html)
#     A = xpath_parser.xpath('//div[@class="city-list"]//li[position()=1]//a[@class="js-city-name"]/text()')
#     B = xpath_parser.xpath('//div[@class="city-list"]//li[position()=2]//a[@class="js-city-name"]/text()')
#     C = xpath_parser.xpath('//div[@class="city-list"]//li[position()=3]//a[@class="js-city-name"]/text()')
#     D = xpath_parser.xpath('//div[@class="city-list"]//li[position()=4]//a[@class="js-city-name"]/text()')
#     E = xpath_parser.xpath('//div[@class="city-list"]//li[position()=5]//a[@class="js-city-name"]/text()')
#     F = xpath_parser.xpath('//div[@class="city-list"]//li[position()=6]//a[@class="js-city-name"]/text()')
#
#     return A,B,C,D,E,F
#
# def jsonfy(s):
#     #此函数将不带双引号的json的key标准化
#     obj = eval(s, type('js', (dict,), dict(__getitem__=lambda s, n: n))())
#     return obj
#
# def shiguang():
#     data_url = 'http://static1.mtime.cn/20180730161010/Utility/Data/TheaterListBoxData.m'
#     data = requests.get(data_url).text.replace("var threaterListBoxData = ", "").replace(";", "")  # 切掉字典数据之外多余的部分
#     cinemas_data = jsonfy(data)  # 将不带双引号的json的key标准化
#     A, B, C, D, E, F = [], [], [], [], [], []
#     for city in cinemas_data['locations']['List']:
#         cityName = city['NameCn']
#         letter = re.match(r'\w', city['PinyinShort'])  # 匹配城市拼音首字母
#         if letter != None and letter.group() == 'a':
#             A.append(cityName)
#         if letter != None and letter.group() == 'b':
#             B.append(cityName)
#         if letter != None and letter.group() == 'c':
#             C.append(cityName)
#         if letter != None and letter.group() == 'd':
#             D.append(cityName)
#         if letter != None and letter.group() == 'e':
#             E.append(cityName)
#         if letter != None and letter.group() == 'f':
#             F.append(cityName)
#     return A,B,C,D,E,F
#
# def nuomi():
#     citys_url = 'https://dianying.nuomi.com/home/citylist?cityId=320'
#     driver.get(citys_url)
#     html = driver.page_source
#     xpath_parser = etree.HTML(html)
#     """拼音首字母为A-F的城市"""
#     A = [city.split()[0] for city in xpath_parser.xpath('//li[@class="city-list clearfix"][position()=1]//ul[@class="cities fl"]//li//a/text()')]
#     B = [city.split()[0] for city in xpath_parser.xpath('//li[@class="city-list clearfix"][position()=2]//ul[@class="cities fl"]//li//a/text()')]
#     C = [city.split()[0] for city in xpath_parser.xpath('//li[@class="city-list clearfix"][position()=3]//ul[@class="cities fl"]//li//a/text()')]
#     D = [city.split()[0] for city in xpath_parser.xpath('//li[@class="city-list clearfix"][position()=4]//ul[@class="cities fl"]//li//a/text()')]
#     E = [city.split()[0] for city in xpath_parser.xpath('//li[@class="city-list clearfix"][position()=5]//ul[@class="cities fl"]//li//a/text()')]
#     F = [city.split()[0] for city in xpath_parser.xpath('//li[@class="city-list clearfix"][position()=6]//ul[@class="cities fl"]//li//a/text()')]
#
#     return A,B,C,D,E,F
#
# def taopiaopiao():
#     city_json = "https://www.taopiaopiao.com/cityAction.json?activityId&_ksTS=1550457279536_84&jsoncallback=jsonp85&action=cityAction&n_s=new&event_submit_doGetAllRegion=true"
#     driver.get(city_json)
#     jsonp = driver.page_source
#     pattern = re.compile(r'{"returnCode.+]}}')
#     content = pattern.search(jsonp).group()
#     content = json.loads(content)
#
#     A = [city['regionName'] for city in content['returnValue']['A']]
#     B = [city['regionName'] for city in content['returnValue']['B']]
#     C = [city['regionName'] for city in content['returnValue']['C']]
#     D = [city['regionName'] for city in content['returnValue']['D']]
#     E = [city['regionName'] for city in content['returnValue']['E']]
#     F = [city['regionName'] for city in content['returnValue']['F']]
#
#     return A, B, C, D, E, F
#
# A1, B1, C1, D1, E1, F1 = maoyan()
# A2, B2, C2, D2, E2, F2 = shiguang()
# A3, B3, C3, D3, E3, F3 = taopiaopiao()
# A4, B4, C4, D4, E4, F4 = nuomi()
#
# A = (list(set(A1).union(set(A2)).union(set(A3)).union(set(A4))))
# B = (list(set(B1).union(set(B2)).union(set(B3)).union(set(B4))))
# C = (list(set(C1).union(set(C2)).union(set(C3)).union(set(C4))))
# D = (list(set(D1).union(set(D2)).union(set(D3)).union(set(D4))))
# E = (list(set(E1).union(set(E2)).union(set(E3)).union(set(E4))))
# F = (list(set(F1).union(set(F2)).union(set(F3)).union(set(F4))))
#
# city = mongo(CITY_COLLECTION)
# city.insert({'key':'A','cities':A})
# city.insert({'key':'B','cities':B})
# city.insert({'key':'C','cities':C})
# city.insert({'key':'D','cities':D})
# city.insert({'key':'E','cities':E})
# city.insert({'key':'F','cities':F})




from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
import requests
import re
import json
from database.cities import mongo
from setting import CITY_COLLECTION

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless') #无界面运行（无窗口）
chrome_options.add_argument('--no-sandbox') #取消沙盒模式
chrome_options.add_argument('--disable-gpu') #谷歌文档提到需要加上这个属性来规避bug
driver = webdriver.Chrome(options=chrome_options)
# driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

def maoyan():
    cinemas_url = 'https://maoyan.com/cinemas'

    driver.get(cinemas_url)
    actions = ActionChains(driver)
    city_tag = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="city-name"]')))  # 定位城市
    actions.click(city_tag).perform() #展开城市列表
    html = driver.page_source
    xpath_parser = etree.HTML(html)
    A = xpath_parser.xpath('//div[@class="city-list"]//li[position()=1]//a[@class="js-city-name"]/text()')
    B = xpath_parser.xpath('//div[@class="city-list"]//li[position()=2]//a[@class="js-city-name"]/text()')

    return A,B

def jsonfy(s):
    #此函数将不带双引号的json的key标准化
    obj = eval(s, type('js', (dict,), dict(__getitem__=lambda s, n: n))())
    return obj

def shiguang():
    data_url = 'http://static1.mtime.cn/20180730161010/Utility/Data/TheaterListBoxData.m'
    data = requests.get(data_url).text.replace("var threaterListBoxData = ", "").replace(";", "")  # 切掉字典数据之外多余的部分
    cinemas_data = jsonfy(data)  # 将不带双引号的json的key标准化
    A, B = [], []
    for city in cinemas_data['locations']['List']:
        cityName = city['NameCn']
        letter = re.match(r'\w', city['PinyinShort'])  # 匹配城市拼音首字母
        if letter != None and letter.group() == 'a':
            A.append(cityName)
        if letter != None and letter.group() == 'b':
            B.append(cityName)

    return A,B

def nuomi():
    citys_url = 'https://dianying.nuomi.com/home/citylist?cityId=320'
    driver.get(citys_url)
    html = driver.page_source
    xpath_parser = etree.HTML(html)
    """拼音首字母为A-F的城市"""
    A = [city.split()[0] for city in xpath_parser.xpath('//li[@class="city-list clearfix"][position()=1]//ul[@class="cities fl"]//li//a/text()')]
    B = [city.split()[0] for city in xpath_parser.xpath('//li[@class="city-list clearfix"][position()=2]//ul[@class="cities fl"]//li//a/text()')]

    return A,B

def taopiaopiao():
    city_json = "https://www.taopiaopiao.com/cityAction.json?activityId&_ksTS=1550457279536_84&jsoncallback=jsonp85&action=cityAction&n_s=new&event_submit_doGetAllRegion=true"
    driver.get(city_json)
    jsonp = driver.page_source
    pattern = re.compile(r'{"returnCode.+]}}')
    content = pattern.search(jsonp).group()
    content = json.loads(content)

    A = [city['regionName'] for city in content['returnValue']['A']]
    B = [city['regionName'] for city in content['returnValue']['B']]

    return A, B

def getCity():
    print(">>>>>>>>>>>>>>>>>>>开始获取城市列表>>>>>>>>>>>>>>>>>>")
    A1, B1 = maoyan()
    A2, B2 = shiguang()
    A3, B3 = nuomi()

    A = (list(set(A1).union(set(A2)).union(set(A3))))
    B = (list(set(B1).union(set(B2)).union(set(B3))))

    city = mongo(CITY_COLLECTION)
    city.insert({'key':'A','cities':A})
    city.insert({'key':'B','cities':B})
    print("<<<<<<<<<<<<<<<城市列表获取完成<<<<<<<<<<<<<<<<<<")
    city.disconnect()