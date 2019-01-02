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

class Booking_ticket_class():
    
    def __init__(self, run_session):
        self.run_session = run_session
        self.INIT_HTML_DICT = {}
        self.REPEAT_SUBMIT_TOKEN = ""
        
    def set_report_submit_token(self, html_text):
        '''
        输入HTML 查找 report_submit_token
        :return:
        '''
        init_html = etree.HTML(html_text)
        script_path = "/html/head/script/text()"
        script_list = init_html.xpath(script_path)[0].split("\n")
        for row in script_list:
            if "globalRepeatSubmitToken" in row:
                self.REPEAT_SUBMIT_TOKEN = row[row.find("'") + 1:-2]
        if self.REPEAT_SUBMIT_TOKEN == "":
            return False
        return True
    
    def get_train_date_gmt(self, train_date):
        '''
            计算gmt时间
        :param train_date:
        :return:            gmt时间字符串
        '''
        train_date = int(train_date) // 1000
        time_list = time.ctime(train_date).split(" ")
        try:
            time_list.remove("")
        except:
            pass
        time_list[-1], time_list[-2] = time_list[-2], time_list[-1]
        if len(time_list[2]) == 1:
            time_list[2] = "0" + time_list[2]
        time_list = list(map(lambda x: quote_plus(x), time_list))
        time_difference = time.localtime()[3] - time.gmtime()[3]
        if time_difference >= 0:
            gmt_str = "GMT+" + str((time.localtime()[3] - time.gmtime()[3]) * 100).zfill(4)
        else:
            gmt_str = "GMT-" + str(abs((time.localtime()[3] - time.gmtime()[3]) * 100)).zfill(4)
        gmt_str = quote_plus(gmt_str)
        # gmt_str = quote_plus("GMT+0100")
        # zone_str = quote_plus("中欧标准时间")
        return "+".join(time_list) + "+" + gmt_str  # + "+(" + zone_str + ")"
    
    def get_booking_ticket_result_dict(self, html_text):
        '''
        输入HTML 返回订票结果
        :param html_text:
        :return:            成功返回booking_ticket_result_json_data 结果字典
                            失败返回False
        '''
        init_html = etree.HTML(html_text)
        script_path = '/html//script/text()'
        script_list = init_html.xpath(script_path)[-1].split("\n")
        booking_ticket_result_json_data = None
        for row in script_list:
            if "var passangerTicketList" in row:
                json_str = row[row.find("{"):-2].replace("'", '"')
                booking_ticket_result_json_data = json.loads(json_str)
        if booking_ticket_result_json_data is not None:
            return booking_ticket_result_json_data
        else:
            return False
    
    def set_init_html_dict(self, html_text):
        '''
        输入HTML 查找 report_submit_token
        :return: repor_submit_token
        '''
        init_html = etree.HTML(html_text)
        script_path = '/html//script/text()'
        script_list = init_html.xpath(script_path)[3].split("\n")
        for row in script_list:
            if "var ticketInfoForPassengerForm={" in row:
                json_str = row[row.find("{"):-1].replace("'", '"')
                try:
                    self.INIT_HTML_DICT = json.loads(json_str)
                except ValueError:
                    logger.info("读取init网页信息失败, 因为从script截取的数据可能不是json格式")
                    return False
        if self.INIT_HTML_DICT:
            return True
        else:
            return False
    
    def meger_data_to_string(self, data_dict):
        '''
        把字典转换成字符串
        例如:
                {"a":"1","b":"2"}  ==>  "a=1&b=2"

        :param data_dict:
        :return:
        '''
        data_str = ""
        for data in data_dict.keys():
            data_str += data + "=" + data_dict[data] + "&"
        return data_str[:-1]
    
    def submit_order_requests(self,
                              secret_str,
                              train_date,
                              back_train_date,
                              purpose_code,
                              query_from_station_name,
                              query_to_station_name):
        '''
        请求 submit_order_requests 页面
        :param secret_str:                  列车鉴别码
        :param train_date:                  train_date
        :param back_train_date:             back_train_date
        :param purpose_code:                purpose_code
        :param query_from_station_name:     query_from_station_name
        :param query_to_station_name:       query_to_station_name
        :return:                            成功 True
                                            失败 False
        '''
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            "Host": "kyfw.12306.cn",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        submit_order_requests_url = "https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest"
        # referer_1 = "https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs=" + \
        #             quote_plus(from_station, encoding="utf-8") + "," + self.site_name_to_code_dict[from_station] + \
        #             "&ts=" + \
        #             quote_plus(to_station, encoding="utf-8") + "," + self.site_name_to_code_dict[to_station] + \
        #             "&date=" + train_date + "&flag=N,N,Y"
        # headers['Referer'] = referer_1
        headers['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
        submit_order_requests_data = {
            "secretStr": secret_str,
            "train_date": train_date,
            "back_train_date": back_train_date,
            "tour_flag": "dc",
            "purpose_codes": purpose_code,  # ADULT
            "query_from_station_name": query_from_station_name,
            "query_to_station_name": query_to_station_name,
            "undefined": ""
        }
        submit_order_requests_req = self.run_session.post(url=submit_order_requests_url, headers=headers,
                                                          data=submit_order_requests_data)
        try:
            submit_order_requests_json_data = json.loads(submit_order_requests_req.text)
        except ValueError:
            logger.info("订票 submit_order_requests 返回的数据不是Json格式")
            return False
        if submit_order_requests_json_data['status'] == False:
            logger.info("返回信息:{0}".format(submit_order_requests_json_data['messages']))
            return False
        return True
    
    def init_dc(self):
        '''
        请求 https://kyfw.12306.cn/otn/confirmPassenger/initDc 页面

        :return:        成功 True
                        失败 False
        '''
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            "Host": "kyfw.12306.cn",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        # init_dc
        init_dc_url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
        init_dc_data = {
            "_json_att": ""
        }
        init_dc_req = self.run_session.post(url=init_dc_url, headers=headers, data=init_dc_data)
        # 这个页面会返回很多有用的信息, 有时间仔细看下
        if self.set_report_submit_token(init_dc_req.text) == False:
            logger.info("在尝试设置report_submit_token的时候发生错误!")
            return False
        if self.set_init_html_dict(init_dc_req.text) == False:
            logger.info("在尝试设置初始化信息的时候发生错误!")
            return False
        if not self.REPEAT_SUBMIT_TOKEN:
            logger.info("REPEAT_SUBMIT_TOKEN 获取失败.")
            return False
        return True
    
    def get_passenger_dto(self):
        '''
        请求 https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs 页面

        :return:        成功 True
                        失败 False
        '''
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            "Host": "kyfw.12306.cn",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
        }
        get_passenger_dto_url = "https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs"
        get_passenger_dto_data = {
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": self.REPEAT_SUBMIT_TOKEN
        }
        get_passenger_dto_req = self.run_session.post(url=get_passenger_dto_url, headers=headers,
                                                      data=get_passenger_dto_data)
        try:
            get_passenger_dto_json_data = json.loads(get_passenger_dto_req.text)
        except ValueError:
            logger.info("订票 get_passenger_dto 返回的数据不是Json格式")
            return False
        if get_passenger_dto_json_data['data']['isExist'] == False:
            logger.info("返回信息:{0}".format(get_passenger_dto_json_data['data']['exMsg']))
            return False
        return True
    
    def check_order_info(self, seat_type, passenger_name, document_type, document_number, mobile):
        '''
        请求 https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo 页面
        :param seat_type:           seat_type
        :param passenger_name:      passenger_name
        :param document_type:       document_type
        :param document_number:     document_number
        :param mobile:              mobile
        :return:                    成功  True, passengerTicketStr, oldPassengerStr
                                    失败  False, False, False
        '''
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            "Host": "kyfw.12306.cn",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
        }
        check_order_info_url = "https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo"
        passengerTicketStr = ",".join([seat_type,
                                       "0",
                                       "1",
                                       passenger_name,
                                       str(document_type),
                                       str(document_number),
                                       str(mobile),
                                       "N"])
        oldPassengerStr = ",".join([passenger_name,
                                    str(document_type),
                                    str(document_number),
                                    "1_"])
        check_order_info_data = {
            "cancel_flag": "2",
            "bed_level_order_num": "000000000000000000000000000000",
            "passengerTicketStr": passengerTicketStr,  
            "oldPassengerStr": oldPassengerStr,
            "tour_flag": "dc",
            "randCode": "",
            "whatsSelect": "1",
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": self.REPEAT_SUBMIT_TOKEN
        }
        check_order_info_req = self.run_session.post(url=check_order_info_url, headers=headers,
                                                     data=check_order_info_data)
        try:
            check_order_info_json_data = json.loads(check_order_info_req.text)
        except ValueError:
            logger.info("订票 check_order_info 返回的数据不是Json格式")
            return False, False, False
        if check_order_info_json_data['data']['submitStatus'] == False:
            logger.info("返回信息:{0}".format(check_order_info_json_data['data']['errMsg']))
            return False, False, False
        return True, passengerTicketStr, oldPassengerStr
    
    def get_queue_conut(self, seat_type):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            "Host": "kyfw.12306.cn",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
        }
        # get_queue_conut
        get_queue_conut_url = "https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount"
        if not self.REPEAT_SUBMIT_TOKEN:
            logger.info("LEFT_TICKET 获取失败.")
            return False
        
        train_date_gmt = self.get_train_date_gmt(self.INIT_HTML_DICT['orderRequestDTO']['train_date']['time'])
        # train_date_gmt = str(self.INIT_HTML_DICT['orderRequestDTO']['train_date']['time'])
        get_queue_conut_data = {
            "_json_att": "",
            "fromStationTelecode": self.INIT_HTML_DICT['orderRequestDTO']['from_station_telecode'],  # 起始站号码
            "leftTicket": self.INIT_HTML_DICT['leftTicketStr'],
            "purpose_codes": self.INIT_HTML_DICT['purpose_codes'],  # 乘客码
            "REPEAT_SUBMIT_TOKEN": self.REPEAT_SUBMIT_TOKEN,  # 估计是一个随机码
            "seatType": seat_type,  # 座位类型
            "stationTrainCode": self.INIT_HTML_DICT['orderRequestDTO']['station_train_code'],  # 列车车次
            "toStationTelecode": self.INIT_HTML_DICT['orderRequestDTO']['to_station_telecode'],  # 终到站号码
            "train_date": train_date_gmt,  # 列车时间
            "train_location": self.INIT_HTML_DICT['train_location'],  # 可能是站台?
            "train_no": self.INIT_HTML_DICT['queryLeftTicketRequestDTO']['train_no']  # 列车号
        }
        get_queue_conut_data_str = self.meger_data_to_string(get_queue_conut_data)
        get_queue_conut_req = self.run_session.post(url=get_queue_conut_url, headers=headers,
                                                    data=get_queue_conut_data_str)
        get_queue_conut_json_data = json.loads(get_queue_conut_req.text)
        if get_queue_conut_json_data['status'] == False:
            logger.info("返回信息:{0}".format(get_queue_conut_json_data['messages']))
            return False
        logger.info(" --- ".join(self.INIT_HTML_DICT['leftDetails']))
        return True
    
    def confirm_single_for_queue(self, expect_seat_number, passengerTicketStr, oldPassengerStr):
        # confirm_single_for_queue
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            "Host": "kyfw.12306.cn",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        confirm_single_for_queue_url = "https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue"
        expect_seat_number = "1" + expect_seat_number
        confirm_single_for_queue_data = {
            "_json_att": "",
            "choose_seats": expect_seat_number,  # 选择座位
            "dwAll": "N",
            "key_check_isChange": self.INIT_HTML_DICT['key_check_isChange'],
            "leftTicketStr": self.INIT_HTML_DICT['leftTicketStr'],
            "oldPassengerStr": oldPassengerStr,
            "passengerTicketStr": passengerTicketStr,
            "purpose_codes": self.INIT_HTML_DICT['purpose_codes'],
            "randCode": "",
            "REPEAT_SUBMIT_TOKEN": self.REPEAT_SUBMIT_TOKEN,
            "roomType": "00",
            "seatDetailType": "000",
            "train_location": self.INIT_HTML_DICT['train_location'],
            "whatsSelec": "1"
        }
        confirm_single_for_queue_req = self.run_session.post(url=confirm_single_for_queue_url, headers=headers,
                                                             data=confirm_single_for_queue_data)
        try:
            confirm_single_for_queue_json_data = json.loads(confirm_single_for_queue_req.text)
        except ValueError:
            logger.info("订票 confirm_single_for_queue 返回的数据不是Json格式")
            return False
        if confirm_single_for_queue_json_data['status'] != True or confirm_single_for_queue_json_data['data'][
            'submitStatus'] != True:
            logger.info("返回信息:{0}".format(confirm_single_for_queue_json_data['messages']))
            return False
        return True
    
    def query_order_wait_time(self):
        '''
        请求 https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime 页面
        :return:    成功返回 True, orderId
                    失败返回 False, False
        '''
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            "Host": "kyfw.12306.cn"
        }
        # query_order_wait_time
        query_order_wait_time_url = "https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime"
        
        orderId = None
        wait_time = 10
        
        while orderId == None and wait_time > 0:
            query_order_wait_time_data = {
                "_json_att": "",
                "random": str(int(time.time() * 1000)),
                "REPEAT_SUBMIT_TOKEN": self.REPEAT_SUBMIT_TOKEN,
                "tourFlag": "dc"
            }
            query_order_wait_time_req = self.run_session.get(url=query_order_wait_time_url,
                                                             headers=headers,
                                                             params=query_order_wait_time_data)
            # print(query_order_wait_time_req.text)
            try:
                query_order_wait_time_json_data = json.loads(query_order_wait_time_req.text)
                wait_time = int(query_order_wait_time_json_data['data']['waitTime'])
            except ValueError:
                logger.info("订票 query_order_wait_time 返回的数据不是Json格式")
                return False, False
            if query_order_wait_time_json_data['status'] != True:
                logger.info("返回信息:{0}".format(query_order_wait_time_json_data['messages']))
                return False, False
            # requestId = query_order_wait_time_json_data['data']['requestId']
            orderId = query_order_wait_time_json_data['data']['orderId']
            # if orderId is not None:
            #     break
            # else:
            logger.info("正在下单, 等待时间(s):{0:< 10}订单号:{1}".format(wait_time, orderId))
            if wait_time < 0 and orderId == None:
                logger.info("返回信息:{0}".format(query_order_wait_time_json_data['data']['msg']))
                break
            if orderId is not None:
                break
        return True, orderId
    
    def result_order_for_queue(self, orderId):
        '''
        请求 https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue 页面
        :param orderId: orderId(车票订单号)
        :return:        成功返回 True
                        失败返回 False
        '''
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            "Host": "kyfw.12306.cn",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        # result_order_for_queue
        result_order_for_queue_url = "https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue"
        result_order_for_queue_data = {
            "_json_att": "",
            "orderSequence_no": orderId,
            "REPEAT_SUBMIT_TOKEN": self.REPEAT_SUBMIT_TOKEN,
        }
        result_order_for_queue_req = self.run_session.post(url=result_order_for_queue_url, headers=headers,
                                                           data=result_order_for_queue_data)
        try:
            result_order_for_queue_json_data = json.loads(result_order_for_queue_req.text)
        except ValueError:
            logger.info("订票 result_order_for_queue 返回的数据不是Json格式")
            return False
        if result_order_for_queue_json_data['status'] != True or result_order_for_queue_json_data['data'][
            'submitStatus'] != True:
            logger.info("返回信息:{0}".format(result_order_for_queue_json_data['messages']))
            return False
        return True
    
    def result_booking_ticket_html(self):
        '''
        请求预定结果页面获取预定结果信息
        :return: 预定结果页面html信息
        '''
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            "Host": "kyfw.12306.cn",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        # result_booking_ticket_html
        result_booking_ticket_html_url = "https://kyfw.12306.cn/otn//payOrder/init?random=" + str(
            int(time.time() * 1000))
        result_booking_ticket_html_data = {
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": self.REPEAT_SUBMIT_TOKEN,
        }
        result_booking_ticket_html_req = self.run_session.post(url=result_booking_ticket_html_url, headers=headers,
                                                               data=result_booking_ticket_html_data)
        return result_booking_ticket_html_req.text
    
    def booking_ticket_method(self,
                              secret_str,
                              train_date,
                              back_train_date,
                              purpose_code,
                              query_from_station_name,
                              query_to_station_name,
                              passenger_name,
                              document_type,
                              document_number,
                              mobile,
                              seat_type,
                              expect_seat_number):
        '''
        预定车票
        :param secret_str:
        :param train_date:
        :param back_train_date:
        :param purpose_code:
        :param query_from_station_name:
        :param query_to_station_name:
        :param passenger_name:
        :param document_type:
        :param document_number:
        :param mobile:
        :param seat_type:
        :param train_info_dict:
        :param expect_seat_number:
        :return:                    成功返回True, 订票结果
                                    失败返回False, False
        '''
        logger.info("检查登陆状态...")
        check_user_req = Login_class.check_user(self.run_session)
        if check_user_req == False:
            return False, False
        # i = 0
        # while check_user_req == False:
        #     i += 1
        #     logger.info("用户未登录, 准备登陆...尝试次数:{0}".format(i))
        #     check_user_req = self.check_user()
        
        logger.info("提交订单请求...")
        submit_order_requests_req = self.submit_order_requests(secret_str,
                                                               train_date,
                                                               back_train_date,
                                                               purpose_code,
                                                               query_from_station_name,
                                                               query_to_station_name)
        if submit_order_requests_req == False:
            logger.info("获取提交订单请求失败!")
            return False, False
        
        logger.info("获取初始化数据并设置...")
        init_dc_req = self.init_dc()
        if init_dc_req == False:
            logger.info("获取初始化数据失败!")
            return False, False
        
        logger.info("获取乘客dto...")
        get_passenger_dto_req = self.get_passenger_dto()
        if get_passenger_dto_req == False:
            logger.info("获取乘客dto失败!")
            return False, False
        
        logger.info("检查订单信息...")
        check_order_info_req, passengerTicketStr, oldPassengerStr = self.check_order_info(seat_type,
                                                                                          passenger_name,
                                                                                          document_type,
                                                                                          document_number,
                                                                                          mobile)
        if check_order_info_req == False:
            logger.info("检查订单信息失败!")
            return False, False
        
        logger.info("获取排队信息...")
        get_queue_conut_req = self.get_queue_conut(seat_type)
        if get_queue_conut_req == False:
            logger.info("获取排队信息失败!")
            return False, False
        
        logger.info("获取确认信息...")
        confirm_single_for_queue_req = self.confirm_single_for_queue(expect_seat_number, passengerTicketStr,
                                                                     oldPassengerStr)
        if confirm_single_for_queue_req == False:
            logger.info("获取确认信息失败!")
            return False, False
        
        logger.info("查询订单等待时间...")
        query_order_wait_time_req, orderId = self.query_order_wait_time()
        if query_order_wait_time_req == False:
            logger.info("查询订单等待时间失败! 但是可能已经成功订票, 准备发送通知.")
            notice_text = "可能已经预定成功, 请登陆12306网站查看."
            return True, notice_text
            # if self.send_booking_ticket_result(notice_text) == False:
            #     logger.info("发送通知失败")
            # else:
            #     logger.info("发送通知成功")
            # return False, False
        
        logger.info("尝试从队列获取订单结果...")
        result_order_for_queue_req = self.result_order_for_queue(orderId)
        if result_order_for_queue_req == False:
            logger.info("从队列获取订单结果失败!")
            return False, False
        
        logger.info("获取订票结果...")
        result_booking_ticket_html_text = self.result_booking_ticket_html()
        booking_ticket_result_dict = self.get_booking_ticket_result_dict(result_booking_ticket_html_text)
        if booking_ticket_result_dict == False:
            logger.info("获取订票结果失败, 但是可能已经成功订票, 准备发送通知.")
            notice_text = "可能已经预定成功, 请登陆12306网站查看."
            return True, notice_text
            # if self.send_booking_ticket_result(notice_text) == False:
            #     logger.info("发送通知失败!")
            # else:
            #     logger.info("发送通知成功!")
        
        # logger.info("准备发送通知...")
        booking_ticket_result_str = self.change_booking_ticket_result_to_string(booking_ticket_result_dict)
        if booking_ticket_result_str == False:
            logger.info("转换订票结果到字符串失败, 尝试发送原始结果.")
            booking_ticket_result_str = str(booking_ticket_result_dict)
            return True, booking_ticket_result_str
            # self.send_booking_ticket_result(booking_ticket_result_str)
        
        # if self.send_booking_ticket_result(booking_ticket_result_str) == False:
        #     logger.info("发送通知失败!")
        # logger.info("发送通知成功!")
        
        return True, booking_ticket_result_str

    def change_booking_ticket_result_to_string(self, booking_ticket_result_dict):
        '''
        返回订票结果字符串, 输入一个结果字典
        :param booking_ticket_result_dict:
        :return:                            成功:订票结果字符串
                                            失败:False
        '''
        result_str = ""
        try:
            result_str += "席位已锁定, 请于30分钟内支付, 超时将取消订单!\n"
            result_str += "订单号码:{0}{1}".format(booking_ticket_result_dict['sequence_no'], "\n")
            result_str += "证件类型:{0}{1}".format(booking_ticket_result_dict['passengerDTO']['passenger_id_type_name'],
                                               "\n")
            result_str += "证件号码:{0}{1}".format(booking_ticket_result_dict['passengerDTO']['passenger_id_no'], "\n")
            result_str += "乘客姓名:{0}{1}".format(booking_ticket_result_dict['passengerDTO']['passenger_name'], "\n")
        
            result_str += "车厢号码:{0}{1}".format(booking_ticket_result_dict['coach_name'], "\n")
            result_str += "座位号码:{0}{1}".format(booking_ticket_result_dict['seat_name'], "\n")
            result_str += "座位类型:{0}{1}".format(booking_ticket_result_dict['seat_type_name'], "\n")
        
            result_str += "出发站点:{0}{1}".format(booking_ticket_result_dict['stationTrainDTO']['from_station_name'], "\n")
            result_str += "到达站点:{0}{1}".format(booking_ticket_result_dict['stationTrainDTO']['to_station_name'], "\n")
            result_str += "列车车次:{0}{1}".format(booking_ticket_result_dict['stationTrainDTO']['station_train_code'],
                                               "\n")
            result_str += "出发日期:{0}{1}".format(booking_ticket_result_dict['start_train_date_page'], "\n")
        
            result_str += "车票价格:{0}{1}{2}".format(booking_ticket_result_dict['str_ticket_price_page'], "元", "\n")
            result_str += "车票号码:{0}{1}".format(booking_ticket_result_dict['ticket_no'], "\n")
            result_str += "车票类型:{0}{1}".format(booking_ticket_result_dict['ticket_type_name'], "\n")
        except:
            logger.info("尝试读取订单返回结果的时候出现了一些故障,以下是输入数据:\n{0}".format(booking_ticket_result_dict))
            if result_str:
                return result_str
            else:
                return False
        if result_str:
            return result_str
        else:
            return False