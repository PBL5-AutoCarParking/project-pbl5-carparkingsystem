
import cv2
import numpy as np
import urllib.request
import matplotlib.pyplot as plt


url = 'http://192.168.91.35/cam-lo.jpg'
while (1):
    img = urllib.request.urlopen(url)
    img_np = np.array(bytearray(img.read()), dtype=np.uint8)
    frame = cv2.imdecode(img_np, -1)
    print(frame)
    cv2.imshow("img", frame)
    # plt.imshow(frame)
    # plt.show()
    if cv2.waitKey(10) & 0xFF == ord('q'):
        frame.release()
        cv2.destroyAllWindowns()
        break
