# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from Sina_News.items import SinaNewsItem
import re
from scrapy_splash import SplashRequest
import datetime
import copy
import requests
import os
from urllib.parse import quote, unquote
from lxml import etree
import logging

logger = logging.getLogger(__name__)

emoji_pattern = re.compile(
    u"(\ud83d[\ude00-\ude4f])|"  # emoticons
    u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
    u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
    u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
    u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
    "+", flags=re.UNICODE)


class NewsSpider(scrapy.Spider):
    name = 'news'
    allowed_domains = ['sina.com.cn']
    start_urls = ['http://sina.com.cn/']
    total = 0
    urls = ["https://news.sina.com.cn/roll/#pageid=153&lid=2509&k=&num=50&page=1",
            "https://news.sina.com.cn/roll/#pageid=153&lid=2510&k=&num=50&page=1",
            "https://news.sina.com.cn/roll/#pageid=153&lid=2511&k=&num=50&page=1",
            "https://news.sina.com.cn/roll/#pageid=153&lid=2669&k=&num=50&page=1",
            "https://news.sina.com.cn/roll/#pageid=153&lid=2512&k=&num=50&page=1",
            "https://news.sina.com.cn/roll/#pageid=153&lid=2513&k=&num=50&page=1",
            "https://news.sina.com.cn/roll/#pageid=153&lid=2514&k=&num=50&page=1",
            "https://news.sina.com.cn/roll/#pageid=153&lid=2515&k=&num=50&page=1",
            "https://news.sina.com.cn/roll/#pageid=153&lid=2516&k=&num=50&page=1",
            "https://news.sina.com.cn/roll/#pageid=153&lid=2517&k=&num=50&page=1",
            "https://news.sina.com.cn/roll/#pageid=153&lid=2518&k=&num=50&page=1"]

    def start_requests(self):
        for i in self.urls:
            yield SplashRequest(url=i, callback=self.get_page_num, method='GET',
                                args={'wait': 10}, endpoint='render.html', dont_filter=True)

    def get_page_num(self, response):
        num = re.findall(r"newsList.page.goTo[(](.*?)[)];return false;", response.body.decode())[-1]
        for i in range(1, int(num)):
            page_url = response.url.replace("page=1", "page=" + str(i))
            yield SplashRequest(url=page_url, callback=self.url_in_page,
                                args={'wait': 5}, endpoint='render.html', dont_filter=True)

    def url_in_page(self, response):
        xpaths = response.xpath("//div[@id='d_list']/ul/li")
        for i in xpaths:
            url = i.xpath("./span[2]/a/@href").extract_first()
            title_temp = i.xpath("./span[2]/a/text()").extract()
            title = "".join([i.strip() for i in title_temp])
            date = i.xpath(".//span[@class='c_time']/text()").extract_first().strip()
            meta = {"url": url, "title": title, "date": date}
            if "video" not in url:
                yield Request(url, callback=self.parse, meta=meta)

    def parse(self, response):
        meta = copy.copy(response.meta)
        source = response.xpath(
            "//span[@class='source']/text()|//a[@class='source ent-source']/text()|//span[@class='source ent-source']/text()|//a[@class='source']/text()|//span[@data-sudaclick='media_name']/a/text()|//span[@id='media_name']//text()|//span[@data-sudaclick='content_media_p']/a/text()|//meta[@name='mediaid']/@content").extract_first()

        year_str = response.xpath(
            "//div/span[@class='date']/text()|//time[@class='art_time']/text()|//meta[@property='article:published_time']/@content|//span[@id='pub_date']/text()|//span[@class='time-source']/text()").extract_first().strip().replace(
            "\n", "").replace("\r", "")[0:4]
        if meta["date"].startswith("20"):
            date_time = datetime.datetime.strptime(meta["date"] + ":00", '%Y-%m-%d %H:%M:%S')
        else:
            date_time = datetime.datetime.strptime(year_str + "-" + meta["date"] + ":00", '%Y-%m-%d %H:%M:%S')
        author = response.xpath(
            "//p[@class='article-editor']/text()|//p[@class='show_author']/text()|//h2[@class='weibo_user']/text()|//span[@id='author_ename']/a/text()|//div[@class='show_author']/text()|//div[@style='float:right;']/text()").extract_first()
        author = author.split("：")[-1].replace("）", "").replace(")", "") if author else ""

        content = response.xpath(
            "//div[@id='artibody']/p[not(@class='article-editor')]//text()|//div[@id='article']/p[not(@class='article-editor')]//text()|div[@id='artibody']//text()|div[@id='articleContent']//text()|//section[@class='art_pic_card art_content']//text()").extract()
        content = [i for i in content if not re.match("\s*?责任编辑：|\s*?来源：|\s*?原标题", i)]
        content = "".join([i for i in content]).strip().replace("\n", "").replace("\r", "").replace("\t", "")

        # try:
        #     self.total += 1
        #     print("total", self.total)
        #     print("111urlurl", meta["url"])
        #     print("222titletitle", meta["title"])
        #     print("333date_time", date_time)
        #     print("444source", source)
        #     print("555author", author)
        #     print("*" * 100)
        # except Exception as e:
        #     logger(e)
        if date_time and source and len(content) > 10:
            self.total += 1
            print("total", self.total)
            print("111url", meta["url"])
            print("222title", meta["title"])
            print("333date_time", date_time)
            print("444source", source)
            print("555author", author)
            print("*" * 100)

            item = SinaNewsItem()
            item["title"] = meta["title"]
            item["date_time"] = date_time
            item["content"] = emoji_pattern.sub(r"", content)
            item["url"] = meta["url"]
            item["author"] = author
            item["source"] = source.strip()
            yield item
