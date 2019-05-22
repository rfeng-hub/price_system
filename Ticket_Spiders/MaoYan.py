"""
爬去猫眼电影的电影票
Edit By RanFeng
"""
from fontTools.ttLib import TTFont
import xml.dom.minidom as xmldom
import re
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from lxml import etree
import sys,os
sys.path.append(os.getcwd())
from database.cinema import mongo as mao_cinema
from database.ticket import mongo as mao_ticket
from setting import CINEMA_MAO_COLLECTION,TICKET_MAO_COLLECTION
from multiprocessing import Pool

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)
# driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)
cinema = mao_cinema(CINEMA_MAO_COLLECTION)
ticket = mao_ticket(TICKET_MAO_COLLECTION)

def getValue(node, attribute):
    return node.attributes[attribute].value

def getTTGlyphList(xml_path):
    dataXmlfilepath = os.path.abspath(xml_path)
    dataDomObj = xmldom.parse(dataXmlfilepath)
    dataElementObj = dataDomObj.documentElement
    dataTTGlyphList = dataElementObj.getElementsByTagName('TTGlyph')
    return dataTTGlyphList

def isEqual(ttglyph_a, ttglyph_b):
    a_pt_list = ttglyph_a.getElementsByTagName('pt')
    b_pt_list = ttglyph_b.getElementsByTagName('pt')
    a_len = len(a_pt_list)
    b_len = len(b_pt_list)
    if a_len != b_len:
        return False
    for i in range(a_len):
        if getValue(a_pt_list[i], 'x') != getValue(b_pt_list[i], 'x') or getValue(a_pt_list[i], 'y') != getValue(
                b_pt_list[i], 'y') or getValue(a_pt_list[i], 'on') != getValue(b_pt_list[i], 'on'):
            return False
    return True

def refresh(dict, ttGlyphList_a, ttGlyphList_data):
    data_dict = {"uniE0A9": "0", "uniEF4F": "1", "uniEAEE": "2", "uniEB0C": "3", "uniE517": "4",
                 "uniF1F8": "5", "uniF798": "6", "uniF346": "7", "uniE11A": "8", "uniEE4F": "9"}
    data_keys = data_dict.keys()
    for ttglyph_data in ttGlyphList_data:
        if getValue(ttglyph_data, 'name') in data_keys:
            for ttglyph_a in ttGlyphList_a:
                if isEqual(ttglyph_a, ttglyph_data):
                    dict[getValue(ttglyph_a, 'name')] = data_dict[getValue(ttglyph_data, 'name')]
                    break
    return dict

def decode(decode_dict, code):
    _lst_uincode = []
    for item in code.__repr__().split("\\u"):
        _lst_uincode.append("uni" + item[:4].upper())
        if item[4:]:
            _lst_uincode.append(item[4:])
    _lst_uincode = _lst_uincode[1:-1]
    result = "".join([str(decode_dict[i]) for i in _lst_uincode])
    return result

def getInfo(item):
    city, cinema_url, cinema_name, address = item['city'], item['url'], item['name'], item['address']
    try:
        driver.get(cinema_url)
        html = driver.page_source
        xpath_parser = etree.HTML(html)
        # 下载字体文件
        style = xpath_parser.xpath('//head/style[1]/text()')[0]
        pattern = re.compile('//vfile.meituan.net/colorstone/(\w)+?\.woff')
        font_url = 'https:' + pattern.search(style).group()
        # print(font_url)
        woff_path = 'Ticket_Spiders/tmp.woff'
        f = requests.get(font_url)
        data = f.content
        with open(woff_path, "wb") as code:
            code.write(data)
        # 分析解码字典
        font1 = TTFont('Ticket_Spiders/tmp.woff')
        font1.saveXML('Ticket_Spiders/tmp.xml')

        """由于每次的unicode码是随机生成的，因此还需要知道新的0-9对应的unicode码是多少"""
        decode_dict = dict(enumerate(font1.getGlyphOrder()[2:]))
        decode_dict = dict(zip(decode_dict.values(), decode_dict.keys()))

        """获取已知映射关系的data.xml的字体数据节点和新的动态字体文件的数据节点"""
        dataTTGlyphList = getTTGlyphList("Ticket_Spiders/data.xml")
        tmpTTGlyphList = getTTGlyphList("Ticket_Spiders/tmp.xml")
        """利用字体数据更新映射字典"""
        decode_dict = refresh(decode_dict, tmpTTGlyphList, dataTTGlyphList)
        decode_dict['.'] = '.'
        # print(decode_dict)

        phone = xpath_parser.xpath('//div[@class="telphone"]/text()')[0].strip().replace("电话：","")
        movie_list = xpath_parser.xpath('//div[@class="movie-list"]//img/@src')
        show_list = xpath_parser.xpath('//div[contains(@class,"show-list")]')  # 所有电影及其排片信息
        for num in range(len(show_list)):
            """电影信息"""
            name = show_list[num].xpath('./div[@class="movie-info"]//h3[@class="movie-name"]/text()')[0]
            score = show_list[num].xpath('./div[@class="movie-info"]//span[@class="score sc"]/text()')
            score = score[0] if score != [] else "暂无评分" # 有可能暂无评分
            date = show_list[num].xpath('./div[@class="show-date"]//span/text()')
            date.pop(0)  # 删除“观影时间 :”
            for index in range(len(date)):
                date[index] = date[index].replace(" ","") + "日"

            """排片信息"""
            plist_container = show_list[num].xpath('./div[contains(@class,"plist-container")]')  # 接下来几天的排片信息在里面，长度为排片天数
            infos = {}  # 多天的排片信息
            for i in range(len(plist_container)):
                day = []  # 一天的排片信息
                plist = plist_container[i].xpath('./table//tbody//tr')  # 某天的每一条排片信息
                for p in plist:
                    begin_time = p.xpath('./td[1]//span[@class="begin-time"]/text()')[0].strip()
                    end_time = p.xpath('./td[1]//span[@class="end-time"]/text()')[0].strip()
                    language = p.xpath('./td[2]/span[@class="lang"]/text()')[0].strip()
                    hall = p.xpath('./td[3]/span[@class="hall"]/text()')[0].strip()
                    price = p.xpath('./td[4]/span[@class="sell-price"]//span/text()')[0]
                    price = decode(decode_dict, price) #解码
                    perTime = {  # 一条排片信息
                        'begin-time': begin_time,
                        'end-time': end_time,
                        'language': language,
                        'hall': hall,
                        'price': price
                    }
                    day.append(perTime)
                if day != []:  # 该电影在这一天有排片
                    infos[date[i]] = day
            if infos != {}:  # 该电影有排片
                movie = {
                    'city': city,
                    'url': cinema_url,
                    'cinema_name' : cinema_name,
                    'address' : address,
                    'phone' : phone,
                    'name': name,
                    'score': score,
                    'image': movie_list[num],
                    'date': date,
                    'plist': infos
                }
                print(movie)
                ticket.insert(movie)
    except:
        print(cinema_url, "连接失败")

def crawl():
    ticket.delete()  # 抓取排片信息前先删除集合
    pool = Pool()
    print(">>>>>>>>>>>>>>>>>开始爬取猫眼排片信息>>>>>>>>>>>>>")
    pool.map(getInfo, (item for item in cinema.findAll()))
    pool.close()
    print("<<<<<<<<<<<<<<<<<猫眼排片信息爬取完成！<<<<<<<<<<<<<<<<<<<<\n\n\n")
    driver.quit()

    cinema.disconnect()
    ticket.disconnect()

