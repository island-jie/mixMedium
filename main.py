# -*- coding:utf-8 -*-
import os

from utils import readConfig
from utils import newsPandas
from DataPreprocess import preProcess
from scrapy import cmdline

current_folder_path = os.path.dirname(os.path.realpath(__file__))       #当前项目路径
config_path = os.path.join(current_folder_path,'config.ini')

# 获取数据存放目录路径
data_path = os.path.join(current_folder_path, 'data')
raw_news_folder_path = os.path.join(data_path, 'rawNews')
cut_news_folder_path = os.path.join(data_path, 'cutNews')
extra_dicts_path = os.path.join(data_path, 'extra_dicts')


def main_spider():
    """
    数据爬虫主函数
    :return:
    """
    cmdline.execute([])

def main_preProcess():
    """
    数据处理主函数，
    :return:
    """
    raw_news_path =  os.path.join(raw_news_folder_path, 'rawNews.csv')
    # 从数据库读取新闻，存储至rawNews文件夹下
    newsPandas.mongoDB2csv(config_path, raw_news_path)

    # 加载新闻
    raw_news_df = newsPandas.load_news(raw_news_path)
    print("原始新闻语料的数据shape：" + str(raw_news_df.shape))

    # 过滤没有正文的新闻，并且根据url、title去重,并存储
    filter_news_df = preProcess.data_filter(raw_news_df)
    newsPandas.save_news(filter_news_df, os.path.join(raw_news_folder_path, 'filterNews.csv'))
    print("去重新闻语料的数据shape：" + str(filter_news_df.shape))

    print('以下新闻标题预处理：')
    #下面进行分词操作
    cut_news_df = filter_news_df.copy()
    #pandas单列运算
    cut_news_df['title_'] = cut_news_df['title'].map(lambda x: preProcess.clean_title_blank(x))     #清除新闻标题空白字符
    print('清除新闻标题空白字符 Success')
    cut_news_df['title_'] = cut_news_df['title_'].map(lambda x: preProcess.get_num_en_ch(x))  # 保留数字&英文&中文
    print('保留数字&英文&中文 Success')
    cut_news_df['title_cut'] = cut_news_df['title_'].map(lambda x: preProcess.pseg_cut(  # 分词 + 词性标注
        x, userdict_path=os.path.join(extra_dicts_path, 'userdict.txt')))
    print('分词 + 词性标注 Success')
    cut_news_df['title_cut'] = cut_news_df['title_cut'].map(lambda x: preProcess.get_words_by_flags(  # 获取特定词性的词汇
        x, flags=['n.*', 'v.*', 'eng', 't', 's', 'j', 'l', 'i']))
    print('获取特定词性的词汇 Success')
    cut_news_df['title_cut'] = cut_news_df['title_cut'].map(lambda x: preProcess.stop_words_cut(  # 去除停用词
        x, os.path.join(extra_dicts_path, 'HG_stopWords.txt')))
    print('去除停用词 Success')
    cut_news_df['title_cut'] = cut_news_df['title_cut'].map(lambda x: preProcess.disambiguation_cut(  # 消除歧义  词汇替换
        x, os.path.join(extra_dicts_path, 'disambiguation_dict.json')))
    print('消除歧义 Success')
    cut_news_df['title_cut'] = cut_news_df['title_cut'].map(lambda x: preProcess.individual_character_cut(  # 消除无用单字
        x, os.path.join(extra_dicts_path, 'individual_character_dict.txt')))
    print('消除无用单字 Success')
    cut_news_df['title_'] = cut_news_df['title_cut'].map(lambda x: ' '.join(x))  # 插入空格
    print('插入空格 Success')

    print('-------------------------------------------------------------')
    print('以下新闻正文预处理：')
    cut_news_df['content_'] = cut_news_df['content'].map(lambda x: preProcess.clean_content(x))     #清理新闻正文内容
    print('清理新闻正文内容 Success')
    cut_news_df['content_'] = cut_news_df['content_'].map(lambda x: preProcess.get_num_en_ch(x))    #保留数字&英文&中文
    print('保留数字&英文&中文 Success')
    cut_news_df['content_cut'] = cut_news_df['content_'].map(lambda x: preProcess.pseg_cut(         #分词 + 词性标注
        x, userdict_path=os.path.join(extra_dicts_path, 'userdict.txt')))
    print('分词 + 词性标注 Success')
    cut_news_df['content_cut'] = cut_news_df['content_cut'].map(lambda x: preProcess.get_words_by_flags(    #获取特定词性的词汇
        x, flags=['n.*', 'v.*', 'eng', 't', 's', 'j', 'l', 'i']))
    print('获取特定词性的词汇 Success')
    cut_news_df['content_cut'] = cut_news_df['content_cut'].map(lambda x: preProcess.stop_words_cut(        #去除停用词
        x, os.path.join(extra_dicts_path, 'HG_stopWords.txt')))
    print('去除停用词 Success')
    cut_news_df['content_cut'] = cut_news_df['content_cut'].map(lambda x: preProcess.disambiguation_cut(    #消除歧义  词汇替换
        x, os.path.join(extra_dicts_path, 'disambiguation_dict.json')))
    print('消除歧义 Success')
    cut_news_df['content_cut'] = cut_news_df['content_cut'].map(lambda x: preProcess.individual_character_cut(  #消除无用单字
        x, os.path.join(extra_dicts_path, 'individual_character_dict.txt')))
    print('消除无用单字 Success')
    cut_news_df['content_'] = cut_news_df['content_cut'].map(lambda x: ' '.join(x))                             #插入空格
    print('插入空格 Success')
    newsPandas.save_news(cut_news_df, os.path.join(cut_news_folder_path, 'cutNews.csv'))
    print('写入文件 Success')

if __name__ == '__main__':
    #先爬虫
    main_spider()
    #预处理
    main_preProcess()
