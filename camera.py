import cv2

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()        

    def get_frame(self):
        ret, frame = self.video.read()

        # DO WHAT YOU WANT WITH TENSORFLOW / KERAS AND OPENCV
        
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        ret, jpeg = cv2.imencode('.jpg', image)

        return jpeg.tobytes()
        