# mafengwospider
爬取马蜂窝网站旅游攻略

## 1.配置虚拟环境

### 1.1 该项目相关包列表

    Twisted(手动安装)
    scrapy
    pywin32

### 1.2 安装相关包需要注意的项

    1. 在安装scrapy框架前我们需要先安装Twisted,直接pip安装时会报错,我们先去https://www.lfd.uci.edu/~gohlke/pythonlibs/该地址下载
    与你所使用的环境相匹配的.whl文件然后使用pip install安装该文件
    2. 此时我们再pip install scrapy就可以成功安装了

## 2.项目

### 2.1 创建项目

	scrapy startproject mafengwospider

### 2.2 settings.py

配置中间件及mongodb常量

	DOWNLOADER_MIDDLEWARES = {
	    'mafengwospider.middlewares.MafengwospiderDownloaderMiddleware': 543,
	    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 543,
	    'mafengwospider.middlewares.MafengwospiderSpiderMiddleware': 125
	}

	ITEM_PIPELINES = {
	    'mafengwospider.pipelines.MafengwospiderPipeline': 300,
	    'mafengwospider.pipelines.SaveData': 301
	}

	MONGODB_HOST = '127.0.0.1'
	MONGODB_PORT = 27017
	MONGODB_DB = 'mafengwo'
	MONGODB_COLLECTION = 'free_play'
	
	IPPOOL = set_ip_pool()

### 2.3 travel_strategy.py

爬虫文件

	# coding=utf-8

	import json
	import re
	
	from bs4 import BeautifulSoup
	from scrapy import Request, Selector
	from scrapy.spiders import Spider
	import lxml
	
	from mafengwospider.items import MafengwospiderItem
	
	
	class TravelStrategy(Spider):

	    def __init__(self):
	        self.headers = {
	            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	            'Accept-Encoding': 'gzip, deflate',
	            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
	                          '(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
	        }
	
	    name = 'mafengwo'
	
	    # 马蜂窝目的地页面地址
	    mdd_url = 'http://www.mafengwo.cn/mdd/'
	
	    def start_requests(self):
	        yield Request(self.mdd_url)
	
	    def parse(self, response):
	        res = Selector(response)
	        # 爬取大洲区域信息
	        area_name_list = res.xpath('/html/body/div[2]/div[6]/div/div/div/dl/dt[@class="sub-title"]/text()').extract()
	        i = 1
	        for area_name in area_name_list:
	            # 定义获取每个国家名字的xpath_str
	            country_list_xpath_str = '/html/body/div[2]/div[6]/div/div/div/dl[' + str(i) + ']/dd/ul/li/a/text()'
	            # 定义获取每个国家链接的xpath_str
	            country_url_list_xpath_str = '/html/body/div[2]/div[6]/div/div/div/dl[' + str(i) + ']/dd/ul/li/a/@href'
	            country_list = res.xpath(country_list_xpath_str).extract()
	            # 获取国家id的列表
	            country_id_list = [url.split('/')[-1].split('.')[0] for url
	                               in res.xpath(country_url_list_xpath_str).extract()]
	            # 国家名字及对应的id信息
	            country_info = dict(zip(country_list, country_id_list))
	            # 生成各个国家自由行攻略的页面的请求
	            for country in country_info.items():
	                yield Request('http://www.mafengwo.cn/gonglve/ziyouxing/list/list_page?mddid=' + country[1] + '&page=1',
	                              callback=self.parse_free_play,
	                              meta={'country_name': country[0], 'country_id': country[1], 'area_name': area_name})
	
	    def parse_free_play(self, response):
	
	        html = json.loads(response.text).get('html')
	        # 捕获没有攻略信息时抛出的异常并不做处理
	        try:
	            # 正则匹配出攻略的总页数
	            total_pages = int(re.findall('共(\w+)页', html)[0])
	            # 循环解析每一页
	            for i in range(1, total_pages + 1):
	                # 正则匹配出每条攻略的url地址
	                detail_urls = [('http://www.mafengwo.cn' + i) for i in re.findall('.*?<a.*?href="(.*?.html)"', html)]
	                for detail_url in detail_urls:
	                    yield Request(detail_url, callback=self.parse_details,
	                                  meta={'country_name': response.meta.get('country_name'),
	                                        'country_id': response.meta.get('country_id'),
	                                        'area_name': response.meta.get('area_name')})
	        except:
	            pass
	
	    def parse_details(self, response):
	        """
	        解析详情页面的信息并做处理
	        :param response:
	        :return:
	        """
	        item = MafengwospiderItem()
	        res = Selector(response)
	        # 国家名
	        item['country_name'] = response.meta.get('country_name')
	        # 国家id
	        item['country_id'] = response.meta.get('country_id')
	        # 所属大洲名字
	        item['area_name'] = response.meta.get('area_name')
	        # 标题
	        item['title'] = res.xpath('//div[@class="l-topic"]/h1/text()').extract()[0]
	        # 发表时间
	        item['public_time'] = res.xpath('//div[@class="l-topic"]/div[1]/span[2]/em/text()').extract()[0]
	        # bs4对整个页面进行处理并生成新页面
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

### 2.4 items.py

定义模型字段

	import scrapy
	
	
	class MafengwospiderItem(scrapy.Item):
	
	    country_name = scrapy.Field()  # 城市名称
	    country_id = scrapy.Field()  # 城市id
	    area_name = scrapy.Field()  # 大洲名称
	    title = scrapy.Field()  # 攻略标题
	    public_time = scrapy.Field()  # 发表时间
	    article_html = scrapy.Field()  # 文章文档页面

### 2.5 pipelines.py

初始化连接mongodb数据库并将爬取到的数据持久化(update)

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

### 2.6 middlewares.py

重写process_request方法，向request中加入代理ip
	
	class MafengwospiderSpiderMiddleware(object):
	    # Not all methods need to be defined. If a method is not defined,
	    # scrapy acts as if the spider middleware does not modify the
	    # passed objects.
	
	    def __init__(self, ip=''):
	        self.ip = ip
	
	    def process_request(self, request, spider):
	        thisip = random.choice(IPPOOL)
	        print('this is ip:' + thisip['ipaddr'])
	        request.meta['proxy'] = 'http://' + thisip['ipaddr']

### 2.7 proxies.py

定义类从ip代理网站爬取代理ip、校验ip的可用性并返回

	# *-* coding:utf-8 *-*
	
	from bs4 import BeautifulSoup
	import lxml
	from multiprocessing import Process, Queue
	import random
	import requests
	
	
	class Proxies(object):
	    """docstring for Proxies"""
	    def __init__(self, page=3):
	        self.proxies = []
	        self.verify_pro = []
	        self.page = page
	        self.headers = {
	            'Accept': '*/*',
	            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
	                          '(KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
	            'Accept-Encoding': 'gzip, deflate, sdch',
	            'Accept-Language': 'zh-CN,zh;q=0.8'
	        }
	        self.get_proxies()
	        self.get_proxies_nn()
	
	    def get_proxies(self):
	        page = random.randint(1, 10)
	        page_stop = page + self.page
	        while page < page_stop:
	            url = 'http://www.xicidaili.com/nt/%d' % page
	            html = requests.get(url, headers=self.headers).content
	            soup = BeautifulSoup(html, 'lxml')
	            ip_list = soup.find(id='ip_list')
	            for odd in ip_list.find_all(class_='odd'):
	                protocol = odd.find_all('td')[5].get_text().lower() + '://'
	                self.proxies.append(protocol + ':'.join([x.get_text() for x in odd.find_all('td')[1:3]]))
	            page += 1
	
	    def get_proxies_nn(self):
	        page = random.randint(1, 10)
	        page_stop = page + self.page
	        while page < page_stop:
	            url = 'http://www.xicidaili.com/nn/%d' % page
	            html = requests.get(url, headers=self.headers).content
	            soup = BeautifulSoup(html, 'lxml')
	            ip_list = soup.find(id='ip_list')
	            for odd in ip_list.find_all(class_='odd'):
	                protocol = odd.find_all('td')[5].get_text().lower() + '://'
	                self.proxies.append(protocol + ':'.join([x.get_text() for x in odd.find_all('td')[1:3]]))
	            page += 1
	
	    def verify_proxies(self):
	
	        # 没验证的代理
	        old_queue = Queue()
	        # 验证后的代理
	        new_queue = Queue()
	        print('verify proxy........')
	        works = []
	        for _ in range(30):
	            works.append(Process(target=self.verify_one_proxy, args=(old_queue, new_queue)))
	        for work in works:
	            work.start()
	        for proxy in self.proxies:
	            old_queue.put(proxy)
	        for work in works:
	            old_queue.put(0)
	        for work in works:
	            work.join()
	        self.proxies = []
	        while 1:
	            try:
	                self.proxies.append(new_queue.get(timeout=1))
	            except:
	                break
	        print('verify_proxies done!')
	
	    def verify_one_proxy(self, old_queue, new_queue):
	        while 1:
	            proxy = old_queue.get()
	            if proxy == 0:
	                break
	            protocol = 'https' if 'https' in proxy else 'http'
	            proxies = {protocol: proxy}
	            try:
	                if requests.get('http://www.baidu.com', proxies=proxies, timeout=2).status_code == 200:
	                    print('success %s' % proxy)
	                    new_queue.put(proxy)
	            except:
	                print('fail %s' % proxy)

### 2.8 set_IPPOOL.py

设置ip代理地址池

	from mafengwospider.proxies import Proxies
	
	
	def set_ip_pool():
	    a = Proxies()
	    a.verify_proxies()
	    print(a.proxies)
	    proxie = a.proxies
	    ip_pool = []
	    for proxy in proxie:
	        proxy_new = proxy.split('//')[-1]
	        ip = {'ipaddr': proxy_new}
	        ip_pool.append(ip)
	    return ip_pool



