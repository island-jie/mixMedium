import requests
from bs4 import BeautifulSoup
import json
import re
import pandas as pd
import MysqlHelper
import time
from utils import readConfig


class News:
    def __init__(self, searchName, searchArea='news'):
        """
        init parameters
        Args:
            searchName：搜索关键字
            searchArea:搜索范围，默认为新闻
        Returns:
            NULL
        """
        self.head = {
            'User-Agent' :"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/61.0.3163.79 Safari/537.36",
            'Cookie' : "UOR=,k.sina.com.cn,; SINAGLOBAL=171.217.92.127_1558922890.497388; Apache=171.217.92.127_"
                       "1558922890.497390; ULV=1558922899005:2:2:2:171.217.92.127_1558922890.497390:1558922890476; "
                       "U_TRS1=0000007f.8da65be9.5ceb5bda.d813a4df; U_TRS2=0000007f.8db85be9.5ceb5bda.5119306e; "
                       "WEB2_OTHER=ea4b3c7f7d9d067e32500238120cd1b6; SUB=_2AkMrt9TAf8NxqwJRmP0TxGvqZIh2zwjEieKd6yUbJRM"
                       "yHRl-yD83qh0gtRB6ADf6Lx2uvK1-lDL0cQSEo7_kxmqyVI1u; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WFSsFZ"
                       "ZQkpLzpzZDRWlR4_j; ULOGIN_IMG=gz-1ce8d0f8e61941477ad657acb3495d473d56; UM_distinctid=16af7db4ddc"
                       "287-0dc58dcf9bf925-1781c36-100200-16af7db4ddd29d; lxlrttp=1556243090;verify=False"
        }
        self.searchName = searchName
        self.searchArea = searchArea

        self.total_urls = []
        self.total_news = []

        self.url = 'https://www.baidu.com/s?ie=utf-8&medium=2&tn={}&word={}&pn={}'

    #给一个搜索结果页面 输出 10条链接 & 新闻总数
    def getListLinks(self,url):
        """
        给一个搜索结果页面 输出 10条链接 & 新闻总数
        Args:
            url:搜索结果的链接
        Returns:
            10条链接 & 新闻总数
        """
        urls = []
        response = requests.get(url, headers= self.head)
        # response.encoding = 'utf-8'
        html = response.text
        # 得到的网页，判断是否有找到news
        soup = BeautifulSoup(html, 'html.parser')
        try:
            nums = soup.select(".nums")[0].text  # 找到相关资讯约712,000篇
        except Exception as e:
            nums = ''
            print(e)
        if nums != '':
            purl = ''
            nums_list = re.findall(r'[0-9]\d*', nums)       #['712', '000']
            for x in nums_list:
                purl = purl + x
            numsCount = int(purl)       # 总的新闻数     712000

            reg = soup.select('h3 a')
            for eachone in reg:
                urls.append(eachone['href'])
        else:
            numsCount = 0
        return urls,numsCount

    def getArticle(self,news_url):
        """
        获取新闻正文文章
        Args:
            news_url：每条新闻具体链接
        Returns:
            文章正文
        """
        #time.sleep(3)
        article = []
        res = requests.get(news_url)

        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        #以id来取  id可能为 artibody 和 article
        for p in soup.select('#article p'):
            if(not(p.text.startswith('来源：') or p.text.startswith('作者：'))):
                article.append(p.text.strip())
        return ' '.join(article)


    def getNewsDetail(self,news_url):
        """
        获取新闻具体细节
        Args:
            search_url:每条新闻具体链接
        Returns:
            新闻链接、标题、正文、时间、日期
        """
        result = {}
        res = requests.get(news_url)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        if(len(soup.select('.article-title h2')) > 0 and len(soup.select('.date')[0]) > 0 and len(soup.select('.time')[0]) > 0):
            result['url'] = news_url
            result["title"] = soup.select('.article-title h2')[0].text
            result["date"] = soup.select('.date')[0].text.lstrip('发布时间：')
            result["time"] = soup.select('.time')[0].text
            #source = soup.select('.account-authentication')[0].text
            #print(title,date,time,source)
            if len(result["date"]) == 5:
                result["datetime"] = "2020-" + result["date"] + " " + result["time"]
            elif len(result["date"]) == 8:
                result["datetime"] = "20" + result["date"] + " " + result["time"]
            else:
                result["datetime"] =result["date"] + " " + result["time"]
            result["article"] = self.getArticle(news_url)
            msh = MysqlHelper.MysqlHelper(host="localhost", username="root",password="123456",db="baiduSearchNews",charset="utf8",port=3306)
            msh.connect()
            sql = "insert into disease values('%s','%s','%s','%s')" %(result["article"],result["datetime"],result["title"],result['url'])
            msh.insert(sql)
        #return  result


    def save2MySQL(self,page):
        """
        存储新闻
        Args:
            page:获取新闻的页数，一页10条
        Returns:
            所有新闻
        """
        for i in range(1, page):
            cur_url = self.url.format(self.searchArea, self.searchName, (i - 1) * 10)
            news_nums = self.getListLinks(cur_url)[1]
            urls = self.getListLinks(cur_url)[0]
            self.total_urls.extend(urls)
        i = 0
        for item in self.total_urls:
            self.getNewsDetail(item)
            i += 1
            print(item + "   " + str(i))

    # def save2mysql(self):
    #     conn = MysqlHelper.MysqlHelper(host="localhost", username="root", password="123456", db="topic_evolution",
    #                                    charset="utf8", port=3306)
    #     conn.connect()
    #     sql = "insert into news values(%s,%s,%s,%s,%s)"
    #     all_news = self.save2List()
'''
if __name__=='__main__':
    key_word = "***"
    type = "news"
    pageNum = 2

    news = News(key_word,type)
    total_news = news.save(pageNum + 1)
    # 存储到excel中
    df = pd.DataFrame(total_news)
    df.to_excel('news1.xlsx')
'''
