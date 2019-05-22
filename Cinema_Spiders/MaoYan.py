"""
获取猫眼电影院链接地址等信息，作为基本信息保存到数据库
Edit by RanFeng
"""
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from lxml import etree
import time
import sys,os
sys.path.append(os.getcwd())
from database.cinema import mongo
from setting import CINEMA_MAO_COLLECTION
import re
from multiprocessing import Pool

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless') #无界面运行（无窗口）
chrome_options.add_argument('--no-sandbox') #取消沙盒模式
chrome_options.add_argument('--disable-gpu') #谷歌文档提到需要加上这个属性来规避bug
driver = webdriver.Chrome(options=chrome_options) # 实际使用
# driver = webdriver.Chrome() # 测试时使用
wait = WebDriverWait(driver, 10)
base_url = 'https://maoyan.com'
cinemas_url = 'https://maoyan.com/cinemas'
maoyan = mongo(CINEMA_MAO_COLLECTION)

def get_cinemas(i):
    driver.get(cinemas_url)
    #依次展开城市列表后点击每一个城市
    driver.find_element_by_xpath('//div[@class="city-name"]').click() #展开城市列表
    try:
        driver.find_elements_by_xpath('//div[@class="city-list"]//a[@class="js-city-name"]')[i].click() #点击城市
        time.sleep(4)  # 睡一会儿，不然下一个点击事件有可能无法响应
        js = "window.scrollTo(0, 0)"
        driver.execute_script(js)  # 现将进度条拉到顶部，防止后续定位不到“全部”按钮

        # 影院所属城市
        city = driver.find_element_by_css_selector('.city-selected .city-name').text
        brand_all = ""
        try:
            brand_all = driver.find_element_by_css_selector('.tags-line .active a').text
        except:
            print(city, " 没有电影院")

        if brand_all != "":
            # 每次选中一个城市后，点击“品牌”处的“全部”按钮即可跳转展示电影院列表第一页
            driver.find_element_by_css_selector('.tags-line .active a').click()
            time.sleep(3)

            js = "window.scrollTo(0, document.body.scrollHeight)"
            driver.execute_script(js)  # 将滚动条移动到页面的底部

            try:
                page_count = driver.find_element_by_css_selector('.list-pager li:nth-last-child(2) a').text
                page_count = int(page_count)
            except:
                page_count = 1

            if page_count != 1:
                """影院列表有多页"""
                print(city, " 共", page_count, "页")
                for j in range(int(page_count)):
                    print("第", j + 1, "页")
                    html = driver.page_source
                    xpath_parser = etree.HTML(html)

                    # 影院名字列表
                    name_list = xpath_parser.xpath(
                        '//div[@class="cinemas-list"]//div[@class="cinema-cell"]//div[@class="cinema-info"]//a/text()')
                    # 影院链接地址列表
                    url_list = xpath_parser.xpath(
                        '//div[@class="cinemas-list"]//div[@class="cinema-cell"]//div[@class="cinema-info"]//a//@href')
                    # 影院所在地址列表
                    address_list = xpath_parser.xpath(
                        '//div[@class="cinemas-list"]//div[@class="cinema-cell"]//div[@class="cinema-info"]//p/text()')

                    for k in range(len(name_list)):
                        """三个List的长度相等"""
                        info = {
                            'city': city,
                            'name': name_list[k],
                            'url': base_url + url_list[k],
                            'address': re.sub(r"地址：", "", address_list[k])
                        }
                        maoyan.insert(info)  # 保存到mongodb
                    print(name_list)

                    driver.find_element_by_css_selector('.list-pager li:nth-last-child(1)').click()  # 下一页
                    time.sleep(4)
            else:
                """列表只有 1 页"""
                js = "window.scrollTo(0, 0)"
                driver.execute_script(js)  # 现将进度条拉到顶部，防止后续定位不到“全部”按钮
                # 每次选中一个城市后，点击“品牌”处的“全部”按钮即可跳转展示电影院列表第一页
                driver.find_element_by_css_selector('.tags-line .active a').click()

                js = "window.scrollTo(0, document.body.scrollHeight)"
                driver.execute_script(js)  # 将滚动条移动到页面的底部

                print(city, " 只有一页")
                html = driver.page_source
                xpath_parser = etree.HTML(html)

                # 影院名字列表
                name_list = xpath_parser.xpath(
                    '//div[@class="cinemas-list"]//div[@class="cinema-cell"]//div[@class="cinema-info"]//a/text()')
                # 影院链接地址列表
                url_list = xpath_parser.xpath(
                    '//div[@class="cinemas-list"]//div[@class="cinema-cell"]//div[@class="cinema-info"]//a//@href')
                # 影院所在地址列表
                address_list = xpath_parser.xpath(
                    '//div[@class="cinemas-list"]//div[@class="cinema-cell"]//div[@class="cinema-info"]//p/text()')
                print(name_list)

                for j in range(len(name_list)):
                    """三个List的长度相等"""
                    info = {
                        'city': city,
                        'name': name_list[j],
                        'url': base_url + url_list[j],
                        'address': re.sub(r"地址：", "", address_list[j])
                    }
                    maoyan.insert(info)  # 保存到mongodb
    except:
        print("点击城市失败")

    print()


def crawl():
    maoyan.delete()
    """获取全国城市总数"""
    print(">>>>>>>>>>>>>>>>>开始爬取猫眼影院信息>>>>>>>>>>>>>")
    driver.get(cinemas_url)
    # actions = ActionChains(driver)
    # city_tag = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="city-name"]')))  # 定位城市
    # actions.click(city_tag).perform() #展开城市列表
    driver.find_element_by_xpath('//div[@class="city-name"]').click()  # 展开城市列表
    html = driver.page_source
    xpath_parser = etree.HTML(html)
    all_city = xpath_parser.xpath('//div[@class="city-list"]//li[position()<=2]//a[@class="js-city-name"]')
    city_count = len(all_city)  # 拼音首字母为A-B的城市总数
    print("猫眼共", city_count, "个城市")

    pool = Pool()
    pool.map(get_cinemas, (i for i in range(city_count)))
    pool.close()
    print("<<<<<<<<<<<<<<<<<猫眼影院信息爬取完成！<<<<<<<<<<<<<<<<<<<<\n\n\n")
    driver.quit()
    maoyan.disconnect()  # 断开连接

# Fri Apr 19 08:49:18 2019 Fri Apr 19 08:50:23 2019
# Fri Apr 19 08:51:25 2019 Fri Apr 19 08:54:42 2019