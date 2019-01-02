import cv2
from io import BytesIO
import base64
import numpy as np

ID = [
    [(5, 12), (72, 79)],
    [(5, 84), (72, 151)],
    [(77, 12), (142, 79)],
    [(77, 84), (142, 151)],
    [(147, 12), (214, 79)],
    [(147, 84), (214, 151)],
    [(221, 12), (286, 79)],
    [(221, 84), (286, 151)]
]

def show_captcha(base64_str):
    '''
    输入base64字符串显示图像
    :param base64_str: base64字符串
    '''
    base64_str = base64.b64decode(base64_str)
    image = BytesIO(base64_str)
    image_array = np.asarray(bytearray(image.getvalue()), dtype="uint8")
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    cv2.imshow("Mark result", img)
    cv2.waitKey(5000)

def show_mark_result(base64_str, result_list):
    '''
    显示验证码标记结果
    :param base64_str:  验证码base64字符串
    :param result_list: 输入格式 [[123,123], [456,456]]
    :return:
    '''
    
    def get_center_point(A, B):
        '''
        获取中心点, A和B分别为图像左上角和右下角左边
        :param A: 左上角坐标
        :param B: 右下角坐标
        :return: 中心点坐标
        '''
        x = int((B[0] - A[0]) // 2 + A[0])
        y = int((B[1] - A[1]) // 2 + A[1])
        return (x, y)
    
    def sum_id(x, y):
        '''
        从坐标反推图像id号
        :param x:
        :param y:
        :return:
        '''
        if 5<=x<=72 and 12<=y<=79:
            return 0
        elif 5<=x<=72 and 84<=y<=151:
            return 1
        elif 77<=x<=142 and 12<=y<=79:
            return 2
        elif 77<=x<=142 and 84<=y<=151:
            return 3
        elif 147<=x<=214 and 12<=y<=79:
            return 4
        elif 147<=x<=214 and 84<=y<=151:
            return 5
        elif 221<=x<=286 and 12<=y<=79:
            return 6
        elif 221<=x<=286 and 84<=y<=151:
            return 7
        else:
            return None

    id_list = []
    for result in result_list:
        id = sum_id(result[0], result[1])
        if id is not None:
            id_list.append(id)
        # else:
        #     raise Exception("返回的标记坐标可能是错误的")
    if not id_list:
        print("id_list 为空")
        return None
    
    base64_str = base64.b64decode(base64_str)
    image = BytesIO(base64_str)
    image_array = np.asarray(bytearray(image.getvalue()), dtype="uint8")
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    mark_bgr_color = (71, 99, 255)  # 颜色顺序是BGR 不是 RGB
    for id in id_list:
        # 画矩形
        # cv2.rectangle(img, ID[id][0], ID[id][1], mark_bgr_color, 2)
        
        # 画圆圈
        # cv2.circle(img, get_center_point(ID[id][0], ID[id][1]), 8, mark_bgr_color, 8)
        
        # 画对勾
        center_point = get_center_point(ID[id][0], ID[id][1])  # 图像中心点
        tick_midpoint = (  # 对勾中心点
            center_point[0] + 2,
            center_point[1] + 5
        )
        a = (center_point[0] - 5, center_point[1] - 5)  # 对勾左上角坐标
        b = (center_point[0] + 10, center_point[1] - 10)  # 对勾右上角坐标
        cv2.line(img, a, tick_midpoint, mark_bgr_color, 5)
        cv2.line(img, tick_midpoint, b, mark_bgr_color, 5)
    cv2.imshow("Mark result", img)
    cv2.waitKey(3000)
    # return img

