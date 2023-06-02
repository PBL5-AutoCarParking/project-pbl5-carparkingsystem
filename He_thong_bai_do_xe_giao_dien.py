import tkinter as tk
from PIL import Image, ImageTk
import cv2
from flask import Flask, request
import threading
import requests
import numpy as np
import io
from src.lp_recognition import E2E
from tkinter import messagebox

cap = cv2.VideoCapture(0)

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

        # Dòng label giữa hai phần trên bên trái và phải
        self.lbl_divider = tk.Label(window, text='-------------')
        self.lbl_divider.grid(row=0, column=2, columnspan=2, padx=10, pady=10)

        self.esp32_error_message = tk.StringVar()
        self.video_capture_error_message = tk.StringVar()

# Phần trên bên trái (Camera từ URL)
        self.frame_top_left = tk.Frame(window)
        self.frame_top_left.grid(row=0, column=0, padx=10, pady=10)

        self.canvas_top_left = tk.Canvas(self.frame_top_left, width=WIDTH, height=HEIGHT)
        self.canvas_top_left.pack()

        self.capture_frame_top_left = tk.Frame(self.frame_top_left, width=CAPTURE_WIDTH, height=CAPTURE_HEIGHT)
        self.capture_frame_top_left.pack(padx=10, pady=10)

        self.capture_image_top_left = tk.Label(self.capture_frame_top_left)
        self.capture_image_top_left.pack()
        self.capture_frame_top_left.pack_propagate(0) # overflowing and covering the buttons

        self.btn_start_top_left = tk.Button(self.frame_top_left, text='Start', command=self.start_top_left)
        self.btn_start_top_left.pack(side=tk.TOP, padx=10, pady=10)

        self.btn_stop_top_left = tk.Button(self.frame_top_left, text='Stop', command=self.stop_top_left)
        self.btn_stop_top_left.pack(side=tk.TOP, padx=10, pady=10)

        self.lbl_result_lp_top_left = tk.Label(self.frame_top_left, text='License Plate: Not found')
        self.lbl_result_lp_top_left.pack(side=tk.TOP, padx=10, pady=10)

        self.lbl_result_uuid_top_left = tk.Label(self.frame_top_left, text='UUID: Not found')
        self.lbl_result_uuid_top_left.pack(side=tk.TOP, padx=10, pady=10)

        # Phần trên bên phải (Camera từ máy tính)
        self.frame_top_right = tk.Frame(window)
        self.frame_top_right.grid(row=0, column=1, padx=10, pady=10)

        self.canvas_top_right = tk.Canvas(self.frame_top_right, width=WIDTH, height=HEIGHT)
        self.canvas_top_right.pack()

        self.capture_frame_top_right = tk.Frame(self.frame_top_right, width=CAPTURE_WIDTH, height=CAPTURE_HEIGHT)
        self.capture_frame_top_right.pack(padx=10, pady=10)

        self.capture_image_top_right = tk.Label(self.capture_frame_top_right)
        self.capture_image_top_right.pack()
        self.capture_frame_top_right.pack_propagate(0)

        self.btn_start_top_right = tk.Button(self.frame_top_right, text='Start', command=self.start_top_right)
        self.btn_start_top_right.pack(side=tk.TOP, padx=10, pady=10)

        self.btn_stop_top_right = tk.Button(self.frame_top_right, text='Stop', command=self.stop_top_right)
        self.btn_stop_top_right.pack(side=tk.TOP, padx=10, pady=10)

        self.lbl_result_lp_top_right = tk.Label(self.frame_top_right, text='License Plate: Not found')
        self.lbl_result_lp_top_right.pack(side=tk.TOP, padx=10, pady=10)

        self.lbl_result_uuid_top_right = tk.Label(self.frame_top_right, text='UUID: Not found')
        self.lbl_result_uuid_top_right.pack(side=tk.TOP, padx=10, pady=10)

        # Phần dưới bên trái (Message)
        self.frame_bottom_left = tk.Frame(window)
        self.frame_bottom_left.grid(row=1, column=0, padx=10, pady=10)

        self.lbl_message_left = tk.Label(self.frame_bottom_left, text='Message:')
        self.lbl_message_left.pack(side=tk.LEFT)

            # Hiển thị danh sách lỗi
        self.lbl_esp32_error = tk.Label(self.frame_bottom_left, textvariable=self.esp32_error_message, fg='red')
        self.lbl_esp32_error.pack(side=tk.LEFT)

        # Phần dưới bên phải (Message)
        self.frame_bottom_right = tk.Frame(window)
        self.frame_bottom_right.grid(row=1, column=1, padx=10, pady=10)

        self.lbl_message_right = tk.Label(self.frame_bottom_right, text='Message:')
        self.lbl_message_right.pack(side=tk.LEFT)

            # Hiển thị danh sách lỗi
        self.lbl_video_capture_error = tk.Label(self.frame_bottom_right, textvariable=self.video_capture_error_message, fg='red')
        self.lbl_video_capture_error.pack(side=tk.LEFT)

        # Label cổng vào
        self.lbl_input_port = tk.Label(self.frame_top_left, text='Cổng vào')
        self.lbl_input_port.pack(side=tk.TOP, padx=10, pady=10)

        # Label cổng ra
        self.lbl_output_port = tk.Label(self.frame_top_right, text='Cổng ra')
        self.lbl_output_port.pack(side=tk.TOP, padx=10, pady=10)


        # Các biến và cờ cho phần trên bên trái
        self.running_top_left = False
        self.after_id_top_left = None
        self.can_capture_top_left = True
        self.previous_capture_image_top_left = None

        # Các biến và cờ cho phần trên bên phải
        # self.video_capture = cv2.VideoCapture(0)
        self.running_top_right = False
        self.after_id_top_right = None
        self.can_capture_top_right = True
        self.previous_capture_image_top_right = None

    # Các phương thức bắt sự kiện cho phần trên bên trái
    def start_top_left(self):
        self.running_top_left = True
        self.update_image_top_left()

    def stop_top_left(self):
        self.running_top_left = False
        if self.after_id_top_left is not None:
            self.window.after_cancel(self.after_id_top_left)
            self.after_id_top_left = None

    # Các phương thức bắt sự kiện cho phần trên bên phải
    def start_top_right(self):
        self.running_top_right = True
        self.update_image_top_right()

    def stop_top_right(self):
        self.running_top_right = False
        if self.after_id_top_right is not None:
            self.window.after_cancel(self.after_id_top_right)
            self.after_id_top_right = None

    # Các phương thức cập nhật hình ảnh cho phần trên bên trái
    def update_image_top_left(self):
        if not self.running_top_left:
            return
        try:
            response = requests.get(URL)
            if response.status_code == 200:
                img_bytes = io.BytesIO(response.content)
                img = Image.open(img_bytes)
                img = img.resize((WIDTH, HEIGHT))
                img_np = np.array(img)
                img = Image.fromarray(cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY))
                self.img_top_left = ImageTk.PhotoImage(img)
                self.canvas_top_left.create_image(0, 0, image=self.img_top_left, anchor=tk.NW)

                cropped_img, img = model.predict(img_np)
                license_plate = model.format()

                if license_plate != "":
                    if license_plate != self.lbl_result_lp_top_left.cget('text')[15:]:
                        self.lbl_result_lp_top_left.config(text='License Plate: ' + license_plate)
                        capture_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
                        capture_img = cv2.resize(capture_img, (CAPTURE_WIDTH, CAPTURE_HEIGHT))
                        pil_capture_img = Image.fromarray(capture_img)
                        pil_capture_img = ImageTk.PhotoImage(pil_capture_img)
                        self.capture_image_top_left.config(image=pil_capture_img)
                        self.capture_image_top_left.image = pil_capture_img
                        # self.capture()      # Gọi phương thức chụp ảnh khi có sự nhận diện biển số
                else:
                    self.lbl_result_lp_top_left.config(text='License Plate: Not found')
                    if self.previous_capture_image_top_left is not None:
                        # Sử dụng hình ảnh chụp trước đó nếu không có biển số được nhận dạng
                        pil_capture_img = Image.fromarray(self.previous_capture_image_top_left)
                        pil_capture_img = ImageTk.PhotoImage(pil_capture_img)
                        self.capture_image_top_left.config(image=pil_capture_img)
                        self.capture_image_top_left.image = pil_capture_img
            else:
                print("Khong ket noi voi cam duoc")

        except Exception as e:
            self.lbl_result_lp_top_left.config(text=f'Error: {str(e)}')
            print("An error occurred:", e)

        finally:
            self.after_id_top_left = self.window.after(DELAY, self.update_image_top_left)

    # Các phương thức cập nhật hình ảnh cho phần trên bên phải
    def update_image_top_right(self):
        if not self.running_top_right:
            return
        try:
            ret, frame = cap.read()
            #ret, frame=self.video_capture.read()
            if ret:
                frame = cv2.resize(frame, (WIDTH, HEIGHT))
                img_np = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # chỉnh lại màu sắc
                img = Image.fromarray(img_np)
                self.img_top_right = ImageTk.PhotoImage(img)
                self.canvas_top_right.create_image(0, 0, image=self.img_top_right, anchor=tk.NW)

                # Xử lý nhận dạng biển số
                cropped_img, img = model.predict(frame)
                license_plate = model.format()

                if license_plate != "":
                    if license_plate != self.lbl_result_lp_top_right.cget('text')[15:]:
                        self.lbl_result_lp_top_right.config(text='License Plate: ' + license_plate)
                        capture_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
                        capture_img = cv2.resize(capture_img, (CAPTURE_WIDTH, CAPTURE_HEIGHT))
                        pil_capture_img = Image.fromarray(capture_img)
                        pil_capture_img = ImageTk.PhotoImage(pil_capture_img)
                        self.capture_image_top_right.config(image=pil_capture_img)
                        self.capture_image_top_right.image = pil_capture_img
                        # self.capture()      # Gọi phương thức chụp ảnh khi có sự nhận diện biển số
                else:
                    self.lbl_result_lp_top_right.config(text='License Plate: Not found')
                    if self.previous_capture_image_top_right is not None:
                        # Sử dụng hình ảnh chụp trước đó nếu không có biển số được nhận dạng
                        pil_capture_img = Image.fromarray(self.previous_capture_image_top_right)
                        pil_capture_img = ImageTk.PhotoImage(pil_capture_img)
                        self.capture_image_top_right.config(image=pil_capture_img)
                        self.capture_image_top_right.image = pil_capture_img

        except Exception as e:
            self.lbl_result_lp_top_right.config(text=f'Error: {str(e)}')
            print("An error occurred:", e)

        finally:
            self.after_id_top_right = self.window.after(DELAY, self.update_image_top_right)

    # Các phương thức chụp ảnh
    def capture(self):
        if self.can_capture_top_left:
            self.previous_capture_image_top_left = self.capture_image_top_left.image
        if self.can_capture_top_right:
            self.previous_capture_image_top_right = self.capture_image_top_right.image



@app.route('/process_post', methods=['POST'])
def receive_uuid():
    uuid = request.form.get('uuid')
    entry_signal=request.form.get('entry_signal')
    if entry_signal=="True":
        app_window.lbl_result_uuid_top_left.config(text='UUID: ' + uuid)
    else:
        app_window.lbl_result_uuid_top_right.config(text='UUID: ' + uuid)
    return 'UUID received'


@app.route('/')
def index():
    return 'Hello, World!'


if __name__ == '__main__':
    app_window = App(window)
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 8000}).start()
    window.mainloop()
