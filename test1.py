import cv2
import os
import requests
import numpy as np
from src.lp_recognition import E2E
import serial
import time
# Địa chỉ IP của ESP32
ip = '192.168.224.35'

# URL của ảnh stream từ CameraWebServer
url = f'http://{ip}/capture'


def save_img(filename, img):
    cv2.imwrite(filename, img)

# Khởi tạo một cửa sổ mới để hiển thị ảnh stream
cv2.namedWindow('ESP32 Cam Stream', cv2.WINDOW_NORMAL)
model = E2E()  #
while True:
    # Thực hiện yêu cầu HTTP GET từ ESP32 và lưu lại dữ liệu nhận được dưới dạng ảnh
    response = requests.get(url)
    img_array = np.array(bytearray(response.content), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    image = model.predict(img)
    # Hiển thị ảnh trong cửa sổ
    cv2.imshow('ESP32 Cam Stream', image)

    # Đợi 1 phím bất kỳ được nhấn để thoát chương trình
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # if cv2.waitKey(1) & 0xFF == ord('s'):
    #     end = time.time()
    #     if not os.path.exists("samples"):
    #         os.makedirs("samples")
    #         print("Loi thu muc chua ton tai")
    #     filename = "samples/image_" + str(end) + ".jpg"
    #     # count += 1
    #     print("Luu anh: ", filename)
    #     save_img(filename, image)


# Giải phóng tài nguyên và đóng các cửa sổ hiển thị
cv2.destroyAllWindows()
