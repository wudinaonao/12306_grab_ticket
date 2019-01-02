# 12306抢票程序
Python3.x实现.<br>
在config.py文件里配置需要使用的信息.

## 关于验证码识别的问题
### 12306的验证码分为两部分:
1. 文字部分
2. 图片部分

我们需要先识别出文字信息然后再识别图像信息, 
笔者这里使用了2个CNN网络来识别验证码, 一个用于
文字部分, 一个用于图像部分.
    
笔者在识别文字部分的时候开始想到的是CNN+LSTM+CTC
实现不定长文本识别, 但是经过笔者测试这种方法的识别准
确率大概在0.93, 因为笔者的数据集并不大, 所以用这个识
别的准确率并不高.
    
笔者之后发现12306验证码的文字部分为80个分类, 这样
我们似乎可以直接使用CNN来识别, 经过笔者测试,效果出乎意
料的不错, 准确率基本在1.0
    
<img src="https://github.com/wudinaonao/12306_grab_ticket/blob/master/use/captcha_text.png">

图片部分的识别因为笔者数据集并不大, 所以准确率大约在0.9附近, 不过这个准确率已经够用了, 关于图像分类的部分这里不赘述.

## 验证码识别
<img src="https://github.com/wudinaonao/12306_grab_ticket/blob/master/use/mark_captcha.png?raw=true">

## 程序运行流程
1. 从配置文件读取信息
2. 登陆
3. 查询符合条件的列车信息
4. 订票
5. 预定成功发送邮件通知

## 程序运行效果

<img src="https://github.com/wudinaonao/12306_grab_ticket/blob/master/use/run.png?raw=true">
<img src="https://github.com/wudinaonao/12306_grab_ticket/blob/master/use/result.png?raw=true">
