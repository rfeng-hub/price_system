"""
爬去糯米电影的电影票
Edit By RanFeng
"""
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from lxml import etree
import time
import sys,os
sys.path.append(os.getcwd())
from database.cinema import mongo as nuo_cinema
from database.ticket import mongo as nuo_ticket
from setting import CINEMA_NUO_COLLECTION,TICKET_NUO_COLLECTION
from multiprocessing import Pool

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
# chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
# chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)
# driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)
cinema = nuo_cinema(CINEMA_NUO_COLLECTION)
ticket = nuo_ticket(TICKET_NUO_COLLECTION)

def get_showInfo(item):
    """
    根据影院链接地址获取每部电影排片信息
    :param cinema_url: 电影院链接地址
    :return: 排片信息
    """
    city, cinema_url, cinema_name, address = item['city'], item['url'], item['name'], item['address']
    try:
        driver.get(cinema_url)
        time.sleep(1) #睡一会儿，不然网页加载不全
        html = driver.page_source
        xpath_parser = etree.HTML(html)
        phone = xpath_parser.xpath('//p[@class="addr font-grey"]/text()')
        phone = phone[1].strip() if len(phone) == 2 else [] # 有些影院没有给出联系电话
        show_list = xpath_parser.xpath('//ul[@class="slides"]//li') #所有电影的信息
        datelist = xpath_parser.xpath('//div[@id="datelist"]/div[contains(@class,"date")]')  # 所有电影的排片信息
        if show_list == []:
            print(city,cinema_url,"没有影讯信息")
        else:
            # movie_list = xpath_parser.xpath('//ul[@class="slides"]//img/@src') # 电影名
            for i in range(len(datelist)):
                """电影信息"""
                if show_list[i].xpath('@class') != ['empty']:
                    name = show_list[i].xpath('./div[@class="info"]//p/text()')[0].strip()
                    score = show_list[i].xpath('./div[@class="info"]//span[1]/text()')
                    score = score[0] if score != [] else "暂无评分"  # 有可能暂无评分
                    infos = {}  # 该电影多天的排片信息
                    date = datelist[i].xpath('./div[@class="datelist"]/span/text()')  # 该电影哪几天有排片
                    for j in range(len(date)):
                        date[j] = date[j].strip()
                    plist = datelist[i].xpath('./div[contains(@class,"session-list")]')  # 该电影这几天的排片
                    for k in range(len(plist)):
                        """排片信息"""
                        day = []  # 一天的排片信息
                        lis = plist[k].xpath('./ul/li')  # 该电影这一天的排片
                        for li in lis:
                            if li.xpath('@class')[0] == "text-center":
                                break
                            else:
                                start_time = li.xpath('./div[@class="time fl"]/p[1]/text()')[0].strip()
                                end_time = li.xpath('./div[@class="time fl"]/p[2]/text()')[0].strip()
                                language = li.xpath('./div[@class="type fl font14"]/text()')[0].strip()
                                hall = li.xpath('./div[@class="hall fl font14"]/text()')[0].strip()
                                price = li.xpath('./div[@class="price fl"]//span[@class="num nuomi-red"]/text()')[0].strip()
                                perTime = {  # 一条排片信息
                                    'begin-time': start_time,
                                    'end-time': end_time,
                                    'language': language,
                                    'hall': hall,
                                    'price': price
                                }
                                day.append(perTime)

                        if day != []: #该电影在这一天有排片
                            infos[date[k]] = day

                    if infos != {}: #该电影有排片
                        movie = { #一部电影的排片信息
                            'city' : city,
                            'url': cinema_url,
                            'cinema_name' : cinema_name,
                            'address' : address,
                            'phone' : phone,
                            'name': name,
                            'score': score,
                            'date': date,
                            'plist': infos
                        }
                        print(movie)
                        # log.write(str(num) + str(movie) + "\n")
                        ticket.insert(movie)
                    else:
                        print(city, cinema_url, "没有影讯信息")
    except:
        print(cinema_url, "连接失败")


def crawl():
    ticket.delete()  # 抓取排片信息前先删除集合
    pool = Pool()
    print(">>>>>>>>>>>>>>>>>开始爬取糯米排片信息>>>>>>>>>>>>>")
    pool.map(get_showInfo, (item for item in cinema.findAll()))
    pool.close()
    print(">>>>>>>>>>>>>>>>>糯米排片信息爬取完成！>>>>>>>>>>>>>\n\n\n")
    driver.quit()  # 不关闭的话，chrome进程会一直在后台，占用大量内存

    cinema.disconnect()
    ticket.disconnect()