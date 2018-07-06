
import scrapy
from scrapy import Request, Selector
from scrapy.spiders import Spider


class TravelStrategy(Spider):

    name = 'mafengwo'
    mdd_url = 'http://www.mafengwo.cn/mdd/'

    def start_requests(self):
        yield Request(self.mdd_url)

    def parse(self, response):
        res = Selector(response)
        area_list = res.xpath('/html/body/div[2]/div[6]/div/div/div/dl/dt[@class="sub-title"]/text()')
        for area in area_list:
            area_name = area.extract()
            area.x
            print(area_name)