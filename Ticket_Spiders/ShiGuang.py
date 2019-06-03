"""
爬取时光网电影的电影票
Edit By RanFeng
"""
import re
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import sys,os
sys.path.append(os.getcwd())
from database.cinema import mongo as shi_cinema
from database.ticket import mongo as shi_ticket
from setting import CINEMA_SHI_COLLECTION,TICKET_SHI_COLLECTION
from lxml import etree
from multiprocessing import Pool

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
wait = WebDriverWait(driver, 10)

"""一家电影院某一天所有上映电影的排片信息API"""
cinemaApi = "http://service.theater.mtime.com/Cinema.api?Ajax_CallBack=true" \
            "&Ajax_CallBackType=Mtime.Cinema.Services&Ajax_CallBackMethod=GetShowtimesJsonObjectByCinemaId" \
            "&Ajax_CrossDomain=1&Ajax_RequestUrl=http%3A%2F%2Ftheater.mtime.com%2F{}%2F{}%2F%3Fd%3D{}" \
            "&t=201922720461284724&Ajax_CallBackArgument0={}&Ajax_CallBackArgument1={}"


cinema = shi_cinema(CINEMA_SHI_COLLECTION)
ticket = shi_ticket(TICKET_SHI_COLLECTION)

def get_data_api(item):
    """
    根据影院链接地址获取每部电影排片信息
    :param cinema_url: 电影院链接地址
    :return: 排片信息
    """
    city, cinema_url, string_id, cinema_id, cinema_name = \
        item['city'], item['url'], item['stringId'], item['cinemaId'], item['name']
    # try:
    driver.get(cinema_url)
    html = driver.page_source
    xpath_parser = etree.HTML(html)
    address = xpath_parser.xpath('//div[@class="ci_title"]/p/text()')[1].strip()
    phone = xpath_parser.xpath('//div[@class="ci_title"]/p/text()')[3].strip().replace("电话：","")
    cinema_date_urls = xpath_parser.xpath('//ul[@id="valueDateRegion"]/li/a/@href')  #每个日期有不同的链接地址

    dates = []
    for i in range(len(cinema_date_urls)): #获取放映时间，形式于"今天 2月28日"这种格式
        date = xpath_parser.xpath('//ul[@id="valueDateRegion"]/li/a')[i].text + \
               xpath_parser.xpath('//ul[@id="valueDateRegion"]/li/a/b')[i].text
        dates.append(date)
    shows = [] #该影院每天每部电影的排片信息
    for j in range(len(cinema_date_urls)): #对该影院每一天的排片信息进行爬取
        date = re.search(r'\?d=(\d+)', cinema_date_urls[j]).group(1) #形似于"20190228"这种格式
        api = cinemaApi.format(string_id,cinema_id,date,cinema_id,date)
        # html = requests.get(api).text
        driver.get(api)
        html = driver.find_element_by_tag_name('pre').text

        data = re.sub(r'var result_(\d)+ = ', "", html)
        data = re.sub(r';var GetShowtimesJsonObjectByCinemaResult=result_(\d)+;', "", data)
        data = data.replace('true', '"true"').replace('false', '"false"').replace('null', '"null"').\
                    replace('new Date(', "").replace(')', "")
        data = eval(data)
        value = data["value"] #该影院某一天的所有电影的排片信息在里面

        if value["movies"] != []:
            print("有排片信息", api)
            for movie in value["movies"]:
                movieName = movie["movieTitleCn"]
                flag = 0 # 该电影的排片未加入到shows中
                for show in shows:
                    if show['name'] == movieName:
                        flag = 1 # shows中已有该电影之前天的排片
                        break
                if flag == 0: # 不在，初始化一部电影的排片
                    movieId = movie["movieId"]
                    bigRating = movie["bigRating"] #大分
                    smallRating = movie["smallRating"] # 小分
                    score = str(bigRating) + '.' + str(smallRating)
                    info = {
                        'city': city,
                        'url': cinema_url,
                        'cinema_name' : cinema_name,
                        'address': address,
                        'phone': phone,
                        'movieId': movieId,
                        'name': movieName,
                        'score': score,
                        'date': [],
                        'plist': {}
                    }
                    shows.append(info) #这样shows中的每一条记录中就只有排片信息未填充

            showTimes = value["showtimes"]
            curdate = dates[j]
            for showtime in showTimes: # 这一天的所有排片
                movieId = showtime["movieId"]
                for show in shows:
                    if show["movieId"] == movieId:
                        if curdate not in show['plist']:
                            show["plist"][curdate] = [] # 第一次插入每部电影每天的排片都需要初始化
                            show['date'].append(curdate)
                        begin_time = re.search(r'(\d){2}:(\d){2}', showtime["realtime"]).group()
                        end_time = showtime["movieEndTime"]
                        language = showtime["language"]
                        hall = showtime["hallName"]
                        price = showtime["price"] if showtime["mtimePrice"] == 0 else showtime["mtimePrice"]
                        perTime = {  # 一条排片信息
                            'begin-time': begin_time,
                            'end-time': end_time,
                            'language': language,
                            'hall': hall,
                            'price': str(price)
                        }
                        show["plist"][curdate].append(perTime)
                        break
        else:
            print("没有排片信息", api)
            print(cinema_url)
    for show in shows:
        show.pop('movieId')
        ticket.insert(show)
    # except:
    #     print(cinema_url, "连接失败")


def crawl():
    ticket.delete()  # 抓取排片信息前先删除集合
    pool = Pool()
    # pool.map(get_data_api, (item for item in cinema.findAll()))
    print(">>>>>>>>>>>>>>>>>开始爬取时光排片信息>>>>>>>>>>>>>")
    for item in cinema.findAll():
        # get_data_api(item)
        pool.apply_async(get_data_api, (item,))
    pool.close()
    pool.join()
    print("<<<<<<<<<<<<<<<<<时光排片信息爬取完成！<<<<<<<<<<<<<<<<<<<<\n\n\n")
    driver.quit()

    cinema.disconnect()
    ticket.disconnect()


if __name__ == '__main__':
    crawl()