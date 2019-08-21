# -*- coding: utf-8 -*-
import pymysql
from .items import SinaNewsItem
import traceback
import logging
from Sina_News.middlewares import UrlFilterAndAdd, URLRedisFilter
import os
from twisted.enterprise import adbapi

logger = logging.getLogger(__name__)


# checkFile = "isRunning.txt"


class SinaNewsPipeline(object):
    commit_sql_str = '''insert into news(title,date_time,content,url,author,source) values ("{title}","{date_time}","{content}","{url}","{author}","{source}");'''

    total = 0

    def __init__(self, settings):
        self.settings = settings
        self.dupefilter = UrlFilterAndAdd()

    def process_item(self, item, spider):
        # print("add>>url:", item['url'])
        self.dupefilter.add_url(item['url'])
        try:
            sqltext = self.commit_sql_str.format(
                title=pymysql.escape_string(item["title"]),
                date_time=item["date_time"],
                content=pymysql.escape_string(item["content"]),
                url=item["url"],
                author=item["author"],
                source=item["source"]
            )

            self.cursor.execute(sqltext)
        except Exception as e:
            logger.warning(e)

        print("url：", item["url"])
        self.total += 1
        print("total", self.total)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def open_spider(self, spider):
        self.connect = pymysql.connect(
            host=self.settings.get("MYSQL_HOST"),
            port=self.settings.get("MYSQL_PORT"),
            db=self.settings.get("MYSQL_DBNAME"),
            user=self.settings.get("MYSQL_USER"),
            passwd=self.settings.get("MYSQL_PASSWD"),
            charset='utf8mb4',
            use_unicode=True
        )

        self.cursor = self.connect.cursor()
        self.connect.autocommit(True)

    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()
