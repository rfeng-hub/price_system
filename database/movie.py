import pymongo
from setting import MONGO_URI

class mongo():
    mongo_db = 'Price_System'

    def __init__(self, collection):
        self.mongo_uri = MONGO_URI
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = collection

    def disconnect(self):  # 断开数据库连接
        self.client.close()

    def insert(self, item):  # 插入（更新）一条数据
        self.db[self.collection].update({'key': item['key']}, dict(item), True)

    def findOne(self):  # 获取第一条数据
        return self.db[self.collection].find_one()

    def findAll(self):  # 获取集合中所有数据
        return self.db[self.collection].find()

    def count(self):  # 集合中所有数据数目
        return self.db[self.collection].find().count()

    def update(self, url, url_value, name, value):  # 更新一条数据
        return self.db[self.collection].update({url: url_value}, {"$set": {name: value}})

    def delete(self):  # 删除集合
        self.db[self.collection].drop()