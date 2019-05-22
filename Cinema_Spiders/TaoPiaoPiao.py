"""
获取淘票票电影院链接地址等信息，作为基本信息保存到数据库
Edit by RanFeng
"""
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from lxml import etree
import time
import json
import re
import sys,os
sys.path.append(os.getcwd())
from database.cinema import mongo
from setting import CINEMA_TAO_COLLECTION


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless') #无界面运行（无窗口）
# chrome_options.add_argument('--start-maximized') #最大化运行（全屏窗口）
# chrome_options.add_argument('--no-sandbox') #取消沙盒模式
chrome_options.add_argument('--disable-gpu') #谷歌文档提到需要加上这个属性来规避bug
# chrome_options.add_argument('disable-infobars')#禁用浏览器正在被自动化程序控制的提示
# chrome_options.add_argument('--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"')
# chrome_options.add_argument('blink-settings=imagesEnabled=false') #不加载图片
# prefs = {
#     'profile.default_content_setting_values' :  {
#         'notifications' : 2
#      }
# }
# chrome_options.add_experimental_option('prefs',prefs) #禁止弹窗
# chrome_options.add_argument("--proxy-server=http://" + ip：port) #添加代理
driver = webdriver.Chrome(options=chrome_options)
# driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)
base_url = 'https://www.taopiaopiao.com/'
cinemas_url = 'https://www.taopiaopiao.com/cinemaList.htm?'

def get_cinemas():

    """获取全国城市总数"""
    city_json = "https://www.taopiaopiao.com/cityAction.json?activityId&_ksTS=1550457279536_84&jsoncallback=jsonp85&action=cityAction&n_s=new&event_submit_doGetAllRegion=true"
    driver.get(city_json)
    jsonp = driver.page_source
    pattern = re.compile(r'{"returnCode.+]}}')
    content = pattern.search(jsonp).group()
    content = json.loads(content)
    city_urls = []
    city_url = "https://www.taopiaopiao.com/cinemaList.htm?city={}"
    for i in content['returnValue'].keys():
        if i <= 'B':
            for city in content['returnValue'][i]:
                city_urls.append(city_url.format(city['cityCode']))

    tao = mongo(CINEMA_TAO_COLLECTION)
    for i in range(len(city_urls)):
        driver.get(city_urls[i])
        js = "window.scrollTo(0, 0)"
        driver.execute_script(js)  # 现将进度条拉到顶部，防止后续定位不到“全部”按钮

        # 影院所属城市
        city = driver.find_element_by_css_selector('.cityName .name').text
        area_all = ""
        try:
            area_all = driver.find_element_by_css_selector('.select-tags a').text
        except:
            print(i, city, " 没有电影院")

        if area_all != "":
            # 每次选中一个城市后，点击“选择区域”处的“全部区域”按钮即可跳转展示电影院列表第一页
            driver.find_element_by_css_selector('.select-tags a').click()
            time.sleep(2)

            js = "window.scrollTo(0, document.body.scrollHeight)"
            driver.execute_script(js)  # 将滚动条移动到页面的底部

            try:
                """叉掉广告"""
                driver.find_element_by_xpath(
                    '//div[@class="J_sBanner sBanner-container"]//a[@class="J_closeIcon close-icon"]').click()
            except:
                print("没有广告了")

            """影院列表有折叠隐藏，需要点击显示更多"""
            try:
                more = driver.find_element_by_css_selector('[class="sortbar-more J_cinemaMore"]').get_attribute("style")
            except:
                more = "display: none;"
            while more != "display: none;":
                driver.find_element_by_xpath('//div[@class="sortbar-more J_cinemaMore"]//div').click()
                driver.execute_script(js)  # 将滚动条移动到页面的底部
                time.sleep(1)
                try:
                    more = driver.find_element_by_css_selector('[class="sortbar-more J_cinemaMore"]').get_attribute(
                        "style")
                except:
                    more = "display: none;"

            html = driver.page_source
            xpath_parser = etree.HTML(html)
            # 影院名字列表
            name_list = xpath_parser.xpath(
                '//div[@class="detail-middle"]//div[@class="middle-hd"]//a/text()')
            # 影院链接地址列表
            url_list = xpath_parser.xpath(
                '//div[@class="detail-middle"]//div[@class="middle-hd"]//a//@href')
            # 影院所在地址列表
            address_list = xpath_parser.xpath(
                '//div[@class="middle-p"]//div[1]//span/text()')

            for j in range(len(name_list)):
                """三个List的长度相等"""
                info = {
                    'city': city,
                    'name': name_list[j],
                    'url': url_list[j],
                    'address': address_list[j]
                }
                tao.insert(info)  # 保存到mongodb
            print(i, city," 影院列表\n",name_list)
        print()

    driver.quit()
    tao.disconnect() #断开连接

get_cinemas()