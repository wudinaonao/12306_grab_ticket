'''
抢票基本信息设置

    1. 12306网站用户名
    2. 12306网站密码
    3. 出发日期(train_date)
    4. 列车号  例如:D1234
    5. 出发站
    6. 终到站
    7. 乘客姓名
    8. 乘客证件类型
    9. 乘客证件号码
    10.座位类型
    11.期望的位置
    
    PS: 票类型默认为成人票
    
'''
USERNAME_12306      = ""                            # 12306登陆用户名
PASSWORD_12306      = ""                            # 12306登陆密码
TRAIN_DATE          = "2019-01-28"                  # 乘车日期
BOOKING_AFTER_TIME  = "08:00"                       # 订票的时间区间上界
BOOKING_BEFORE_TIME = "22:00"                       # 订票的时间区间下界
TRAIN_NAME          = ""                            # 如果为空值则取符合条件时间最早的一班
FROM_STATION        = "北京"                        # 出发站
TO_STATION          = "天津"                        # 终到站
PASSENGER_NAME      = ""                            # 乘客姓名
DOCUMENT_TYPE       = "1"                           # 证件类型号, 身份证是1
DOCUMENT_NUMBER     = ""                            # 证件号
MOBILE              = ""                            # 手机号
SEAT_TYPE           = "二等座"                      # 座位类型
EXPECT_SETA_NUM     = "A"                           # 期望的位置A,B,C,E,F A和F靠窗, 这个不一定会有位置, 如果没有系统随机分配

'''
通知方式配置
    
    1. 邮件通知
    2. 等待增加...
    
'''
SMTP_SERVER_HOST = "smtp.gmail.com"                 #发件smtp服务器
SMTP_SERVER_PORT = 465                              #端口号
EMAIL_USERNAME   = ""                               #登陆用户名
EMAIL_PASSWORD   = ""                               #登陆密码
SENDER           = ""                               #发件箱
RECEVIER_LIST    = [""]                             #收件人, 是一个列表, 可以包含多个收件人



'''
日志记录文件
'''
# 日志保存路径
LOG_FILE = "run.log"