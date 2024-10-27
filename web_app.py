from flask import Flask, flash, request, redirect, url_for, Response, render_template, jsonify
from camera import VideoCamera
from werkzeug.utils import secure_filename
import os

import cv2
import mediapipe as mp
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'mp4','mov'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

video_stream = VideoCamera()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen(video_stream), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen(camera):
    input_video_path = 'FullDribble.mp4'
    cap = cv2.VideoCapture(input_video_path)
    counter = 0
    ## Setup mediapipe instance
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            image2 = camera.get_frame()
            
            # Recolor image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # image2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
            
            image.flags.writeable = False
            image2.flags.writeable = False
        
            # Make detection
            results = pose.process(image)
            results2 = pose.process(image2)
        
            # Recolor back to BGR
            image.flags.writeable = True
            image2.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            image2 = cv2.cvtColor(image2, cv2.COLOR_RGB2BGR)
            
            # Extract landmarks
            try:
                landmarks = results2.pose_landmarks.landmark
                
                # Get coordinates
                kneeR = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
                hipR = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                ankleR = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].y]
                kneeL = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                hipL = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                ankleL = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y]
                
                elbowR = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                wristR = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                shoulderR = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                elbowL = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wristL = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                shoulderL = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]

                elbowAngle = calcAngle(wristR, elbowR, shoulderR)
                kneeAngle = calcAngle(ankleR, kneeR, hipR)
                counter += 1

                # height of knee hip elbow wrist shoulder
                # angle of knee and elbow
                printList = [str(counter) + "," + str(wristL) + "," + str(wristR) + "," + str(elbowL) + "," + str(elbowR) + "," + str(shoulderL) + "," + str(shoulderR) + "," + str(hipL) + "," + str(hipR) + "," + str(kneeL) + "," + str(kneeR) + "," + str(ankleL) + "," + str(ankleR)]

                # f.write(str(counter) + ";" + str(wristL) + ";" + str(wristR) + ";" + str(elbowL) + ";" + str(elbowR) + ";" + str(shoulderL) + ";" + str(shoulderR) + ";" + str(hipL) + ";" + str(hipR) + ";" + str(kneeL) + ";" + str(kneeR) + ";" + str(ankleL) + ";" + str(ankleR) + "\n")


                
                # print(str(kneeR) + " " + str(hipR) + " " + str(elbowR) + " " + str(wristR) + " " + str(shoulderR))
                # print(str(elbowAngle) + " " + str(kneeAngle))

                # # Visualize angle
                cv2.putText(image, str(elbowAngle), 
                            tuple(np.multiply(elbow, [640, 480]).astype(int)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                    )
                        
            except:
                pass
            
            
            # Render detections
            # imgClone = image2
            mp_drawing.draw_landmarks(image2, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=5, circle_radius=5), 
                                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=5, circle_radius=5) 
                                    )
            
            mp_drawing.draw_landmarks(image2, results2.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color=(66,117,245), thickness=5, circle_radius=2), 
                                    mp_drawing.DrawingSpec(color=(66,230,245), thickness=5, circle_radius=2) 
                                    )
            
            
            cv2.imshow('Mediapipe Feed', image2)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
            
            yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

        cap.release()
        cv2.destroyAllWindows()

# @app.route('/', methods=['GET', 'POST'])
# @app.route('/')
# def upload_file():
    # if request.method == 'POST':
    #     # check if the post request has the file part
    #     if 'file' not in request.files:
    #         flash('No file part')
    #         return redirect(request.url)
    #     file = request.files['file']
    #     # If the user does not select a file, the browser submits an
    #     # empty file without a filename.
    #     if file.filename == '':
    #         flash('No selected file')
    #         return redirect(request.url)
    #     if file and allowed_file(file.filename):
    #         filename = secure_filename(file.filename)
    #         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    #         # return redirect(url_for('download_file', name=filename))
    # return '''
    # <!doctype html>
    # <title>Upload new File</title>
    # <h1>Upload new File</h1>
    # <form method=post enctype=multipart/form-data>
    #   <input type=file name=file>
    #   <input type=submit value=Upload>
    # </form>
    # '''
    
app.run()