from flask import Flask, Response
from picamera2 import Picamera2, Preview
import time

app = Flask(__name__)

def generate_frames():
    camera = Picamera2()
    camera_config = camera.create_still_configuration(
        main={"size":(640,480)},
        lores={"size":(640,480)},
        display="lores"
        )
    camera.configure(camera_config)
    camera.start()
    time.sleep(2)
    try:
        while True:
            # Capture frame from the camera
            camera.capture_file("temp.jpg")
            # Read the captured image and yield it as a byte stream
            with open('temp.jpg', 'rb') as f:
                frame = f.read()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        # Close the camera instance when done
        camera.stop()
        camera.close()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
    
