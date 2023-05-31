import tkinter as tk
from PIL import Image, ImageTk
import requests
import io
import numpy as np
import cv2
import time
import serial
from src.lp_recognition import E2E

model = E2E()  #
IP = '192.168.1.7'  # Replace with the IP address of your ESP32-CAM
URL = f'http://{IP}/capture'
DELAY = 1000  # Milliseconds to wait between updating the image
WIDTH, HEIGHT = 640, 480  # Width and height of the image
# ser = serial.Serial('CO5', 9600)


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
        text = self.lbl_result.cget('text')

        print('Da lay duoc text:', text)
        # ser.write(b'90\n')  # Gửi gói tin để xoay servo ở góc 90 độ
        print("Da xoay")
        url_api = 'http://127.0.0.1:8000/cars/'
        data = {'license_plate': text, 'car_model': 'Car', 'car_color': 'red'}

        response = requests.post(url_api, data=data)
        print(response.status_code)
        print(response.json())


    def update_image(self):
        if not self.running:
            return
        try:
            # Get the image from the URL
            response = requests.get(URL)
            img_array = np.array(bytearray(response.content), dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            img = model.predict(img)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img)
            # # Convert the image data to a PIL image
            # pil_img = Image.open(io.BytesIO(image))

            # Resize the image to fit the canvas
            pil_img = pil_img.resize((WIDTH, HEIGHT))

            # Convert the PIL image to a Tkinter PhotoImage
            self.img = ImageTk.PhotoImage(pil_img)

            # Draw the image on the canvas
            self.canvas.create_image(0, 0, image=self.img, anchor=tk.NW)
            # print(str(model.format()))
            # print(model.format()=="")
            if model.format() != "":
                self.lbl_result.config(text=model.format())
            else:
                self.lbl_result.config(text='Not found')

            # Schedule the next update
            self.after_id = self.window.after(DELAY, self.update_image)
        except Exception as e:
            self.lbl_result.config(text=f'Error: {str(e)}')
            self.stop()


if __name__ == '__main__':
    window = tk.Tk()
    app = App(window)
    window.mainloop()
