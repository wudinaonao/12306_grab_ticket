'''
    查询符合条件的火车信息, 返回一个列表, 每个元素为一个字典
    
'''
import requests
import time
import re
import random
import json
from show_captcha import show_captcha
from show_captcha import show_mark_result
from urllib.parse import unquote
from log_model import logger
from print_tabel import print_table
from urllib.parse import quote_plus
from send_msg import send_email
from send_msg import send_email_test
from datetime import datetime

import config
import hashlib
from lxml import etree
import time

class Query_train_info():
    
    def __init__(self, run_session):
        self.run_session = run_session
        
    def get_train_info_dict_list(self, booking_after_time, booking_before_time, train_date, from_station, to_station,
                                 purpose_code):
        '''
        获取列车信息, 返回一个列表, 每个元素为一个符合条件的字典

        :param train_date:      出发日期
        :param from_station:    出发站
        :param to_station:      终到站
        :param purpose_code:    乘客类型 例如:ADULT
        :return:                成功返回:列车信息字典列表
                                失败返回:False
        '''
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        }
        base_url = "https://kyfw.12306.cn/otn/leftTicket/"
        query_url = "https://kyfw.12306.cn/otn/leftTicket/queryZ"
        params = {
            "leftTicketDTO.train_date": train_date,
            "leftTicketDTO.from_station": from_station,
            "leftTicketDTO.to_station": to_station,
            "purpose_codes": purpose_code
        }
        # 查询列车信息
        res = self.run_session.get(url=query_url, headers=headers, params=params)
        if res.url == "https://www.12306.cn/mormhweb/logFiles/error.html":
            logger.info("查询超时, 请稍后再试!")
            return False
        try:
            json_data = json.loads(res.text)
        except ValueError:
            logger.info("获取列车信息失败, 原因:返回的数据不是json格式, 可能查询超时, 请稍后再试!")
            return False
        try:
            # 如果返回json显示status为false, 可能是请求url错误
            # 根据返回个url提示拼接正确请求url重新尝试
            while json_data['status'] == False:
                query_url_interface = json_data['c_url'].split("/")[-1]
                query_url = base_url + query_url_interface
                res = self.run_session.get(url=query_url, headers=headers, params=params)
                # 出现错误页面
                if res.url == "https://www.12306.cn/mormhweb/logFiles/error.html":
                    logger.info("查询超时, 请稍后再试!")
                    continue
                try:
                    json_data = json.loads(res.text)
                except ValueError:
                    logger.info("获取列车信息失败, 原因:返回的数据不是json格式, 可能查询超时, 请稍后再试!")
                    return False
        except:
            logger.info("获取列车信息失败, 原因:尝试解析Json的时候发生错误!")
            return False
        # 处理列车信息,每个列车信息为一个字典,生成一个列表
        result_dict_list = []
        # 转换time从string到datetime对象
        booking_after_time = datetime.strptime(str(booking_after_time), "%H:%M")
        booking_before_time = datetime.strptime(str(booking_before_time), "%H:%M")
        try:
            for info in json_data['data']['result']:
                info = info.split("|")
                # if info[3] == train_name:
                train_start_time = datetime.strptime(str(info[8]), "%H:%M")
                if booking_after_time <= train_start_time <= booking_before_time:
                    result_dict = {}
                    result_dict.setdefault("secret", unquote(info[0]).replace("\n", ""))
                    result_dict.setdefault("train_no", info[2])
                    result_dict.setdefault("train_name", info[3])
                    result_dict.setdefault("start_time", info[8])
                    result_dict.setdefault("end_time", info[9])
                    result_dict.setdefault("continue_time", info[10])
                    result_dict.setdefault("train_status", info[11])
                    result_dict.setdefault("train_date", info[13])
                    result_dict.setdefault("start_num", info[16])
                    result_dict.setdefault("end_num", info[17])
                    result_dict.setdefault("train_id", info[35])
                    result_dict_list.append(result_dict)
            if result_dict_list:
                return result_dict_list
            else:
                return False
        except:
            return False
    
    def get_train_info_dict(self, train_name, train_info_dict_list):
        '''
        输入train_name(列车班次)返回对应的train_info_dict, 如果train_name为空的话则返回train_info_dict_list的一个字典
        :param train_name:  列车班次
        :return:            成功返回train_info_dict
                            失败返回False
        '''
        
        train_info_dict = {}
        # 如果用户指定了列车名, 则查找指定列车名的字典
        if train_name:
            for train_info_dict_from_list in train_info_dict_list:
                if train_info_dict_from_list['train_status'] == "Y":
                    if train_info_dict_from_list['train_name'] == train_name:
                        train_info_dict = train_info_dict_from_list
            # 如果没找到返回list第一个status=Y的字典
            if not train_info_dict:
                for i, _ in enumerate(train_info_dict_list):
                    if train_info_dict_list[i]['train_status'] == "Y":
                        train_info_dict = train_info_dict_list[i]
                        break
        else:
            # 返回list第一个status = Y的字典
            for i, _ in enumerate(train_info_dict_list):
                if train_info_dict_list[i]['train_status'] == "Y":
                    train_info_dict = train_info_dict_list[i]
                    break
        if train_info_dict:
            return train_info_dict
        else:
            return False