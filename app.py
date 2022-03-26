import cv2
import time
import numpy as np
from QR_Generator import QR_GEN, decode, ZBarSymbol
from flask import Flask, render_template, Response

app = Flask(__name__)

def FPS(img, fps, latency):
	cv2.putText(img, f"FPS: {str(int(fps))}", org=(7, 25), fontFace=cv2.FONT_HERSHEY_PLAIN,
				fontScale=1, color=(0, 0, 0), thickness=1)

	cv2.putText(img, f"Latency: {str(latency)}s", org=(97, 25), fontFace=cv2.FONT_HERSHEY_PLAIN,
				fontScale=1, color=(0, 0, 0), thickness=1)

	return img

def gen_frames():
	pTime, pTimeL = 0, 0
	previous = time.time()
	delta = 0
	message = ""
	a = 0

	gen = QR_GEN("names.csv")
	url = "http://192.168.0.110:8080/video"

	cap = cv2.VideoCapture(0)
	cap.set(10, 150)

	while True:
		_, img = cap.read()
		# img = cv2.flip(img, 1)

		img = cv2.resize(img, (640, 480))
		# gen.qr_check(img)

		decrypt = decode(img, symbols=[ZBarSymbol.QRCODE])
		if decrypt:
			polygon_cords = decrypt[0].polygon
			img = gen.plot_polygon(img, polygon_cords)

		# # FPS
		cTimeL = time.time()

		cTime = time.time()
		if (cTime - pTime) != 0:
			fps = 1 / (cTime - pTime)
			latency = np.round((cTimeL - pTimeL), 4)
			pTime, pTimeL = cTime, cTimeL
			a += 1

			img = FPS(img, fps, latency)

		# Video stream
		ret, buffer = cv2.imencode('.jpg', img)
		img = buffer.tobytes()
		yield (b'--frame\r\n'
			   b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')


@app.route('/')
def index():
	return render_template('index.html')

@app.route('/video_feed')
def video_feed():
	return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
	app.run(debug=True)