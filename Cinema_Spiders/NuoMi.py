"""
获取糯米电影院链接地址等信息，作为基本信息保存到数据库
Edit by RanFeng
"""
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from lxml import etree
import time
import re
import sys,os
sys.path.append(os.getcwd())
from database.cinema import mongo
from setting import CINEMA_NUO_COLLECTION
from multiprocessing import Pool


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)
# driver = webdriver.Chrome() #测试用这个
wait = WebDriverWait(driver, 20)
city_url = 'https://dianying.nuomi.com/cinema?cityId={}'
cinema_url = 'https://dianying.nuomi.com/cinema/cinemadetail?cityId={}&cinemaId={}'
citys_url = 'https://dianying.nuomi.com/home/citylist?cityId=320'
NuoMi = mongo(CINEMA_NUO_COLLECTION)

def get_cinemas(cityId):
    """
    获取糯米电影中的影院信息
    :return:
    """
    """获取全国城市总数"""

    url = city_url.format(cityId) #拼凑城市影院链接地址
    driver.get(url)

    """将滚动条移动到页面的底部"""
    js = "window.scrollTo(0, document.body.scrollHeight)"
    driver.execute_script(js)
    time.sleep(3) #一定要睡一会儿，不然网页加载不全，获取不到影院信息

    """影院所属城市,睡一会儿后再获取，这个元素加载出来比较慢"""
    city = driver.find_element_by_css_selector('#selectedCity').text

    """看看影院列表是否有折叠隐藏"""
    try:
        more = driver.find_element_by_css_selector('#moreCinema').get_attribute('class')
    except:
        more = "more hide" #到底了
    clicked_num = 0
    while more == "more" and clicked_num <= 7: # 页数超过8就加载不出来，报错
        driver.find_element_by_css_selector('#moreCinema').click() #点击查看更多影院
        clicked_num += 1 # 点击了一次，计数加一
        driver.execute_script(js)  # 将滚动条移动到页面的底部
        time.sleep(2)
        try:
            more = driver.find_element_by_css_selector('#moreCinema').get_attribute('class')
        except:
            """要是try内获取到的more是'more hide'，则下一次循环判断时自然会跳出，所以这里不需要操作"""
            continue

    html = driver.page_source
    xpath_parser = etree.HTML(html)

    # 影院名字列表
    name_list = xpath_parser.xpath('//p[@class="title"]//span/text()')
    # 影院链接地址列表，只需要cinemaId即可
    url_list = xpath_parser.xpath('//p[@class="title"]//span//@data-data')
    # 影院所在地址列表
    address_list = xpath_parser.xpath('//p[@class="addr clearfix"]//span/text()')

    if len(name_list) != 0:
        for j in range(len(name_list)):
            # 三个List的长度相等
            info = {
                'city': city,
                'name': name_list[j],
                'url': cinema_url.format(cityId,re.search('\d+',url_list[j]).group(0)),
                'address': address_list[j]
            }
            NuoMi.insert(info)  # 保存到mongodb
        print(city, " 影院列表\n", name_list)
        print()
    else:
        print(city, " 没有影院\n")
        print()

def crawl():
    NuoMi.delete()
    print(">>>>>>>>>>>>>>>>>>开始爬取糯米影院信息>>>>>>>>>>>>>>>>>>>>")
    driver.get(citys_url)
    html = driver.page_source
    xpath_parser = etree.HTML(html)
    """拼音首字母为A-B的城市"""
    all_city = xpath_parser.xpath(
        '//li[@class="city-list clearfix"][position()<=2]//ul[@class="cities fl"]//li//a/@data-id')
    city_count = len(all_city)
    print("糯米共", city_count, "个城市")

    pool = Pool()
    # pool.map(get_cinemas, (cityId for cityId in all_city))
    for cityId in all_city:
        pool.apply_async(get_cinemas, (cityId,))
    pool.close()
    pool.join()
    print("<<<<<<<<<<<<<<<<<<糯米影院信息爬取完成<<<<<<<<<<<<<<<<<<<\n\n\n")
    driver.quit()
    NuoMi.disconnect()  # 断开连接

# Thu Apr 18 21:22:38 2019
#  Thu Apr 18 21:23:02 2019