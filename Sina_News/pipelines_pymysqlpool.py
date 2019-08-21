# -*- coding: utf-8 -*-
import pymysql
from .items import SinaNewsItem
import traceback
import logging
from Sina_News.middlewares import UrlFilterAndAdd, URLRedisFilter
import os
from twisted.enterprise import adbapi

logger = logging.getLogger(__name__)
checkFile = "isRunning.txt"


class SinaNewsPipeline(object):
    commit_sql_str = '''insert into news1(title,date_time,content,url,author,source) values ("{title}","{date_time}","{content}","{url}","{author}","{source}");'''

    # insert_url_sql = '''insert into total_url(url) values ("{url}");'''
    # query_url_str = '''select * from total_url where url="{url}";'''

    def __init__(self, pool):
        self.dupefilter = UrlFilterAndAdd()
        self.dbpool = pool

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings.get("MYSQL_HOST"),
            port=settings.get("MYSQL_PORT"),
            db=settings.get("MYSQL_DBNAME"),
            user=settings.get("MYSQL_USER"),
            passwd=settings.get("MYSQL_PASSWD"),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool("pymysql", **dbparms)
        return cls(dbpool)


    def process_item(self, item, spider):
        self.dupefilter.add_url(item['url'])

        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        # 根据不同的item 构建不同的sql语句并插入到mysql中
        sqltext = self.commit_sql_str.format(
            title=pymysql.escape_string(item["title"]),
            date_time=item["date_time"],
            content=pymysql.escape_string(item["content"]),
            url=item["url"],
            author=item["author"],
            source=item["source"]
        )
        cursor.execute(sqltext)

    def open_spider(self, spider):
        f = open(checkFile, "w")
        f.close()

    def close_spider(self, spider):
        isFileExsit = os.path.isfile(checkFile)
        if isFileExsit:
            os.remove(checkFile)
