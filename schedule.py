"""
调度数据抓取模块
"""
import gather_ticket
import os

def kill_chrome():
    """
    杀死chromedriver进程和chrome进程
    """
    os.system('taskkill /im chromedriver.exe /F')
    os.system('taskkill /im chrome.exe /F')

if __name__ == '__main__':
    import city_movies
    # 抓取城市-热映电影
    city_movies.crawl()
    kill_chrome()

    from Cinema_Spiders import MaoYan as M_mao, NuoMi as M_nuo, ShiGuang as M_shi
    # 爬取影院信息，作为基本数据，短期内不需要再次获取
    M_nuo.crawl()
    M_mao.crawl()
    kill_chrome()
    M_shi.crawl()

    from Ticket_Spiders import MaoYan as T_mao, NuoMi as T_nuo, ShiGuang as T_shi
    # 爬取电影排片信息
    T_mao.crawl()
    T_nuo.crawl()
    T_shi.crawl()
    kill_chrome()

    # 整合三个平台的电影排片信息
    gather_ticket.begin()