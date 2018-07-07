# coding=utf-8

import json
import re

from scrapy import Request, Selector
from scrapy.spiders import Spider

from mafengwospider.items import MafengwospiderItem


class TravelStrategy(Spider):
    name = 'mafengwo'
    mdd_url = 'http://www.mafengwo.cn/mdd/'

    def start_requests(self):
        yield Request(self.mdd_url)

    def parse(self, response):
        res = Selector(response)
        area_name_list = res.xpath('/html/body/div[2]/div[6]/div/div/div/dl/dt[@class="sub-title"]/text()').extract()
        i = 1
        for area_name in area_name_list:
            country_list_xpath_str = '/html/body/div[2]/div[6]/div/div/div/dl[' + str(i) + ']/dd/ul/li/a/text()'
            country_url_list_xpath_str = '/html/body/div[2]/div[6]/div/div/div/dl[' + str(i) + ']/dd/ul/li/a/@href'
            country_list = res.xpath(country_list_xpath_str).extract()
            country_id_list = [url.split('/')[-1].split('.')[0] for url
                               in res.xpath(country_url_list_xpath_str).extract()]
            country_info = dict(zip(country_list, country_id_list))

            for country in country_info.items():
                yield Request('http://www.mafengwo.cn/gonglve/ziyouxing/list/list_page?mddid=' + country[1] + '&page=1',
                              callback=self.parse_free_play,
                              meta={'country_name': country[0], 'country_id': country[1], 'area_name': area_name})

    def parse_free_play(self, response):
        html = json.loads(response.text).get('html')
        try:
            total_pages = int(re.findall('共(\w+)页', html)[0])
            for i in range(1, total_pages + 1):
                detail_urls = [('http://www.mafengwo.cn' + i) for i in re.findall('.*?<a.*?href="(.*?.html)"', html)]
                for detail_url in detail_urls:
                    yield Request(detail_url, callback=self.parse_details,
                                  meta={'country_name': response.meta.get('country_name'),
                                        'country_id': response.meta.get('country_id'),
                                        'area_name': response.meta.get('area_name')})
        except:
            pass

    def parse_details(self, response):
        item = MafengwospiderItem()
        res = Selector(response)
        item['country_name'] = response.meta.get('country_name')
        item['country_id'] = response.meta.get('country_id')
        item['area_name'] = response.meta.get('area_name')
        item['title'] = res.xpath('//div[@class="l-topic"]/h1/text()').extract()[0]
        item['public_time'] = res.xpath('//div[@class="l-topic"]/div[1]/span[2]/em/text()').extract()[0]
        topic = res.xpath('//div[@class="l-topic"]').extract()[0]
        user_info = res.xpath('//div[@class="user_list"]').extract()[0]
        topic_new = topic.replace(user_info, '')
        content = res.xpath('//div[@class="_j_content"]').extract()[0]
        new_html = topic_new + content
        item['article_html'] = new_html
        yield item
