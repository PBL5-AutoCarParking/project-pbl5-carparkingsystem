import tkinter as tk
from PIL import Image, ImageTk
import cv2
from flask import Flask, request
from src.lp_recognition import E2E
import threading
import requests
import numpy as np
import io

model = E2E()
IP = '192.168.66.35'  # Replace with the IP address of your ESP32-CAM
URL = f'http://{IP}/capture'
DELAY = 1000  # Milliseconds to wait between updating the image
WIDTH, HEIGHT = 640, 480  # Width and height of the image
CAPTURE_WIDTH, CAPTURE_HEIGHT = 320, 240  # Width and height of the capture image


app = Flask(__name__)
window = tk.Tk()

class App:
    def __init__(self, window):
        self.window = window
        self.window.title('Camera Image Stream')

        self.frame_left = tk.Frame(window)
        self.frame_left.grid(row=0, column=0, padx=10, pady=10)

        self.canvas = tk.Canvas(self.frame_left, width=WIDTH, height=HEIGHT)
        self.canvas.pack()

        self.frame_right = tk.Frame(window)
        self.frame_right.grid(row=0, column=1, padx=10, pady=10)

        self.capture_frame = tk.Frame(self.frame_right, width=CAPTURE_WIDTH, height=CAPTURE_HEIGHT)
        self.capture_frame.pack(padx=10, pady=10)

        self.capture_image = tk.Label(self.capture_frame)
        self.capture_image.pack()

        self.btn_start = tk.Button(self.frame_right, text='Start', command=self.start)
        self.btn_start.pack(side=tk.TOP, padx=10, pady=10)

        self.btn_stop = tk.Button(self.frame_right, text='Stop', command=self.stop)
        self.btn_stop.pack(side=tk.TOP, padx=10, pady=10)

        self.lbl_result_lp = tk.Label(self.frame_right, text='License Plate: Not found')
        self.lbl_result_lp.pack(side=tk.TOP, padx=10, pady=10)

        self.lbl_result_uuid = tk.Label(self.frame_right, text='UUID: Not found')
        self.lbl_result_uuid.pack(side=tk.TOP, padx=10, pady=10)

        self.after_id = None

        self.can_capture = True  # Đánh dấu rằng có thể chụp ảnh
        self.previous_capture_image = None  # Lưu trữ hình ảnh chụp trước đó

    def start(self):
        self.running = True
        self.update_image()
        # threading.Thread(target=self.update_image).start()

    def stop(self):
        self.running = False
        if self.after_id is not None:
            self.window.after_cancel(self.after_id)
            self.after_id = None

    def capture(self):
        if self.can_capture:
            self.can_capture = False  # Vô hiệu hóa thao tác chụp ảnh trong khoảng thời gian delay
            text_lp = self.lbl_result_lp.cget('text')
            print('License Plate:', text_lp)
            url_api = 'http://127.0.0.1:8000/cars/'
            data = {
                'license_plate': text_lp,
                'uuid': self.lbl_result_uuid.cget('text')[6:],
                'car_model': 'Car',
                'car_color': 'red'
            }
            response = requests.post(url_api, data=data)
            print(response.status_code)
            print(response.json())
            self.window.after(3000, self.enable_capture)  # Cho phép chụp ảnh sau 3 giây

    def enable_capture(self):
        self.can_capture = True

    def update_image(self):
        if not self.running:
            return
        try:
            response = requests.get(URL)
            if response.status_code == 200:
                img_bytes = io.BytesIO(response.content)
                img = Image.open(img_bytes)
                img = img.resize((WIDTH, HEIGHT))
                img_np = np.array(img)
                img = Image.fromarray(cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY))
                self.img = ImageTk.PhotoImage(img)
                self.canvas.create_image(0, 0, image=self.img, anchor=tk.NW)

                cropped_img, img = model.predict(img_np)
                license_plate = model.format()

                if license_plate != "":
                    if license_plate != self.lbl_result_lp.cget('text')[15:]:
                        self.lbl_result_lp.config(text='License Plate: ' + license_plate)
                        capture_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
                        capture_img = cv2.resize(capture_img, (CAPTURE_WIDTH, CAPTURE_HEIGHT))
                        pil_capture_img = Image.fromarray(capture_img)
                        pil_capture_img = ImageTk.PhotoImage(pil_capture_img)
                        self.capture_image.config(image=pil_capture_img)
                        self.capture_image.image = pil_capture_img
                        # self.capture()      # Gọi phương thức chụp ảnh khi có sự nhận diện biển số
                else:
                    self.lbl_result_lp.config(text='License Plate: Not found')
                    if self.previous_capture_image is not None:
                        # Sử dụng hình ảnh chụp trước đó nếu không có biển số được nhận dạng
                        pil_capture_img = Image.fromarray(self.previous_capture_image)
                        pil_capture_img = ImageTk.PhotoImage(pil_capture_img)
                        self.capture_image.config(image=pil_capture_img)
                        self.capture_image.image = pil_capture_img
            else:
                print("Khong ket noi voi cam duoc")

        except Exception as e:
            self.lbl_result_lp.config(text=f'Error: {str(e)}')
            print("An error occurred:", e)

        finally:
            self.window.after(DELAY, self.update_image)


@app.route('/process_post', methods=['POST'])
def receive_uuid():
    uuid = request.form.get('uuid')
    app_window.lbl_result_uuid.config(text='UUID: ' + uuid)
    return 'UUID received'


@app.route('/')
def index():
    return 'Hello, World!'


if __name__ == '__main__':
    app_window = App(window)
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 8000}).start()
    window.mainloop()
