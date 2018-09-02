import random
import time
import base64
import hmac
import hashlib
import sys
import requests
import json
import urllib
import cv2
from pylab import mpl
from pylab import plt
from io import BytesIO
import PIL.Image as Image

mpl.rcParams['font.sans-serif'] = ['SimHei']

# 腾讯云文档链接
# 鉴权签名：          https://cloud.tencent.com/document/product/867/17719
# 人脸静态活体检测：   https://cloud.tencent.com/document/product/867/17587

# 随机整数串生成函数
def getrandom(length):
    nonce = ''
    for i in range(length):
        number = random.randint(1, 9)
        nonce = nonce+str(number)
    return int(nonce)


# HMAC-SHA1加密函数
def encrypt(signature1, secretkey):
    signature = bytes(signature1, encoding='utf-8')
    secretkey = bytes(secretkey, encoding='utf-8')
    # 这里python跟其他语言的写法不太一样。密钥在第一位，第二位才是要加密的。而且是bytes类型加密
    my_sign = hmac.new(secretkey,signature, hashlib.sha1).digest()
    return my_sign


# 鉴权签名生成函数
#  签名公式：
#  SignTmp = HMAC-SHA1(SecretKey, orignal)
#  Sign = Base64(SignTmp.orignal)
def sign_generate(appid, secret_id, secret_key):
    current = int(time.time())  # 时间戳
    expired = current + 2592000
    rdm = getrandom(4)  # 随机数
    original = "a=" + appid + "&k=" + secret_id + "&e=" + str(expired) \
               + "&t=" + str(current) + "&r=" + str(rdm)
    signtmp = encrypt(original, secret_key)  # HMAC-SHA1加密 输出类型为bytes
    original = bytes(original, encoding='utf-8')
    sign = signtmp + original
    sign = base64.b64encode(sign)
    return sign


# 使用requests发送POST请求，请求内容url
def send_request_byurl(sign, image_url):
    header = {
        "host": "recognition.image.myqcloud.com",
        "content-type": "application/json",
        "authorization": sign,
    }
    param = {
        "appid": "1257383199",
        "url": image_url,
    }
    res = requests.post(url, headers=header, data=json.dumps(param))
    # 打印
    # print('\n-----------------request header-----------------\n',
    #       res.request.headers,
    #       '\n-----------------request header-----------------\n')
    # print('\n-----------------request body-----------------\n',
    #       res.request.body,
    #       '\n-----------------request body-----------------\n')
    # print('\n-----------------request response-----------------\n',
    #       res.text,
    #       '\n-----------------request response-----------------\n')
    return res.text


# 使用requests发送POST请求，请求内容image
def send_request_byimage(sign, imagefile):
    # header
    header = {
        "host": "recognition.image.myqcloud.com",
        "content-type": "multipart/form-data;boundary=--------------acebdf13572468",
        "authorization": sign,
    }
    # data
    with open(imagefile, 'rb') as f:
        img = f.read()
        image_to_show = Image.open(BytesIO(img)).resize((300, 400))
    data = list()
    data.append(bytes(boundary, "utf-8"))
    data.append(bytes('Content-Disposition: form-data; name="%s";\r\n' % 'appid', "utf-8"))
    data.append(bytes(appid, "utf-8"))
    data.append(bytes(boundary, "utf-8"))
    data.append(bytes('Content-Disposition: form-data; name="%s"; filename="face.jpg"' % 'image', "utf-8"))
    data.append(bytes('Content-Type: %s\r\n' % 'image/jpeg', "utf-8"))
    data.append(bytes(img))
    data.append(bytes('----------------acebdf13572468', 'utf-8'))
    http_body = b'\r\n'.join(data)
    res = requests.post(url, headers=header, data=http_body)
    return res.text, image_to_show

if __name__ == "__main__":
    appid = "your appid"
    secret_id = "your secret_id"
    secret_key = "your secret_key"
    userid = "0"
    boundary = '----------------acebdf13572468'
    url = "https://recognition.image.myqcloud.com/face/livedetectpicture"
    sign = sign_generate(appid, secret_id, secret_key)
    # 网络图片url
    # 新垣结衣网图-无翻拍
    url_1 = "http://imgwx2.2345.com/dianyingimg/star/img/8/0/773/photo_192x262.jpg"
    # 新垣结衣网图-翻拍
    url_2 = "https://b-ssl.duitang.com/uploads/item/201604/06/20160406110323_hJjXM.jpeg"
    # 新垣结衣网图-无翻拍
    url_3 = "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1535649711077&di=cba091b8f3698c798efaa72e4d739950&imgtype=0&src=http%3A%2F%2Fimage13.m1905.cn%2Fuploadfile%2F2012%2F0503%2F20120503050545633.jpg"
    # 新垣结衣网图-无翻拍-黑白
    url_4 = "http://news.youth.cn/yl/201801/W020180110550542371207.jpg"
    text_1 = send_request_byurl(sign, url_1)
    print(text_1)
    text_2 = send_request_byurl(sign, url_2)
    print(text_2)
    text_3 = send_request_byurl(sign, url_3)
    print(text_3)
    text_4 = send_request_byurl(sign, url_4)
    print(text_4)
    # 打印keys和score
    # print(json.loads(text_4).keys())
    # print(json.loads(text_4)["data"]["score"])

    score_1 = str(json.loads(text_1)["data"]["score"])
    score_2 = str(json.loads(text_2)["data"]["score"])
    score_3 = str(json.loads(text_3)["data"]["score"])
    score_4 = str(json.loads(text_4)["data"]["score"])

    html_1 = requests.get(url_1)
    html_2 = requests.get(url_2)
    html_3 = requests.get(url_3)
    html_4 = requests.get(url_4)
    # 保存图片
    # with open('picture.jpg', 'wb') as file:
    #     file.write(html.content)

    image_1 = Image.open(BytesIO(html_1.content)).resize((300, 400))
    image_2 = Image.open(BytesIO(html_2.content)).resize((300, 400))
    image_3 = Image.open(BytesIO(html_3.content)).resize((300, 400))
    image_4 = Image.open(BytesIO(html_4.content)).resize((300, 400))

    imagefile_1 = 'img/1.jpg'
    imagefile_2 = 'img/2.jpg'
    imagefile_3 = 'img/3.jpg'
    imagefile_4 = 'img/4.jpg'

    text_5, image_5 = send_request_byimage(sign, imagefile_1)
    print(text_5)
    text_6, image_6 = send_request_byimage(sign, imagefile_2)
    print(text_6)
    text_7, image_7 = send_request_byimage(sign, imagefile_3)
    print(text_7)
    text_8, image_8 = send_request_byimage(sign, imagefile_4)
    print(text_8)
    score_5 = str(json.loads(text_5)["data"]["score"])
    score_6 = str(json.loads(text_6)["data"]["score"])
    score_7 = str(json.loads(text_7)["data"]["score"])
    score_8 = str(json.loads(text_8)["data"]["score"])

    # print(res.request.body)
    # print(res.request.headers)
    # print(res.text)

    plt.subplot(241).set_title("无翻拍 : %s 分" % score_1)
    plt.imshow(image_1)
    plt.axis('off')
    plt.subplot(242).set_title("翻拍 : %s 分" % score_2)
    plt.imshow(image_2)
    plt.axis('off')
    plt.subplot(243).set_title("无翻拍 : %s 分" % score_3)
    plt.imshow(image_3)
    plt.axis('off')
    plt.subplot(244).set_title("无翻拍-黑白 : %s 分" % score_4)
    plt.imshow(image_4)
    plt.axis('off')

    plt.subplot(245).set_title("电脑拍摄 : %s 分" % score_5)
    plt.imshow(image_5)
    plt.axis('off')
    plt.subplot(246).set_title("手机拍摄 : %s 分" % score_6)
    plt.imshow(image_6)
    plt.axis('off')
    plt.subplot(247).set_title("电脑拍摄-翻拍 : %s 分" % score_7)
    plt.imshow(image_7)
    plt.axis('off')
    plt.subplot(248).set_title("手机拍摄-翻拍 : %s 分" % score_8)
    plt.imshow(image_8)
    plt.axis('off')

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
    plt.axis('off')
    plt.suptitle("腾讯-活体检测")
    plt.show()
