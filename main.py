# -*- coding: utf-8 -*-
from scrapy import cmdline


# cmdline.execute("scrapy crawl news -s JOBDIR=./jobdir".split())
cmdline.execute("scrapy crawl news".split())