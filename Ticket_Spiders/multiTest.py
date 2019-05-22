"""
爬去时光网电影的电影票
Edit By RanFeng
"""
import re
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import sys,os
sys.path.append(os.getcwd())
from lxml import etree
from multiprocessing import Pool
import requests


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless') #无界面运行（无窗口）
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)


def get_showInfo(cinemas):
    """
    根据影院链接地址获取每部电影排片信息
    :param cinema_url: 电影院链接地址
    :return: 排片信息
    """
    with open('ticket_shiguang.txt', 'a', encoding='utf-8') as f:
        for cinema in cinemas:
            print(cinema)
            pass
            # flag = 0
    #             # city, cinema_url, string_id, cinema_id, cinema_name = \
    #             #     cinema['city'], cinema['url'], cinema['stringId'], cinema['cinemaId'], cinema['name']
    #             # try:
    #             #     driver.get(cinema_url)
    #             # except:
    #             #     flag = 1
    #             # if flag == 0:
    #             #     html = driver.page_source
    #             #     xpath_parser = etree.HTML(html)
    #             #     cinema_date_urls = xpath_parser.xpath('//ul[@id="valueDateRegion"]/li/a/@href')  #每个日期有不同的链接地址
    #             #     dates = []
    #             #     for i in range(len(cinema_date_urls)): #获取放映时间，形式于"今天 2月28日"这种格式
    #             #         date = xpath_parser.xpath('//ul[@id="valueDateRegion"]/li/a')[i].text + \
    #             #                xpath_parser.xpath('//ul[@id="valueDateRegion"]/li/a/b')[i].text
    #             #         dates.append(date)
    #             #     shows = [] #该影院每天每部电影的排片信息
    #             #     for i in range(len(cinema_date_urls)): #对该影院每一天的排片信息进行爬取
    #             #         date = re.search(r'\?d=(\d)+', cinema_date_urls[i]).group(1) #形似于"20190228"这种格式
    #             #         api = cinemaApi.format(string_id,cinema_id,date,cinema_id,date)
    #             #         html = requests.get(api).text
    #             #         data = re.sub(r'var result_(\d)+ = ', "", html)
    #             #         data = re.sub(r';var GetShowtimesJsonObjectByCinemaResult=result_(\d)+;', "", data)
    #             #         data = data.replace('true', '"true"').replace('false', '"false"').replace('null', '"null"').\
    #             #                     replace('new Date(', "").replace(')', "")
    #             #         data = eval(data)
    #             #         value = data["value"] #该影院某一天的所有电影的排片信息在里面
    #             #
    #             #         if value["movies"] != []:
    #             #             print(cinema_id,"有排片信息", api)
    #             #             if i == 0: #只有获取该影院第一天的排片的时候才向shows中插入一条影片信息，防止后续天的干扰
    #             #                 for movie in value["movies"]:
    #             #                     movieId = movie["movieId"]
    #             #                     movieName = movie["movieTitleCn"]
    #             #                     moviePic = movie["coverSrc"]
    #             #                     bigRating = movie["bigRating"]
    #             #                     smallRating = movie["smallRating"]
    #             #                     score = str(bigRating) + '.' + str(smallRating)
    #             #                     score = score if score != "-1.0" else ""
    #             #                     info = {
    #             #                         'city': city,
    #             #                         'url': cinema_url,
    #             #                         'movieId': movieId,
    #             #                         'name': movieName,
    #             #                         'picture': moviePic,
    #             #                         'score': score,
    #             #                         'date': dates,
    #             #                         'plist': {}
    #             #                     }
    #             #                     for date in dates:
    #             #                         info['plist'][date] = []
    #             #                     shows.append(info) #这样shows中的每一条记录中就只有排片信息未填充
    #             #             showTimes = value["showtimes"]
    #             #             curdate = dates[i]
    #             #             for showtime in showTimes:
    #             #                 movieId = showtime["movieId"]
    #             #                 for show in shows:
    #             #                     if show["movieId"] == movieId:
    #             #                         begin_time = re.search(r'(\d){2}:(\d){2}', showtime["realtime"]).group()
    #             #                         end_time = showtime["movieEndTime"]
    #             #                         language = showtime["language"]
    #             #                         hall = showtime["hallName"]
    #             #                         price = showtime["mtimePrice"]
    #             #                         perTime = {  # 一条排片信息
    #             #                             'begin-time': begin_time,
    #             #                             'end-time': end_time,
    #             #                             'language': language,
    #             #                             'hall': hall,
    #             #                             'price': price
    #             #                         }
    #             #                         show["plist"][curdate].append(perTime)
    #             #                         break
    #             #         else:
    #             #             print(cinema_id,"没有排片信息", api)
    #             #     for show in shows:
    #             #         show.pop('movieId')
    #             #         f.write(str(show) + "\n")


    driver.quit()



if __name__ == '__main__':
    """一家电影院某一天所有上映电影的排片信息API"""
    cinemaApi = "http://service.theater.mtime.com/Cinema.api?Ajax_CallBack=true" \
                "&Ajax_CallBackType=Mtime.Cinema.Services&Ajax_CallBackMethod=GetShowtimesJsonObjectByCinemaId" \
                "&Ajax_CrossDomain=1&Ajax_RequestUrl=http%3A%2F%2Ftheater.mtime.com%2F{}%2F{}%2F%3Fd%3D{}" \
                "&t=201922720461284724&Ajax_CallBackArgument0={}&Ajax_CallBackArgument1={}"

    pool = Pool()
    cinemas = []
    with open('cinema_shiguang.txt', 'r', encoding='utf-8') as f:
        for line in f.readlines():
            cinema = eval(line)
            item = {
                'city' : cinema['city'],
                'url' : cinema['url'],
                'stringId' : cinema['stringId'],
                'cinemaId' : cinema['cinemaId'],
                'name' : cinema['name']
            }
            cinemas.append(item)
    pool.map(get_showInfo, cinemas)