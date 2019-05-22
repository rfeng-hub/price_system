# from database.cinema import mongo as shi_cinema
# from setting import CINEMA_SHI_COLLECTION
# import re
#
# cinema = shi_cinema(CINEMA_SHI_COLLECTION)
# with open('cinema_shiguang.txt','a',encoding='utf-8') as f:
#     for item in cinema.findAll():
#         cinema = re.sub(r"'_id': ObjectId\('\w+'\), ", "", str(item))
#         f.write(cinema + '\n')
#
# from database.cinema import mongo as mao_cinema
# from setting import CINEMA_SHI_COLLECTION
# import re
#
# cinema = mao_cinema(CINEMA_SHI_COLLECTION)
# with open('cinema_maoyan.txt','a',encoding='utf-8') as f:
#     for item in cinema.findAll():
#         cinema = re.sub(r"'_id': ObjectId\('\w+'\), ", "", str(item))
#         f.write(cinema + '\n')

# from database.movie import mongo
# from setting import MOVIE_COLLECTION
# import re
#
# movie = mongo(MOVIE_COLLECTION)
# with open('movies.txt','a',encoding='utf-8') as f:
#     for item in movie.findAll():
#         item = re.sub(r"'_id': ObjectId\('\w+'\), ", "", str(item))
#         f.write(item + '\n')

"""导出/导入猫眼电影票"""
# from database.ticket import mongo
# from setting import TICKET_MAO_COLLECTION
# import re
# ticket = mongo(TICKET_MAO_COLLECTION)
#
# # with open('ticket_mao.txt','a',encoding='utf-8') as f:
# #     for item in ticket.findAll():
# #         cinema = re.sub(r"'_id': ObjectId\('\w+'\), ", "", str(item))
# #         f.write(cinema + '\n')
#
# with open('ticket_mao.txt', 'r', encoding='utf-8') as f:
#     for line in f.readlines():
#         cinema = eval(line)
#         ticket.insert(cinema)

"""导出/导入糯米电影票"""
# from database.ticket import mongo
# from setting import TICKET_NUO_COLLECTION
# import re
# ticket = mongo(TICKET_NUO_COLLECTION)
#
# # with open('ticket_nuo.txt','a',encoding='utf-8') as f:
# #     for item in ticket.findAll():
# #         cinema = re.sub(r"'_id': ObjectId\('\w+'\), ", "", str(item))
# #         f.write(cinema + '\n')
#
# with open('ticket_nuo.txt', 'r', encoding='utf-8') as f:
#     for line in f.readlines():
#         cinema = eval(line)
#         ticket.insert(cinema)


"""导出/导入时光电影票"""
# from database.ticket import mongo
# from setting import TICKET_SHI_COLLECTION
# import re
# ticket = mongo(TICKET_SHI_COLLECTION)
#
# # with open('ticket_shi.txt','a',encoding='utf-8') as f:
# #     for item in ticket.findAll():
# #         cinema = re.sub(r"'_id': ObjectId\('\w+'\), ", "", str(item))
# #         f.write(cinema + '\n')
#
# with open('ticket_shi.txt', 'r', encoding='utf-8') as f:
#     for line in f.readlines():
#         cinema = eval(line)
#         ticket.insert(cinema)

"""导出/导入整合后的电影票"""
from database.ticket import mongo
from setting import TICKET_COLLECTION
import re
ticket = mongo(TICKET_COLLECTION)

# with open('tickets.txt','a',encoding='utf-8') as f:
#     for item in ticket.findAll():
#         cinema = re.sub(r"'_id': ObjectId\('\w+'\), ", "", str(item))
#         f.write(cinema + '\n')

with open('tickets.txt', 'r', encoding='utf-8') as f:
    for line in f.readlines():
        cinema = eval(line)
        ticket.insert(cinema)


# from database.ticket import mongo
# from setting import TICKET_MAO_COLLECTION
# import re
# ticket = mongo(TICKET_MAO_COLLECTION)
#
# with open('ticket_mao.txt','a',encoding='utf-8') as f:
#     for item in ticket.findAll():
#         movie = {}
#         movie['city'], movie['url'], movie['cinema_name'], movie['adress'], movie['phone'], movie['name'] =\
#             item['city'], item['url'], item['cinema_name'], re.sub(r"地址：", "", item['adress']), item['phone'], item['name']
#         movie['date'] = item['date']
#         movie['plist'] = item['plist']
#         # for date in item['date']:
#         #     movie['date'].append(date.replace(" ","") + "日")
#         #
#         # for key,value in item['plist'].items():
#         #     key = key.replace(" ","") + "日"
#         #     movie['plist'][key] = value
#         # print(movie)
#         # cinema = re.sub(r"'_id': ObjectId\('\w+'\), ", "", str(item))
#         f.write(str(movie) + '\n')

# from database.ticket import mongo
# from setting import TICKET_MAO_COLLECTION
# ticket = mongo(TICKET_MAO_COLLECTION)
# for item in ticket.findAll():
#     print(item['phone'])
