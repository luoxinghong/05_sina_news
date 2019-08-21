①scrapy_redis url去重 ②使用fake_useragent，生了自己定义user_agent列表③使用mysql连接池保存数据 ④windows定时任务设置 ⑤scrapy_splash加载page页

新增功能：⑥使用ItemLoader(垃圾，别用)

备注：items_load.py、news_load.py为加入了ItemLoader后的版本，可忽略，仅供参考
****************************************************************************************************
1. 人生苦短，我用Python

      ①声明
      代码仅供下载个人使用，请勿转发或者用于任何商业用途！

      ②项目初衷
      应公司要求，需要爬取新浪尽可能多的新闻，用于机器学习语料。每条新闻必须包括url、标题，日期、内容、作者（不必须一定有）、来源。

      ③环境
      windows7 + docker + redis + mysql + python3.5 + scrapy_splash

      ④使用方法
      先按照项目用到的pip包（所有包均在requirements.txt文件中），命令pip install -r requirements.txt。
      mysql、redis数据库的配置在settings.py文件中，请自行修改为你的配置。
      爬取的数据保存在mysql。所以需先建表，建表语句在create_news.sql文件中。
      运行main.py文件，即可启动爬虫。
      默认项目设置的日志等级为WARNING,线程数设置的为10，可自行在settings.py文件中修改。

****************************************************************************************************
2. URL去重

    利用scrapy_redis+redis数据库实现的去重，可查看middlewares.py文件中的UrlFilterAndAdd、URLRedisFilter
    注意
    由于所有的起始url地址均是js动态加载的，所以项目采用了scrapy_splash+docker

****************************************************************************************************
3. redis命令

    cd到redis安装的目录下，执行redis-cli -a lxh123 连接reids
    select 10 # 选择10库
    keys *
    SMEMBERS sina_news_key

****************************************************************************************************
4. mysql命令

    ①#按条导出表数据，只能导出到mysql的设置的目录，可以使用show variables like '%secure%';查看 secure-file-priv 当前的值是什么

    ②select * from news limit 10 into outfile 'C://ProgramData//MySQL//MySQL Server 5.7//Uploads//1.csv' fields terminated by ',' optionally      enclosed by '"' escaped by '"' lines terminated by '\r\n';

    ③导出的csv文件使用excel打开，乱码，可以先使用notepad转换成UTF-8-BOM

****************************************************************************************************
5. 定时任务

    参考地址：https://blog.csdn.net/zwq912318834/article/details/77806737
    注意:定时任务执行的bat文件的路径不允许含有中文

****************************************************************************************************
6. pymysqlpool设置
详见pipelines_pymysqlpool.py文件

****************************************************************************************************
7. cookie池设置
以微博为例