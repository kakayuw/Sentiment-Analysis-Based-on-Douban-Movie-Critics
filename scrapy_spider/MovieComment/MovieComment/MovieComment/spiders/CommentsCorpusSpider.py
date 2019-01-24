import csv
import os
import re
import time
import jieba

import scrapy


class MovieCommentSpider(scrapy.Spider):
    # 爬虫唯一标识符
    name = 'CommentCorpus'

    # 爬取页面地址
    base_url = 'https://movie.douban.com/j/search_subjects?type=movie&tag=' \
               '%E7%83%AD%E9%97%A8&sort=recommend&page_limit=20&page_start='

    # 爬取条目数量
    item_count = 0
    # 爬取条目上限
    item_max_count = 20

    def __init__(self):
        self.file = open('CommentsCorpus626.txt', 'w', encoding='utf8', newline='')

    def start_requests(self):
        for i in range(20):
            url = self.base_url + str(i * 20)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.item_count = self.item_count + 1
        if self.item_count > self.item_max_count:
            return

        # from id list to generate comment urls : h, m, l
        if "search_subjects" in response.url:
            ids = []
            items = str(response.body).split("subject")
            for item in items:
                for j in re.findall(r"\d+\.?\d*", item[3:15]):
                    ids.append(j)
            del ids[0:2]
            for i in ids:
                url = "https://movie.douban.com/subject/" + i + \
                      "/comments?start=0&limit=20&sort=new_score&status=P&percent_type="
                url1 = "https://movie.douban.com/subject/" + i + \
                       "/comments?start=20&limit=20&sort=new_score&status=P&percent_type="
                url2 = "https://movie.douban.com/subject/" + i + \
                       "/comments?start=40&limit=20&sort=new_score&status=P&percent_type="
                urls = [url + "h", url + "m", url + "l",
                        url1 + "h", url1 + "m", url1 + "l",
                        url2 + "h", url2 + "m", url2 + "l"]
                for u in urls:
                    yield scrapy.Request(url=u, callback=self.parse)
        # from comment page crawl down data into csv
        else:
            movies = response.css("div.comment-item")
            for movie in movies:
                comment = movie.css(".comment p::text").extract_first()
                comment = comment.replace('\t', '').replace('\n', '').replace('  ', '')
                comment = comment.encode("GB18030")
                seg_list = jieba.cut(comment, cut_all=False)
                self.file.write(" ".join(seg_list) + '\n')

            # 及时将内容写入文件，否则可能会出现少许延迟
            self.file.flush()
            os.fsync(self.file)
            # 输出当前解析完成的网页网址，可以当做爬取进度来看待,与程序逻辑无关
            print("over: " + response.url)
            time.sleep(0.2)

    def close(self, spider, reason):
        self.file.close()

