import tkinter as tk
from PIL import Image, ImageTk
import requests
import io
import numpy as np
import cv2
import time
import serial
from src.lp_recognition import E2E
from flask import Flask, request

model = E2E()
IP = '192.168.1.12'  # Replace with the IP address of your ESP32-CAM
URL = f'http://{IP}/capture'
DELAY = 1000  # Milliseconds to wait between updating the image
WIDTH, HEIGHT = 640, 480  # Width and height of the image

app = Flask(__name__)

class App:
    def __init__(self, window):
        self.window = window
        self.window.title('ESP32-CAM Image Stream')
        self.canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT)
        self.canvas.pack()
        self.img = None
        self.after_id = None
        self.running = False
        self.btn_start = tk.Button(window, text='Start', command=self.start)
        self.btn_start.pack(side=tk.LEFT, padx=10, pady=10)
        self.btn_stop = tk.Button(window, text='Stop', command=self.stop)
        self.btn_stop.pack(side=tk.LEFT, padx=10, pady=10)
        self.btn_capture = tk.Button(window, text='Capture', command=self.capture)
        self.btn_capture.pack(side=tk.LEFT, padx=10, pady=10)
        self.ip_var = tk.StringVar(value=IP)
        self.combo_ip = tk.OptionMenu(window, self.ip_var, IP, *['192.168.224.35', '192.168.1.20', '192.168.1.30'])
        self.combo_ip.pack(side=tk.LEFT, padx=10, pady=10)
        self.lbl_result = tk.Label(window, text='Not found')
        self.lbl_result.pack(side=tk.LEFT, padx=10, pady=10)

    def start(self):
        self.running = True
        self.update_image()

    def stop(self):
        self.running = False
        if self.after_id is not None:
            self.window.after_cancel(self.after_id)
            self.after_id = None

    def capture(self):
            text_plate = self.lbl_result_plate.cget('text')
            text_uuid = self.lbl_result_uuid.cget('text')

            print('Da lay duoc text:', text_plate)
            print('UUID:', text_uuid)
            # ser.write(b'90\n')  # Gửi gói tin để xoay servo ở góc 90 độ
            print("Da xoay")
            url_api = 'http://127.0.0.1:8000/cars/'
            data = {'license_plate': text_plate, 'uuid': text_uuid, 'car_model': 'Car', 'car_color': 'red'}

            response = requests.post(url_api, data=data)
            print(response.status_code)
            print(response.json())
    def update_image():
        if not app.running:
            return
        try:
            # Get the image from the URL
            response = requests.get(URL)
            img_array = np.array(bytearray(response.content), dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            img = model.predict(img)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img)

            # Resize the image to fit the canvas
            pil_img = pil_img.resize((WIDTH, HEIGHT))

            # Convert the PIL image to a Tkinter PhotoImage
            app.img = ImageTk.PhotoImage(pil_img)

            # Draw the image on the canvas
            app.canvas.create_image(0, 0, image=app.img, anchor=tk.NW)

            # Schedule the next update
            app.after_id = app.window.after(DELAY, update_image)
        except Exception as e:
            app.lbl_result_plate.config(text=f'Error: {str(e)}')
            app.lbl_result_uuid.config(text='')
            app.stop()
@app.route('/post-uuid', methods=['POST'])
def post_uuid():
    plate = request.form.get('license_plate')
    uuid = request.form.get('uuid')
    app.lbl_result_plate.config(text=plate)
    app.lbl_result_uuid.config(text=uuid)
    return 'OK'



if __name__ == '__main__':
    window = tk.Tk()
    app = App(window)

    # Tạo nhãn hiển thị biển số xe
    app.lbl_result_plate = tk.Label(window, text='Not found')
    app.lbl_result_plate.pack(side=tk.LEFT, padx=10, pady=10)

    # Tạo nhãn hiển thị UUID điều khiển
    app.lbl_result_uuid = tk.Label(window, text='')
    app.lbl_result_uuid.pack(side=tk.LEFT, padx=10, pady=10)

    window.after(0, update_image)  # Bắt đầu cập nhật hình ảnh ngay khi ứng dụng chạy
    window.mainloop()
