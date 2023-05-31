import cv2  # Thư viên Opencv hỗ trợ xử lý hình ảnh
from pathlib import Path  # Path và argparse lần lượt là thuư viện hỗ trợ xử lý đường dẫn và tham số dòng lệnh
import argparse
import numpy as np
import urllib.request
import time  # Thư viện hỗ trợ tính thời gian thực thi
import os
import matplotlib.pyplot as plt
import serial
import threading
import requests
from src.lp_recognition import E2E  # lớp nhận dạng biển số xe trong file lp.recognition

# from PyQt5.QtCore import Qt

# ser = serial.Serial('COM5', 9600)  # Thay đổi tên cổng COM tùy thuộc vào Arduino của bạn
# url = 'http://192.168.1.5'

# url = 'http://192.168.1.120/cam-lo.jpg'

# Địa chỉ IP của ESP32
ip = '192.168.66.35'

# URL của ảnh stream từ CameraWebServer
url = f'http://{ip}/capture'

# Khởi tạo một cửa sổ mới để hiển thị ảnh stream
cv2.namedWindow('ESP32 Cam Stream', cv2.WINDOW_NORMAL)


def get_arguments():
    arg = argparse.ArgumentParser()  # Khởi tạo đối tượng Ardument Parser
    arg.add_argument('-i', '--image_path', help='link to image', default='./samples/1.jpg')  # các tham số cho đối tượng
    # arg = argparse.ArgumentParser('-i', '--image_path', help='link to image', default='./samples/1.jpg') #thay hàm add_argument bằng cách này sẽ gặp bug. Không trùng tham số với hàm
    return arg.parse_args()  # hàm parse_args()


end = ""
model = E2E()  #
#
# # recognize license plate
# image = model.predict(img)  # check hàm predict
# read image
# img = cv2.imread(str(img_path))  # đọc ảnh từ đường dẫn
count = 0


def save_img(filename, img):
    cv2.imwrite(filename, img)


# def slider_changed(value):
#     ser.write(str(value).encode() + b'\n')


# cap = cv2.VideoCapture(url)
while (1):
    start = time.time()  # lấy thời điểm bắt đầu
    response = requests.get(url)
    img_array = np.array(bytearray(response.content), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    # ret, frame = cap.read()
    # img = urllib.request.urlopen(url)
    # img_np = np.array(bytearray(img.read()), dtype=np.uint8)
    # frame = cv2.imdecode(img_np, -1)
    _,image = model.predict(img)
    cv2.imshow("License Plate", image)

    if cv2.waitKey(0) & 0xFF == ord('q'):
        # frame.release()
        cv2.destroyAllWindows()
        end = time.time()  # lấy thời điểm kết thúc
        print('Model process on %.2f s' % (end - start))
        break
    elif chr(cv2.waitKey(1) & 255) == 's':
        end = time.time()
        if not os.path.exists("samples"):
            os.makedirs("samples")
            print("Loi thu muc chua ton tai")
        filename = "samples/image_" + str(end) + str(count) + ".jpg"
        # count += 1
        print("Luu anh: ", filename)
        save_img(filename, frame)
        plt.imshow(frame)
        plt.show()
    elif chr(cv2.waitKey(1) & 255) == 'a':
        args = get_arguments()  # trả về đối tượng ảnh
        img_path = Path(args.image_path)  # lấy đường dẫn ảnh từ tham số args. imagepath
        # read image
        img = cv2.imread(str(img_path))  # đọc ảnh từ đường dẫn
        image = model.predict(img)  # check hàm predict
        cv2.imshow("img", image)

        # slider = QSlider(Qt.Horizontal)
        # slider.setMinimum(0)
        # slider.setMaximum(180)
        # slider.valueChanged.connect(slider_changed)
    elif chr(cv2.waitKey(1) & 255) == 'c':
        # ser.write(b'90\n')  # Gửi gói tin để xoay servo ở góc 90 độ
        print("Da xoay")
    #print("vong lap")




# # start
# start = time.time() # lấy thời điểm bắt đầu
#
# # load model
# model = E2E() #
#
# # recognize license plate
# image = model.predict(img)  # check hàm predict
#
# # end
# end = time.time()# lấy thời điểm kết thúc
#

#
# # show image
# cv2.imshow('License Plate', image) # Bao gồm tên cửa sổ và ảnh
# if cv2.waitKey(0) & 0xFF == ord('q'):
#     exit(0)
#
#
# cv2.destroyAllWindows()
