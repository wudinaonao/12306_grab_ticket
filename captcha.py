'''
    验证码处理模块
    
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
from lxml import etree
import time

class Captcha_class():
    
    def __init__(self, run_session):
        self.run_session = run_session
        
    def get_captcha(self):
        '''
        获取验证码
        :return: 成功返回base64_str, time_value, params_callback, run_session
                 失败返回False, time_value, params_callback, run_session
        '''
        
        def get_checkcode():
            '''
            生成一个21位的随机码用于获取验证码, 以及之后检查验证码的识别字符串
            :return:
            '''
            number_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            rand_num_list = [str(random.choice(number_list)) for i in range(17)]
            rand_num_str = "jQuery1910" + "".join(rand_num_list)
            return rand_num_str
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        # 请求验证码
        url_get_captcha = "https://kyfw.12306.cn/passport/captcha/captcha-image64"
        # 设置时间戳
        time_value = str(int(time.time() * 1000))
        params_callback = get_checkcode() + "_" + time_value
        get_captcha_params = {
            "login_site": "E",
            "module": "login",
            "rand": "sjrand",
            time_value: "",
            "callback": params_callback,
            "_": time_value
        }
        get_captcha = self.run_session.get(url=url_get_captcha, headers=headers, params=get_captcha_params)
        # 把json数据格式的验证码base64_str切割出来处理
        get_captcha_json_str = get_captcha.text[get_captcha.text.find("{"):-2]
        get_captcha_json_data = json.loads(get_captcha_json_str)
        # 检查状态码判断是否生成成功
        if int(get_captcha_json_data['result_code']) != 0:
            logger.info(get_captcha_json_data['result_message'])
            return False, time_value, params_callback, self.run_session
        # 如果存在base64_str则返回, 否则返回False
        if get_captcha_json_data['image'] != "":
            return get_captcha_json_data['image'], time_value, params_callback, self.run_session
        else:
            return False, time_value, params_callback, self.run_session
    
    def mark_captcha(self, base64_str):
        '''
        输入base64字符串标记验证码
        :param base64_str: base64字符串
        :return: 验证码坐标字符串
                 格式:
                 "123,123,123,123"
                 失败返回False
        '''
        # 展示验证码
        # show_captcha(base64_str)
        url_mark = "http://192.168.1.252:5000/mark_captcha/12306/"
        req_data = {"image_base64": base64_str}
        req = requests.post(url=url_mark, data=req_data)
        # {"result": [[86, 50], [163, 88]]}
        json_data = json.loads(req.text)
        # print(req.text)
        if json_data['result'] != []:
            # 展示标记后的验证码
            # show_mark_result(base64_str, json_data['result'])
            result = []
            for coordinate in json_data['result']:
                result.append(str(coordinate[0]))
                result.append(str(coordinate[1]))
            result = ",".join(result)
            return result
        return False
    
    def mark_captcha_v2(self, base64_str):
        '''
            使用一个公共接口标记验证码, 网址:http://60.205.200.159/

        :param base64_str:  验证码base64字符串
        :return:            成功返回: 字符串结果, 格式:"123,123,123,123"
                            失败返回: False
        '''
        headers = {
            # "Host":"check.huochepiao.360.cn",
            "Origin": "http://60.205.200.159",
            "Referer": "http://60.205.200.159/",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
        }
        check_data = {
            "base64": base64_str
        }
        check_url = "http://60.205.200.159/api"
        check_req = requests.post(url=check_url, headers=headers, data=json.dumps(check_data))
        try:
            check_json_data = json.loads(check_req.text)
        except ValueError:
            logger.info("尝试标记验证码的时候发生了一个错误, 原因:返回数据不是Json格式.")
            logger.info("返回信息:{0}".format(check_req.text))
            return False
        if check_json_data['success'] == False:
            logger.info("标记验证码失败.")
            return False
        check_value = check_json_data['check']
        
        mark_url = "http://check.huochepiao.360.cn/img_vcode"
        mark_data = {
            "img_buf": base64_str,
            "type": "D",
            "logon": 1,
            "check": check_value,
            "=": ""
        }
        mark_req = requests.post(url=mark_url, headers=headers, data=json.dumps(mark_data))
        try:
            mark_json_data = json.loads(mark_req.text)
        except ValueError:
            logger.info("尝试标记验证码的时候发生了一个错误, 原因:返回数据不是Json格式.")
            logger.info("返回信息:{0}".format(check_req.text))
            return False
        mark_result = mark_json_data['res'].replace("(", "")
        mark_result = mark_result.replace(")", "")
        if mark_result:
            # # 转换res结果到一个元组列表,格式如:[(123,123)]
            # # 展示标记结果需要转换字符串到列表
            # mark_id_list = []
            # mark_count = len(re.findall("\)", mark_json_data['res']))
            # if mark_count == 1:
            #     mark_str_list = mark_json_data['res'].replace("(", "")
            #     mark_str_list = mark_str_list.replace(")", "")
            #     mark_tuple = mark_str_list.split(",")
            #     X, Y = mark_tuple[0], mark_tuple[1]
            #     mark_id_list.append((int(X), int(Y)))
            # elif mark_count > 1:
            #     mark_str_list = mark_json_data['res'].split("),")
            #     for i in range(len(mark_str_list)):
            #         mark_str_list[i] = mark_str_list[i].replace("(", "")
            #         mark_str_list[i] = mark_str_list[i].replace(")", "")
            #         mark_tuple = mark_str_list[i].split(",")
            #         X, Y = mark_tuple[0], mark_tuple[1]
            #         mark_id_list.append((int(X), int(Y)))
            # # 展示标记结果
            # show_mark_result(base64_str, mark_id_list)
            return mark_result
        else:
            logger.info("标记验证码失败.")
            return False
    
    def chcek_captcha(self, params_callback, captcha_result, time_value):
        '''
        检查验证码
        :param params_callback: params_callback 从get_captcha    返回值获取
        :param captcha_result:  captcha_result  从mark_captcha   返回值获取
        :param time_value:      time_value      从get_captcha    返回值获取
        :return:                成功返回True, self.run_session
                                失败返回False, self.run_session
        '''
        # 设置请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        # 检查验证码
        url_check_captcha = "https://kyfw.12306.cn/passport/captcha/captcha-check"
        check_captcha_params = {
            "callback": params_callback,
            "answer": captcha_result,
            "rand": "sjrand",
            "login_site": "E",
            "_": time_value
        }
        check_captcha = self.run_session.get(url=url_check_captcha, headers=headers, params=check_captcha_params)
        if check_captcha.text.strip() != "":
            check_captcha_result_json = json.loads(check_captcha.text[check_captcha.text.find("{"):-2])
            # 如果结果码不是4 则记录返回信息, 返回False
            if int(check_captcha_result_json['result_code']) != 4:
                logger.info(check_captcha_result_json['result_message'])
                return False, self.run_session
            else:
                return True, self.run_session
        return False, self.run_session