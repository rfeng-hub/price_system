# from setting import CINEMA_MAO_COLLECTION
# from database import cinema
# import pickle
#
# mao = cinema.mongo(CINEMA_MAO_COLLECTION)
# # cinemas = []
# # for item in mao.findAll():
# #     flag = 0
# #     for cinema in cinemas:
# #         if item['url'] == cinema['url']:
# #             flag = 1
# #             break
# #     if flag == 0:
# #         cinemas.append(item)
# #
# # with open("mao_cinema", 'wb') as f:
# #     pickle.dump(cinemas, f)
#
# with open("mao_cinema", 'rb') as f:
#     data = pickle.load(f)
#     for item in data:
#         mao.insert(item)

# import requests
#
# api = "http://m.maoyan.com/movie/list.json?type=hot&offset=0&limit=1000"
#
# html = requests.get(api).text
# print(html)

from lxml import etree

html = """<li>
                <span>A</span>
                <div>
                  <a class="js-city-name" data-ci="150" data-val="{ choosecityid:150 }" data-act="cityChange-click">阿拉善盟</a>
                  <a class="js-city-name" data-ci="151" data-val="{ choosecityid:151 }" data-act="cityChange-click">鞍山</a>
                  <a class="js-city-name" data-ci="197" data-val="{ choosecityid:197 }" data-act="cityChange-click">安庆</a>
                  <a class="js-city-name" data-ci="238" data-val="{ choosecityid:238 }" data-act="cityChange-click">安阳</a>
                  <a class="js-city-name" data-ci="319" data-val="{ choosecityid:319 }" data-act="cityChange-click">阿坝</a>
                  <a class="js-city-name" data-ci="324" data-val="{ choosecityid:324 }" data-act="cityChange-click">安顺</a>
                  <a class="js-city-name" data-ci="359" data-val="{ choosecityid:359 }" data-act="cityChange-click">安康</a>
                  <a class="js-city-name" data-ci="400" data-val="{ choosecityid:400 }" data-act="cityChange-click">阿勒泰</a>
                  <a class="js-city-name" data-ci="394" data-val="{ choosecityid:394 }" data-act="cityChange-click">阿克苏</a>
                  <a class="js-city-name" data-ci="490" data-val="{ choosecityid:490 }" data-act="cityChange-click">安吉</a>
                  <a class="js-city-name" data-ci="588" data-val="{ choosecityid:588 }" data-act="cityChange-click">安丘</a>
                  <a class="js-city-name" data-ci="699" data-val="{ choosecityid:699 }" data-act="cityChange-click">安岳</a>
                  <a class="js-city-name" data-ci="807" data-val="{ choosecityid:807 }" data-act="cityChange-click">安平</a>
                  <a class="js-city-name" data-ci="873" data-val="{ choosecityid:873 }" data-act="cityChange-click">安宁</a>
                  <a class="js-city-name" data-ci="844" data-val="{ choosecityid:844 }" data-act="cityChange-click">安溪</a>
                  <a class="js-city-name" data-ci="1008" data-val="{ choosecityid:1008 }" data-act="cityChange-click">安化</a>
                  <a class="js-city-name" data-ci="1126" data-val="{ choosecityid:1126 }" data-act="cityChange-click">阿勒泰市</a>
                  <a class="js-city-name" data-ci="1068" data-val="{ choosecityid:1068 }" data-act="cityChange-click">安福</a>
                </div>
              </li>"""
xpath_parser = etree.HTML(html)
AnShan = xpath_parser.xpath('//a[@class="js-city-name"][2]')[0]
chara = AnShan.xpath('./parent::div/parent::li/span/text()')
print(chara)