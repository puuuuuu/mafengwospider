# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MafengwospiderItem(scrapy.Item):

    country_name = scrapy.Field()  # 城市名称
    country_id = scrapy.Field()  # 城市id
    area_name = scrapy.Field()  # 大洲名称
    title = scrapy.Field()  # 攻略标题
    public_time = scrapy.Field()  # 发表时间
    article_html = scrapy.Field()  # 文章文档页面

