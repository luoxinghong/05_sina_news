# -*- coding: utf-8 -*-
import scrapy
from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
import random
from scrapy.dupefilters import RFPDupeFilter
import hashlib
import redis
import os
import json
import logging
from scrapy.utils.url import canonicalize_url
from Sina_News import settings
from fake_useragent import UserAgent


class SinaNewsSpiderMiddleware(object):
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    def process_start_requests(self, start_requests, spider):
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SinaNewsDownloaderMiddleware(object):
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


# 自己定义一个user_agent的类，继承了userAgentMiddleware
class RandomUserAgentMiddleware(object):
    def __init__(self, crawler):
        super(RandomUserAgentMiddleware, self).__init__()
        self.ua = UserAgent()
        # 从setting文件中读取RANDOM_UA_TYPE值
        self.ua_type = crawler.settings.get('RANDOM_UA_TYPE', 'random')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        def get_ua():
            '''Gets random UA based on the type setting (random, firefox…)'''
            return getattr(self.ua, self.ua_type)

        user_agent_random = get_ua()
        request.headers.setdefault('User-Agent', user_agent_random)  # 这样就是实现了User-Agent的随即变换


class URLRedisFilter(RFPDupeFilter):
    """ 只根据url去重"""

    def __init__(self, path=None, debug=False):
        RFPDupeFilter.__init__(self, path)
        self.dupefilter = UrlFilterAndAdd()

    def request_seen(self, request):
        # 校验，新增2行代码
        if self.dupefilter.check_url(request.url):
            return True

        # 保留中间页面的去重规则不变，不然爬虫在运行过程中容易出现死循环
        fp = self.request_fingerprint(request)
        if fp in self.fingerprints:
            return True
        self.fingerprints.add(fp)
        if self.file:
            self.file.write(fp + os.linesep)


class UrlFilterAndAdd(object):
    def __init__(self):
        redis_config = {
            "host": settings.REDIS_HOST,  # redis ip
            "port": settings.REDIS_PORT,
            "password": settings.REDIS_PASSWD,
            "db": settings.REDIS_DBNAME,
        }

        pool = redis.ConnectionPool(**redis_config)
        self.pool = pool
        self.redis = redis.StrictRedis(connection_pool=pool)
        self.key = "sian_news_key"

    def url_sha1(self, url):
        fp = hashlib.sha1()
        # 对url中的构成数据进行了重新排列，例如有些url中请求参数一样，但是顺序不同
        fp.update(canonicalize_url(url).encode("utf-8"))
        url_sha1 = fp.hexdigest()
        return url_sha1

    # 此处只判断url是否在set中，并不添加url信息，
    # 防止将起始url 、中间url(比如列表页的url地址)写入缓存中
    def check_url(self, url):
        sha1 = self.url_sha1(url)
        isExist = self.redis.sismember(self.key, sha1)
        return isExist

    # 将经过hash的url添加到reids的集合中，key为sian_news_key，命令为SMEMBERS spider_redis_key
    def add_url(self, url):
        sha1 = self.url_sha1(url)
        added = self.redis.sadd(self.key, sha1)
        return added
