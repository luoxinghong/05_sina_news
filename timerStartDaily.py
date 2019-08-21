#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: 罗兴红
@contact: EX-LUOXINGHONG001@pingan.com.cn
@file: timerStartDaily.py
@time: 2018/12/17 14:03
@desc:
'''
# 文件timerStartDaily.py
from scrapy import cmdline
import datetime
import time
import shutil
import os

recoderDir = r"jobdir"   # 这是为了爬虫能够续爬而创建的目录，存储续爬需要的数据
checkFile = "isRunning.txt"  # 爬虫是否在运行的标志

startTime = datetime.datetime.now()
print(f"！！！startTime = {startTime}")

miniter = 0
while True:
    isRunning = os.path.isfile(checkFile)
    # 爬虫不在执行，开始启动爬虫
    if not isRunning:
        # 在爬虫启动之前处理一些事情，清掉JOBDIR = crawls
        # 检查JOBDIR目录crawls是否存在
        isExsit = os.path.isdir(recoderDir)
        if isExsit:
            # 删除续爬目录jobdir及目录下所有文件
            removeRes = shutil.rmtree(recoderDir)
            print(f"！！！At time:{datetime.datetime.now()}, delete res:{removeRes}")
        else:
            print(f"！！！At time:{datetime.datetime.now()}, Dir:{recoderDir} is not exsit.")
        time.sleep(5)
        clawerTime = datetime.datetime.now()
        waitTime = clawerTime - startTime
        print(f"！！！At time:{clawerTime}, start clawer: news !!!, waitTime:{waitTime}")
        cmdline.execute('scrapy crawl news -s JOBDIR=./jobdir'.split())

        break  #爬虫结束之后，退出脚本
    else:
        print(f"！！！At time:{datetime.datetime.now()}, news is running, sleep to wait.")

    time.sleep(60)        # 每1分钟检查一次
    miniter += 1
    if miniter >= 5:    # 等待满24小时，自动退出监控脚本
        break