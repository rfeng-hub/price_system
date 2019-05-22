from setting import TICKET_MAO_COLLECTION,TICKET_NUO_COLLECTION,TICKET_SHI_COLLECTION,TICKET_TAO_COLLECTION
from setting import TICKET_COLLECTION
from database.ticket import mongo
import re

mao = mongo(TICKET_MAO_COLLECTION)
nuo = mongo(TICKET_NUO_COLLECTION)
shi = mongo(TICKET_SHI_COLLECTION)
tao = mongo(TICKET_TAO_COLLECTION)

nuo_tickets = []
shi_tickets = []
mao_tickets = []
tickets = []

def gather_mao():
    # 调整猫眼日期格式
    for item in mao.findAll():
        ticket = {}
        ticket["city"], ticket["url"], ticket["cinema_name"], ticket["address"], ticket["phone"], ticket["name"], ticket["score"], ticket["image"] =\
            item["city"], item["url"], item["cinema_name"], item["address"], item["phone"], item["name"], item["score"], item["image"]
        ticket['date'] = []
        ticket['plist'] = {}
        ticket['date'].append(item['date'][0])

        #修改猫眼日期格式
        if len(item['date']) >= 2:
            ticket['date'].append("明天" + item['date'][1][2:])
            if len(item['date']) >= 3:
                ticket['date'].append("后天" + item['date'][2][2:])
                for i in range(3, len(item['date'])):
                    ticket['date'].append(item['date'][i])

        #排片
        num = 0
        for day in item['plist']:
            for j in range(len(item['plist'][day])):  # 猫眼此家影院此部电影这一天的每一条排片
                item['plist'][day][j]['shi_price'] = ""
                item['plist'][day][j]['nuo_price'] = ""
            ticket['plist'][ticket['date'][num]] = item['plist'][day]
            num += 1

        mao_tickets.append(ticket)
    for item in nuo.findAll():
        nuo_tickets.append(item)
    for item in shi.findAll():
        shi_tickets.append(item)

def gather_shi():
    # 整合时光排片
    for movie1 in mao_tickets:  # 猫眼的每家影院的每一部电影的排片
        tickets.append(movie1)
        for movie2 in shi_tickets:  # 时光的每家影院的每一部电影的排片
            """判别是同一家影院"""
            if movie2['city'] == movie1['city']:  # 同一个城市
                # 方法一，影院名相同（因为涉及到分店这个概念，所以只能用相同）
                if movie2['cinema_name'] == movie1['cinema_name']:  # 同一家影院
                    if movie2['name'] == movie1['name']:  # 同一家影院同一部电影
                        # print(movie2['cinema_name'],movie2['name'])
                        for day1 in movie1['plist']:  # 猫眼此家影院此部电影每一天
                            for day2 in movie2['plist']:  # 时光此家影院此部电影每一天
                                if day1 == day2:  # 同一天
                                    for i in range(len(movie1['plist'][day1])):  # 猫眼此家影院此部电影这一天的每一条排片
                                        for play2 in movie2['plist'][day1]:  # 时光此家影院此部电影这一天的每一条排片
                                            if play2['begin-time'] == movie1['plist'][day1][i]['begin-time']:  # 同一条排片
                                                tickets[-1]['plist'][day1][i]['shi_price'] = str(
                                                    play2['price'])  # 加上时光的票价
                                                break
                                    break
                        # print(tickets)
                        break
                # 方法二，地址包含
                elif movie2['address'] in movie1['address'] or movie1['address'] in movie2['address']:
                    if movie2['name'] == movie1['name']:  # 同一家影院同一部电影
                        for day1 in movie1['plist']:  # 猫眼此家影院此部电影每一天
                            for day2 in movie2['plist']:  # 时光此家影院此部电影每一天
                                if day1 == day2:  # 同一天
                                    for i in range(len(movie1['plist'][day1])):  # 猫眼此家影院此部电影这一天的每一条排片
                                        for play2 in movie2['plist'][day1]:  # 时光此家影院此部电影这一天的每一条排片
                                            if play2['begin-time'] == movie1['plist'][day1][i]['begin-time']:  # 同一条排片
                                                tickets[-1]['plist'][day1][i]['shi_price'] = str(
                                                    play2['price'])  # 加上时光的票价
                                                break
                                    break
                        break

                # 方法三，电话号码匹配
                else:
                    phone1 = movie1['phone'].replace(",", " ")
                    phone2 = movie2['phone'].replace(",", " ")
                    phone1 = phone1.split(" ")[0]
                    phone2 = phone2.split(" ")[0]
                    phone1 = phone1.split("-")[1] if len(phone1.split("-")) != 1 else phone1.split("-")[0]
                    phone2 = phone2.split("-")[1] if len(phone2.split("-")) != 1 else phone2.split("-")[0]
                    if phone1 == phone2 and movie2['name'] == movie1['name']:  # 同一家影院同一部电影
                        for day1 in movie1['plist']:  # 猫眼此家影院此部电影每一天
                            for day2 in movie2['plist']:  # 时光此家影院此部电影每一天
                                if day1 == day2:  # 同一天
                                    for i in range(len(movie1['plist'][day1])):  # 猫眼此家影院此部电影这一天的每一条排片
                                        for play2 in movie2['plist'][day1]:  # 时光此家影院此部电影这一天的每一条排片
                                            if play2['begin-time'] == movie1['plist'][day1][i]['begin-time']:  # 同一条排片
                                                tickets[-1]['plist'][day1][i]['shi_price'] = str(
                                                    play2['price'])  # 加上时光的票价
                                                break
                                    break
                        break

    print("shi over")
    shi.disconnect()

def gather_nuo():
    # #整合糯米排片
    for num in range(len(tickets)): #已有的每家影院的每一部电影的排片
        for movie2 in nuo_tickets: #糯米的每家影院的每一部电影的排片
            # 方法一影院名相同
            if movie2['cinema_name'] == tickets[num]['cinema_name']: # 同一家影院
                if movie2['name'] == tickets[num]['name']: # 同一家影院同一部电影
                    for day1 in tickets[num]['plist']: # 已有此家影院此部电影每一天
                        for day2 in movie2['plist']: # 糯米此家影院此部电影每一天
                            if day1 == day2: # 同一天
                                for i in range(len(tickets[num]['plist'][day1])): # 已有此家影院此部电影这一天的每一条排片
                                    for play2 in movie2['plist'][day1]:  # 糯米此家影院此部电影这一天的每一条排片
                                        if play2['begin-time'] == tickets[num]['plist'][day1][i]['begin-time']: # 同一条排片
                                            tickets[num]['plist'][day1][i]['nuo_price'] = play2['price'] # 加上糯米的票价
                                            break
                                break
                    break
            # 方法二，地址包含
            elif movie2['address'] in tickets[num]['address'] or tickets[num]['address'] in movie2['address']:
                if movie2['name'] == tickets[num]['name']:  # 同一家影院同一部电影
                    for day1 in tickets[num]['plist']:  # 已有此家影院此部电影每一天
                        for day2 in movie2['plist']:  # 糯米此家影院此部电影每一天
                            if day1 == day2:  # 同一天
                                for i in range(len(tickets[num]['plist'][day1])):  # 已有此家影院此部电影这一天的每一条排片
                                    for play2 in movie2['plist'][day1]:  # 糯米此家影院此部电影这一天的每一条排片
                                        if play2['begin-time'] == tickets[num]['plist'][day1][i]['begin-time']:  # 同一条排片
                                            tickets[num]['plist'][day1][i]['nuo_price'] = play2['price']  # 加上糯米的票价
                                            break
                                break
                    break
            # 方法三，调整联系电话格式后比较是否相等
            else:
                phone1 = tickets[num]['phone'].replace(",", " ")
                phone2 = movie2['phone'].replace(",", " ")
                phone1 = phone1.split(" ")[0]
                phone2 = phone2.split(" ")[0]
                phone1 = phone1.split("-")[1] if len(phone1.split("-")) != 1 else phone1.split("-")[0]
                phone2 = phone2.split("-")[1] if len(phone2.split("-")) != 1 else phone2.split("-")[0]
                if phone1 == phone2 and movie2['name'] == tickets[num]['name']:  # 同一家影院同一部电影
                    for day1 in tickets[num]['plist']:  # 已有此家影院此部电影每一天
                        for day2 in movie2['plist']:  # 糯米此家影院此部电影每一天
                            if day1 == day2:  # 同一天
                                for i in range(len(tickets[num]['plist'][day1])):  # 已有此家影院此部电影这一天的每一条排片
                                    for play2 in movie2['plist'][day1]:  # 糯米此家影院此部电影这一天的每一条排片
                                        if play2['begin-time'] == tickets[num]['plist'][day1][i]['begin-time']:  # 同一条排片
                                            tickets[num]['plist'][day1][i]['nuo_price'] = play2['price']  # 加上糯米的票价
                                            break
                                break
                    break
    mao.disconnect()
    nuo.disconnect()
    print("ok")


def begin():
    print(">>>>>>>>>>>>>>>>开始整合数据>>>>>>>>>>>>>>>>>")
    gather_mao()
    gather_shi()
    gather_nuo()
    with open('tickets.txt','w',encoding='utf-8') as f:
        for item in tickets:
            f.write(str(item) + '\n')

    gather = mongo(TICKET_COLLECTION)
    gather.delete()
    for item in tickets:
        # print(item)
        gather.insert(item)
    print(">>>>>>>>>>>>>>>>整合完毕>>>>>>>>>>>>>>>>>")

begin()

#
# # 糯米
# 0483-3989998
# 0412--7135999
# 0851-36717036
# (0412)3385858
# 3466-4666
# 05565933888
# 87578536
#
# 01053021050
# 010-65231588
# 010-66062266
# (010)52802652
# 010-60407788-804
# 010-88268200-8021
#
# 4000806060
# 15983724586
#
# # 猫眼
# 0483-8888888
# 0851-33604199
# 028-27115333
# 010-64160922
# 010-60749993-601
# 010-62904980-8011
# 18325669188
#
# # 时光
# 0483-3989998
# 0851-33681678
# 0439-6987999-814
# 0915-8163222-3221
# 0827-5559555-5233733
# 010-51193399-0
# 010-56350596
# 010-59056168-8888
# 010-64139608-600
# 18810211987
# 4000806060


