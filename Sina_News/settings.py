# -*- coding: utf-8 -*-
BOT_NAME = 'Sina_News'
SPIDER_MODULES = ['Sina_News.spiders']
NEWSPIDER_MODULE = 'Sina_News.spiders'


import datetime
to_day = datetime.datetime.now()
log_file_path = "./logs/{}_{}_{}.log".format(to_day.year, to_day.month, to_day.day)
LOG_LEVEL = "INFO"
LOG_FILE = log_file_path
ROBOTSTXT_OBEY = False

# 渲染服务的url
SPLASH_URL = 'http://192.168.99.100:8050'
# 使用Splash的Http缓存
# HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

DOWNLOADER_MIDDLEWARES = {
    'Sina_News.middlewares.SinaNewsSpiderMiddleware': 543,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    'Sina_News.middlewares.RandomUserAgentMiddleware': 1,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,  # 这里要设置原来的scrapy的useragent为None，否者会被覆盖掉
}

# 增加爬虫速度及防ban配置
DOWNLOAD_DELAY = 0
DOWNLOAD_FAIL_ON_DATALOSS = False
CONCURRENT_REQUESTS = 10
CONCURRENT_REQUESTS_PER_DOMAIN = 10
CONCURRENT_REQUESTS_PER_IP = 10
COOKIES_ENABLED = False
DOWNLOAD_TIMEOUT = 60

# 配置自己重写的RFPDupeFilter
DUPEFILTER_CLASS = 'Sina_News.middlewares.URLRedisFilter'

# 开启item_pipelines，入库
ITEM_PIPELINES = {
    'Sina_News.pipelines.SinaNewsPipeline': 300,
}

# msyql数据库配置
MYSQL_HOST = "localhost"
MYSQL_DBNAME = "sina_news"
MYSQL_USER = "root"
MYSQL_PASSWD = "lxh123"
MYSQL_PORT = 3306

# redis数据库配置
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PASSWD = "lxh123"
REDIS_DBNAME = 30

# 配置user_agent的随机类型
RANDOM_UA_TYPE = 'random'


# 23小时候关闭爬虫
# CLOSESPIDER_TIMEOUT = 82800
