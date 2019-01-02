import smtplib
from email.mime.text import MIMEText
from email.header import Header
import config

def send_email(subject, text):
    '''
    发送邮件, 发件设置从config读取
    :param subject: 标题
    :param text: 文本
    :return: 成功True 失败False
    '''
    mail_host = config.SMTP_SERVER_HOST
    mail_port = int(config.SMTP_SERVER_PORT)
    mail_user = config.EMAIL_USERNAME
    mail_pass = config.EMAIL_PASSWORD

    sender = config.SENDER
    receivers = config.RECEVIER_LIST  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    
    # plain 表示发送文本格式
    message = MIMEText(text, 'plain', 'utf-8')
    message['From'] = Header(",".join(receivers), 'utf-8')
    message['To'] = Header(subject, 'utf-8')
    
    # 邮件标题
    message['Subject'] = Header(subject, 'utf-8')
    
    try:
        smtpObj = smtplib.SMTP_SSL(mail_host)
        smtpObj.connect(mail_host, mail_port)  # 25 为 SMTP 端口号
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        return True
    except smtplib.SMTPException:
        return False

def send_email_test():
    '''
    发送邮件, 发件设置从config读取
    :param subject: 标题
    :param text: 文本
    :return: 成功True 失败False
    '''
    mail_host = config.SMTP_SERVER_HOST
    mail_port = int(config.SMTP_SERVER_PORT)
    mail_user = config.EMAIL_USERNAME
    mail_pass = config.EMAIL_PASSWORD
    
    subject = "12306抢票通知测试"
    text = "==================================================\n" + \
           "|    12306抢票通知测试                           |\n" + \
           "|    测试方式:邮件                               |\n" + \
           "|    如果收到这个邮件说明可以收到抢票结果通知    |\n" + \
           "==================================================\n"
    
    sender = config.SENDER
    receivers = config.RECEVIER_LIST  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    
    # plain 表示发送文本格式
    message = MIMEText(text, 'plain', 'utf-8')
    message['From'] = Header(",".join(receivers), 'utf-8')
    message['To'] = Header(subject, 'utf-8')
    
    # 邮件标题
    message['Subject'] = Header(subject, 'utf-8')
    
    try:
        smtpObj = smtplib.SMTP_SSL(mail_host)
        smtpObj.connect(mail_host, mail_port)  # 25 为 SMTP 端口号
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        return True
    except smtplib.SMTPException:
        return False
if __name__=="__main__":
    print(send_email_test())