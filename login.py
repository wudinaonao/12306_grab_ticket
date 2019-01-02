'''
    登陆模块
    
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
from captcha import Captcha_class

class Login_class():
    
    def __init__(self, run_session, username, password):
        self.run_session = run_session
        self.username = username
        self.password = password
        self.captcha_class = Captcha_class(run_session)
        self.login_tf = ""
        
    def login(self, captcha_result):
        '''
        登陆
        :param captcha_result: captcha_result    从mark_captcha 获得
        :return:                                 如果密码错误则返回"密码错误"
                                                 因为密码错误4次会锁定用户, 所以如果出现密码错误的提示会终止程序

                                                 暂时不知道登陆失败是什么提示, 所以只会返回True 除非密码错误
        '''
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        url_login = "https://kyfw.12306.cn/passport/web/login"
        login_data = {
            "username": self.username,
            "password": self.password,
            "appid": "otn",
            "answer": captcha_result
        }
        # 这几个请求我也不知道干了什么
        req_1 = self.run_session.post(url=url_login, headers=headers, data=login_data)
        try:
            req_1_json_data = json.loads(req_1.text)
            if req_1_json_data['result_code'] == 1:
                logger.info("返回信息:{0}".format(req_1_json_data['result_message']))
                return "密码错误"
        except:
            pass
        url_user_login = "https://kyfw.12306.cn/otn/login/userLogin"
        self.run_session.get(url=url_user_login, headers=headers)
        return True
    
    def get_login_tk(self):
        '''
        获取login_tk
        :return:           成功返回login_tk
                           失败返回False
        '''
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        # 获取一个登陆tk
        url_uamtk = "https://kyfw.12306.cn/passport/web/auth/uamtk"
        req_4 = self.run_session.post(url=url_uamtk, headers=headers, data={"appid": "otn"})
        req_4_json_data = json.loads(req_4.text)
        if req_4_json_data['result_code'] != 0:
            logger.info("返回信息:{0}".format(req_4_json_data['result_message']))
            return False
        return req_4_json_data['newapptk']
    
    def check_login_tk(self):
        '''
        验证登陆tk
        :return:    成功返回用户名
                    失败返回False
        '''
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        # 提交tk获取登陆结果
        url_uamauthclient = "https://kyfw.12306.cn/otn/uamauthclient"
        req_5 = self.run_session.post(url=url_uamauthclient, headers=headers, data={"tk": self.login_tf})
        req_5_json_data = json.loads(req_5.text)
        if req_5_json_data['result_code'] != 0:
            logger.info("返回信息:{0}".format(req_5_json_data['result_message']))
            return False
        return req_5_json_data['username']
    
    def login_method(self):
        '''
        登陆方法
        :return:    成功 True, self.run_session
                    失败 False, self.run_session
        '''
        
        # 获取验证码, 时间戳
        logger.info("获取验证码...")
        captcha_base64_str, time_value, params_callback, self.run_session = self.captcha_class.get_captcha()
        if captcha_base64_str == False:
            return False, self.run_session
        
        # 标记验证码
        logger.info("识别验证码...")
        captcha_result = self.captcha_class.mark_captcha_v2(captcha_base64_str)
        if captcha_result == False:
            logger.info("验证码识别失败!")
            return False, self.run_session
        
        # 检查验证码
        logger.info("检查验证码...")
        check_captcha_status, self.run_session = self.captcha_class.chcek_captcha(params_callback=params_callback,
                                                                                  captcha_result=captcha_result,
                                                                                  time_value=time_value)
        if check_captcha_status == False:
            logger.info("验证码验证失败!")
            return False, self.run_session
        
        # 模拟登陆
        logger.info("正在登陆...")
        if self.login(captcha_result=captcha_result) == "密码错误":
            logger.info("密码错误!")
            return False, self.run_session
        
        logger.info("获取登陆tk...")
        self.login_tf = self.get_login_tk()
        if self.login_tf == False:
            logger.info("获取登陆tk失败!")
            return False, self.run_session
        
        logger.info("验证登陆tk...")
        user_name = self.check_login_tk()
        if user_name == False:
            logger.info("验证登陆tk失败!")
            return False, self.run_session
        logger.info("登陆成功!    用户名:{0}".format(user_name))
        
        return True, self.run_session
    
    @classmethod
    def check_user(self, run_session):
        '''
        检查用户登陆状态
        :return:        成功True
                        失败False
        '''
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            "Content-Type": "application/json;charset=UTF-8"
        }
        check_user_url = "https://kyfw.12306.cn/otn/login/checkUser"
        check_user_data = {
            "_json_att": ""
        }
        check_user_req = run_session.post(url=check_user_url, headers=headers, data=check_user_data)
        try:
            check_user_json_data = json.loads(check_user_req.text)
        except ValueError:
            logger.info("在检查用户登录状态的时候发生错误, 原因:返回的信息不是Json格式.")
            logger.info("返回信息:{0}".format(check_user_req.text))
            return False
        if check_user_json_data['status'] == False:
            logger.info("在检查用户登录状态的时候发生错误, 原因:请求失败.")
            logger.info("返回信息:{0}".format(check_user_json_data['messages']))
            return False
        if check_user_json_data['data']['flag'] == False:
            logger.info("用户未登录.")
            return False
        return True