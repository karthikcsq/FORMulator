from flask import Flask, flash, request, redirect, url_for, Response, render_template, jsonify
from werkzeug.utils import secure_filename
import os
import cv2
import mediapipe as mp
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

UPLOAD_FOLDER = './'
ALLOWED_EXTENSIONS = {'mp4','mov'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
@app.route('/', methods=['GET', 'POST'])
def default():
    return redirect(url_for('index', video_name='FullDribble.mp4'))

@app.route('/<video_name>', methods=['GET', 'POST'])
def index(video_name):
    return render_template('index.html', videoname=video_name, upload=upload_file(), files=list_files())

@app.route('/fileclick', methods=['GET', 'POST'])
def list_files():
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(path) and allowed_file(filename):
            files.append(filename)
    retstr = '<form action="/forward" method="post">\n'
    for (i, filename) in enumerate(files):
        retstr += f'\t<button name="Btn-{filename}" type="submit">{filename}</button>\n'
    retstr += "</form>"
    return retstr

@app.route('/forward', methods=['GET', 'POST'])
def use_video():
    if request.method == 'POST':
        for key in request.form.keys():
            if key.startswith('Btn-'):
                filename = os.path.join(app.config['UPLOAD_FOLDER'], key[4:])
                return redirect(url_for('index', video_name=filename))

@app.route('/video_feed/<video_name>', methods=['GET', 'POST'])
def video_feed(video_name):
    return Response(gen_frames(video_name), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames(video_name):
    input_video_path = video_name
    cap = cv2.VideoCapture(input_video_path)
    camera = cv2.VideoCapture(0)
    while True:
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while camera.isOpened():
                ret, frame = camera.read()
                ret2, frame2 = cap.read()

                if not ret2 or not ret:
                    continue
                
                # Recolor image to RGB
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
                
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
                    landmarks = results.pose_landmarks.landmark
                    # print(landmarks)
                except:
                    pass
                
                
                # Render detections
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                        mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                        mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                         )
                
                mp_drawing.draw_landmarks(image, results2.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                        mp_drawing.DrawingSpec(color=(66,117,245), thickness=5, circle_radius=2), 
                                        mp_drawing.DrawingSpec(color=(66,230,245), thickness=5, circle_radius=2) 
                                         )
                
                
                if not ret:
                    break
                else:
                    ret, buffer = cv2.imencode('.jpg', image)
                    image = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('download_file', name=filename))
    return '''
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
            <input type=file name=file>
            <input type=submit value=Upload>
        </form>
        '''
    
if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True,port="5000")