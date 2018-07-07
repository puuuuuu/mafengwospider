# coding=utf-8

import json
import re

from bs4 import BeautifulSoup
from scrapy import Request, Selector
from scrapy.spiders import Spider
import lxml

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
        soup = BeautifulSoup(response.text, 'lxml')
        html = str(soup)  # 获取整个网页源码
        header_html = str(soup.find('div', attrs={'id': 'header'}))
        new_html = html.replace(header_html, '')  # 去掉页面导航头
        crumb_html = str(soup.find('div', attrs={'class': 'crumb'}))
        new_html = new_html.replace(crumb_html, '')  # 去掉页面层级关系导航
        user_list_html = str(soup.find('div', attrs={'class': 'user_list'}))
        new_html = new_html.replace(user_list_html, '')  # 去掉作者信息
        section_from_s_html = str(soup.find('div', attrs={'class': 'section_from_s'}))
        new_html = new_html.replace(section_from_s_html, '')  # 去掉开头出处信息
        reader_num_html = str(soup.select('.sub-tit > span')[0])
        new_html = new_html.replace(reader_num_html, '')  # 去掉阅读数信息
        bar_sar_html = str(soup.find('div', attrs={'class': 'bar-sar'}))
        new_html = new_html.replace(bar_sar_html, '')  # 去掉点赞信息
        section_from_e_html = str(soup.find('div', attrs={'class': 'section_from_e'}))
        new_html = new_html.replace(section_from_e_html, '')  # 去掉文末出处信息
        m_t_20_html = str(soup.find('div', attrs={'class': 'm_t_20'}))
        new_html = new_html.replace(m_t_20_html, '')  # 去掉文末版权信息
        l_comment_html = str(soup.find('div', attrs={'class': 'l-comment'}))
        new_html = new_html.replace(l_comment_html, '')  # 去掉评论系统
        ft_content_html = str(soup.find('div', attrs={'class': 'ft-content'}))
        new_html = new_html.replace(ft_content_html, '')  # 去掉页脚信息
        new_html = new_html.replace('\n', ' ')

        item['article_html'] = new_html
        yield item
