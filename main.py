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

from login import Login_class
from booking_ticket import Booking_ticket_class
from query_train_info import Query_train_info



class Grab_ticket_12306():
    
    def __init__(self, username, password):
        
        self.run_session = requests.Session()
        self.login_class = Login_class(self.run_session, username=username, password=password)

        self.seat_name_to_id_dict = {
                                        "商务座": "A9",
                                        "一等座": "M",
                                        "二等座": "O",
                                        "EMU卧": "F",
                                        "无座": "WZ",
                                        "硬座": "A1",
                                        "硬卧": "A3",
                                        "软卧": "A4",
                                        "高级软卧": "A6"
                                    }
        
        self.seat_id_to_name_dict = {v: k for k, v in self.seat_name_to_id_dict.items()}
        
        # 读取站点名和对应的站点号
        self.site_name_to_code_dict = {}
        with open("city_id", "r", encoding="utf-8") as f:
            site_name_to_code_list = f.readlines()
        site_name_to_code_list = list(map(lambda x:x.strip(), site_name_to_code_list))
        for row in site_name_to_code_list:
            key = row.split("|")[0]
            value = row.split("|")[1]
            self.site_name_to_code_dict.setdefault(key, value)
            
    def login(self):
        '''
        登陆
        :return: 成功True
                 失败False
        '''
        login_status, self.run_session = self.login_class.login_method()
        if login_status == False:
            logger.info("登陆失败")
            return False
        return True

    def query_train_info(self):
        '''
        查询火车信息
        :return:        False, False
                        True, train_info_dict
        '''
        query_train_info_class = Query_train_info(self.run_session)
        
        # 读取配置信息
        booking_after_time = config.BOOKING_AFTER_TIME
        booking_before_time = config.BOOKING_BEFORE_TIME
        train_date = config.TRAIN_DATE
        train_name = config.TRAIN_NAME
        from_station_code = self.site_name_to_code_dict[config.FROM_STATION]
        to_station_code = self.site_name_to_code_dict[config.TO_STATION]
        purpose_codes = "ADULT"
        
        train_info_dict = False
        while train_info_dict == False:
            # 获取符合条件的列车信息列表
            logger.info("正在获取符合条件的列车信息列表...")
            train_info_dict_list = query_train_info_class.get_train_info_dict_list(booking_after_time=booking_after_time,
                                                                                   booking_before_time=booking_before_time,
                                                                                   train_date=train_date,
                                                                                   from_station=from_station_code,
                                                                                   to_station=to_station_code,
                                                                                   purpose_code=purpose_codes)
            if train_info_dict_list == False:
                continue
            train_info_dict = query_train_info_class.get_train_info_dict(train_name=train_name,
                                                                         train_info_dict_list=train_info_dict_list)
        try:
            secret_str = train_info_dict['secret']
        except ValueError:
            logger.info("当前车次没有secret")
            return False, False
        if not secret_str:
            logger.info("尝试获取列车secret码失败, 原因:空值")
            return False, False
        return True, train_info_dict
    
    def send_booking_ticket_result(self, result_str):
        '''
        发送订票结果
        :param result_str: 订票结果正文
        :return:           成功:True
                           失败:False
        '''
        # subject = "[{0}]12306抢票结果通知".format(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        subject = ("12306抢票结果通知, 席位已锁定, 请于30分钟内支付")
        if send_email(subject, result_str) == False:
            # logger.info("发送邮件通知失败")
            return False
        # logger.info("发送邮件通知成功")
        return True
      
    def main(self):
        # 登陆
        if self.login() == False:
            return False
        
        # 获取订票要用的火车信息
        query_train_info_status, train_info_dict = self.query_train_info()
        if query_train_info_status == False:
            return False

        # 订票需要的信息
        secret_str = train_info_dict['secret']
        train_date = config.TRAIN_DATE
        back_train_date = str(time.strftime("%Y-%m-%d", time.localtime()))
        purpose_code = "ADULT"
        from_station = config.FROM_STATION
        to_station = config.TO_STATION
        passenger_name = config.PASSENGER_NAME
        document_type = config.DOCUMENT_TYPE
        document_number = config.DOCUMENT_NUMBER
        mobile = config.MOBILE
        seat_type = self.seat_name_to_id_dict[config.SEAT_TYPE]
        expect_seat_number = config.EXPECT_SETA_NUM
        # 订票
        booking_ticket_class = Booking_ticket_class(self.run_session)
        booking_ticket_status, booking_ticket_result = booking_ticket_class.booking_ticket_method(secret_str,
                                                                                                  train_date,
                                                                                                  back_train_date,
                                                                                                  purpose_code,
                                                                                                  from_station,
                                                                                                  to_station,
                                                                                                  passenger_name,
                                                                                                  document_type,
                                                                                                  document_number,
                                                                                                  mobile,
                                                                                                  seat_type,
                                                                                                  expect_seat_number)
        if booking_ticket_status == False:
            logger.info("订票失败")
            return False
        
        if self.send_booking_ticket_result(booking_ticket_result) == False:
            logger.info("发送邮件通知失败")
            return False
        logger.info("发送邮件通知成功")
        return True
    
if __name__ == "__main__":
    grab_ticket_12306 = Grab_ticket_12306(username=config.USERNAME_12306, password=config.PASSWORD_12306)
    grab_ticket_12306.main()
    
    
    