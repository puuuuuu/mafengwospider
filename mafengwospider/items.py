# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MafengwospiderItem(scrapy.Item):

    country_name = scrapy.Field()
    country_id = scrapy.Field()
    area_name = scrapy.Field()
    title = scrapy.Field()
    public_time = scrapy.Field()
    article_html = scrapy.Field()

