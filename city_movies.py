"""
通过豆瓣api获取正在热映的电影
Edit By RanFeng
"""
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from lxml import etree
import time
import sys,os
sys.path.append(os.getcwd())
from database.movie import mongo
from setting import MOVIE_COLLECTION

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless') #无界面运行（无窗口）
chrome_options.add_argument('--no-sandbox') #取消沙盒模式
chrome_options.add_argument('--disable-gpu') #谷歌文档提到需要加上这个属性来规避bug
driver = webdriver.Chrome(options=chrome_options)
# driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)
base_url = 'https://maoyan.com/films?'
movie = mongo(MOVIE_COLLECTION)

def get_movies(num):
    try:
        driver.get(base_url)
        # 依次展开城市列表后点击每一个城市
        driver.find_element_by_xpath('//div[@class="city-name"]').click()  # 展开城市列表

        driver.find_elements_by_xpath('//div[@class="city-list"]//a[@class="js-city-name"]')[num].click()  # 点击城市

        time.sleep(4)  # 睡一会儿，不然下一个点击事件有可能无法响应
        js = "window.scrollTo(0, 0)"
        driver.execute_script(js)  # 现将进度条拉到顶部，防止后续定位不到“全部”按钮

        # 影院所属城市
        city = driver.find_element_by_css_selector('.city-selected .city-name').text
        html = driver.page_source
        xpath_parser = etree.HTML(html)

        movie_images_pre = xpath_parser.xpath('//div[@class="movie-item"]//img[2]') # 电影图片
        movie_names = xpath_parser.xpath('//div[@class="channel-detail movie-item-title"]/@title') # 电影名
        movie_scores_pre = xpath_parser.xpath('//div[@class="channel-detail channel-detail-orange"]') # 电影评分
        images, scores = [], []

        for image in movie_images_pre:
            if image.xpath('@src') != []:
                images.extend(image.xpath('@src'))
            else:
                images.extend(image.xpath('@data-src'))
        for score in movie_scores_pre:
            number = score.xpath('./child::i/text()') # 查找当前节点下子节点要加child::
            number = number[0] + number[1] if number != [] else "暂无评分"
            scores.append(number)

        item = {
            'city': city,
            'movies': {}
        }
        for l in range(len(movie_names)):
            item['movies'][movie_names[l]] = {}
            item['movies'][movie_names[l]]['score'] = scores[l]
            item['movies'][movie_names[l]]['image'] = images[l]
        print(city, movie_names)
        return item
    except:
        print(num,"当前城市没有热映电影")

def crawl():
    movie.delete()
    """获取每个城市热映的电影"""
    print(">>>>>>>>>>>>>>>>>开始爬取城市-电影信息>>>>>>>>>>>>>")
    driver.get(base_url)
    driver.find_element_by_xpath('//div[@class="city-name"]').click()  # 展开城市列表
    html = driver.page_source
    xpath_parser = etree.HTML(html)
    Count = 0
    for i in range(1,3): # A-B的城市
        key = xpath_parser.xpath('//div[@class="city-list"]//li[position()={}]/span/text()'.format(i))[0] # 城市所属字母
        all_city = xpath_parser.xpath('//div[@class="city-list"]//li[position()={}]//a[@class="js-city-name"]'.format(i))
        city_count = len(all_city)  # 拼音首字母为*的城市总数
        print("第", i, "部分共", city_count, "个城市")
        item = {
            'key': key,
            'cities': [],
            'c_m':{}
        }
        for j in range(Count, Count + city_count):
            c_movie = get_movies(j)
            item['cities'].append(c_movie['city'])
            item['c_m'][c_movie['city']] = c_movie['movies']

        movie.insert(item)
        Count += city_count

    print("<<<<<<<<<<<<<<<<<城市-电影信息爬取完成！<<<<<<<<<<<<<<<<<<<<\n\n\n")
    driver.quit()
    movie.disconnect()  # 断开连接