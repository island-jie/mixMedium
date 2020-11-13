# -*- coding:utf-8 -*-

"""
处理数据存储格式
"""
import pandas as pd
import pymongo
import re

import readConfig


def save_news(news_df, path):
    """
    保存新闻
    :param news_df:
    :param path:
    :return:
    """
    news_df.to_csv(path, index=False, encoding='utf-8')

def mongoDB2csv(config_path, csv_path):
    """
    读取mongoDB数据库，转存csv格式
    :param csv_path:
    :return:
    """
    # 连接mongodb数据库
    MONGODB_PARAMS = readConfig.read_conf_mongoDB(config_path)
    MONGODB_HOST = MONGODB_PARAMS['host']
    MONGODB_DB = MONGODB_PARAMS['db']
    MONGODB_TABLE = MONGODB_PARAMS['table']
    client = pymongo.MongoClient(MONGODB_HOST)
    # 连接数据库
    db = client[MONGODB_DB]
    # 数据表
    news = db[MONGODB_TABLE]
    # 将mongodb中的数据读出
    data = pd.DataFrame(list(news.find()))
    # 保存为csv格式
    save_news(data, csv_path)

def replace_line_terminator(x):
    """
    替换行终止符
    :param x:
    :return:
    """
    try:
        x = re.sub(r'\r\n', '\n', x)
    except TypeError:
        pass
    return x


def load_news(path):
    """
    加载新闻
    :param path: csv文件路径
    :return: 返回pandas
    """
    news_df = pd.read_csv(path, encoding='utf-8')
    news_df = news_df.applymap(replace_line_terminator)
    return news_df

