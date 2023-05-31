import tkinter as tk
from PIL import Image, ImageTk
import cv2
import time
import serial
from src.lp_recognition import E2E

model = E2E()
DELAY = 1000  # Milliseconds to wait between updating the image
WIDTH, HEIGHT = 640, 480  # Width and height of the image
# ser = serial.Serial('CO5', 9600)


class App:
    def __init__(self, window):
        self.window = window
        self.window.title('Camera Image Stream')
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
        self.lbl_result = tk.Label(window, text='Not found')
        self.lbl_result.pack(side=tk.LEFT, padx=10, pady=10)
        self.video_capture = cv2.VideoCapture(1)  # Truy cập camera máy tính (số 0 có nghĩa là camera gốc)

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
        # url_api = 'http://127.0.0.1:8000/cars/'
        # data = {'license_plate': text, 'car_model': 'Car', 'car_color': 'red'}
        #
        # response = requests.post(url_api, data=data)
        # print(response.status_code)
        # print(response.json())

    def update_image(self):
        if not self.running:
            return
        try:
            # Read frame from the camera
            ret, frame = self.video_capture.read()

            if ret:
                # Perform any processing or prediction on the frame here
                img = model.predict(frame)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(img)

                # Resize the image to fit the canvas
                pil_img = pil_img.resize((WIDTH, HEIGHT))

                # Convert the PIL image to a Tkinter PhotoImage
                self.img = ImageTk.PhotoImage(pil_img)

                # Draw the image on the canvas
                self.canvas.create_image(0, 0, image=self.img, anchor=tk.NW)

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
