import configparser
import os
conf= configparser.ConfigParser()


def read_conf_MySQL(configPath):
    """
    读取配置文件
    :param configPath: config文件路径
    :return: 返回config参数
    """
    ''''''
    conf.read(configPath) # 文件路径
    # print(conf)
    # print(conf.sections())
    # print(conf.options("mysql"))
    # print(conf.items("mysql"))
    host = conf.get('mysql', 'host')
    username = conf.get('mysql', 'username')
    password = conf.get('mysql', 'password')
    db = conf.get('mysql', 'db')
    charset = conf.get('mysql', 'charset')
    port = conf.getint('mysql', 'port')
    mysqlConfig = {'host': host, 'username': username, 'password': password,
                   'db': db, 'charset': charset, 'port': port}
    return mysqlConfig

def read_conf_mongoDB(configPath):
    """
    读取配置文件
    :param configPath: config文件路径
    :return: 返回config参数
    """
    ''''''
    conf.read(configPath) # 文件路径
    # print(conf)
    # print(conf.sections())
    # print(conf.options("mysql"))
    # print(conf.items("mysql"))
    host = conf.get('mongoDB', 'host')
    db = conf.get('mongoDB', 'db')
    table = conf.get('mongoDB', 'table')

    mongoDBConfig = {'host': host, 'table': table, 'db': db}
    return mongoDBConfig

