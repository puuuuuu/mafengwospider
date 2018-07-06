# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy.conf import settings


class MafengwospiderPipeline(object):
    def process_item(self, item, spider):
        return item


class SaveData(object):

    def __init__(self):
        conn = pymongo.MongoClient(host=settings['MONGODB_HOST'], port=settings['MONGODB_PORT'])
        db = conn[settings['MONGODB_DB']]
        self.collections = db[settings['MONGODB_COLLECTION']]

    def process_item(self, item, spider):

        self.collections.update({'title': item['title']}, {'$set': item}, True)

        return item
