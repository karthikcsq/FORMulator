from flask import Flask, request, redirect, url_for, render_template, Response
import cv2
import os
import cv2
import mediapipe as mp
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
from judge import readFile

# method for corrections
import ast
from math import *
def judge(modelFile, yourFile):
    finalString = ""
    msOne, coordsOne = readFile(modelFile)
    msTwo, coordsTwo = readFile(yourFile)
    # coordsOne and coordsTwo are lists of coordinates of body parts, where One is ideal and Two is user input
    # THESE LISTS SHOULD BE STORED AS [LWrist,RWrist,LElbow,RElbow,LShoulder,RShoulder,LHip,RHip,LKnee,RKnee,LAnkle,RAnkle]

    parts = {
        2: "Left Elbow",
        3: "Right Elbow",
        4: "Left Shoulder",
        5: "Right Shoulder",
        6: "Left Hip",
        7: "Right Hip",
        8: "Left Knee",
        9: "Right Knee",
        
    }

    leniency = {
        2: [10,0.00001],
        3: [10,0.00001],
        4: [5,0.00001],
        5: [5,0.00001],
        6: [1,0.00001],
        7: [1,0.00001],
        8: [10,0.00001],
        9: [10,0.00001],
    }

    LENIENCE = 10
    STOP_LENIENCE = 0.000001
    # breaks frames into key frames, only storing important frames (like when you stop raising your hand)
    keyFramesOne = []
    keyFramesTwo = []
    
    angleOne = []
    angleTwo = []

    # coordsOne[part][coord][x/y]

    
    for x in parts:
        part_key_frames = []
        part_angle_one = []
        prevAngle = None
        curr_state = None
        prevDelta = None
        acc = None
        delta = None

        # for each frame, check each part for change in angle
        for i in range(len(coordsOne[x])):
            curr = calcAngle(coordsOne[x-2][i], coordsOne[x][i], coordsOne[x+2][i])
            if prevAngle is not None:
                delta = abs(curr - prevAngle)
                
                if (acc is not None and (delta < leniency[x][1] and acc > 1) or delta > leniency[x][0]):
                    curr_state = curr - prevAngle > 0
                    if prevOpen is None or curr_state != prevOpen:
                        part_key_frames.append(i)
                        part_angle_one.append(curr - prevAngle)
                
                if prevDelta is not None:
                    acc = delta - prevDelta
                    prevDelta = delta
                    
                prevOpen = curr_state

            prevAngle = curr
            if delta is not None:
                prevDelta = delta

        keyFramesOne.append(part_key_frames)
        angleOne.append(part_angle_one)

    b = 0

    for x in parts:
        part_key_frames = []
        part_angle_two = []
        prevAngle = None
        curr_state = None
        prevDelta = None
        acc = None
        delta = None

        # for each frame, check each part for change in angle
        for i in range(len(coordsTwo[x])):
            curr = calcAngle(coordsTwo[x-2][i], coordsTwo[x][i], coordsTwo[x+2][i])
            if prevAngle is not None:
                delta = abs(curr - prevAngle)
                
                if (acc is not None and (delta < leniency[x][1] and acc > 1) or delta > leniency[x][0]):
                    curr_state = curr - prevAngle > 0
                    if prevOpen is None or curr_state != prevOpen:
                        part_key_frames.append(i)
                        part_angle_two.append(curr - prevAngle)
                
                if prevDelta is not None:
                    acc = delta - prevDelta
                    prevDelta = delta
                    
                prevOpen = curr_state

            prevAngle = curr
            if delta is not None:
                prevDelta = delta

        keyFramesTwo.append(part_key_frames)
        angleTwo.append(part_angle_two)

    # Everything before is finiding key features acorss 2 videos and writing them down

    for x in range(len(keyFramesOne)):
        if len(keyFramesOne[x]) > 0 and len(keyFramesTwo[x]) > 0:
            offset = float(msTwo[keyFramesTwo[x][0]]) - float(msOne[keyFramesOne[x][0]]) 
            break

    missed = False
    b = 0
    for j in parts:
        strOne = None
        for k in range(len(keyFramesOne[b])):
            if (len(keyFramesTwo[b]) < k or keyFramesTwo[b] != keyFramesOne[b]) and strOne != None:                
                missed = True
            
            timeOne = float(msOne[keyFramesOne[b][k]])
            timeTwo = float(float(msTwo[keyFramesOne[b][k]]) + offset)

            if(b >= len(angleTwo) or  k >= len(angleTwo[b])):
                strOne = parts[j] + " " + ("open" if angleOne[b][k] > 0 else "close")
                finalString += "missed " + str(strOne) + " at time: " + str(timeTwo - offset) + "s -- "
                continue
            else:
                strOne = parts[j] + " " + ("open" if angleOne[b][k] > 0 else "close")
                strTwo = parts[j] + " " + ("open" if angleTwo[b][k] > 0 else "close")
            
            
            if (strOne != strTwo):
                finalString += "You did: " + strTwo + " instead of " + strOne + " -- "
            elif (timeOne - (timeTwo - offset) > 0.05):
                finalString += "You did: " + str(strTwo) + " " + str(timeOne - (timeTwo - offset)) + " ms earlier than supposed to at " + str(timeTwo - offset) + "s -- "
            elif (timeOne - (timeTwo - offset) < -0.05):
                finalString += "You did: " + str(strTwo) + " " + str( - (timeOne - (timeTwo - offset)) ) + " ms later than supposed to at " + str(timeTwo - offset) + "s -- "
        b+=1
    
    if(not missed):
        finalString += "Congratulations! You've perfected the form!" + " -- "
    
    return finalString


app = Flask(__name__)
app.secret_key = 'key'

# Directory to store uploaded video files
UPLOAD_FOLDER = './poseCorrector/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# To store the uploaded video paths
video_files = []

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_files():
    global video_files
    video_files.clear()  # Clear previous files
    files = request.files.getlist('videos')

    for file in files:
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            video_files.append(filepath)

    return redirect(url_for('video_display'))

@app.route('/video_display')
def video_display():
    return render_template('display.html')

counter = 0
def generate_frames(video_path):
    global counter
    counter += 1
    # file setup
    if(counter == 1):
        f = open("abhiPipelineModel.txt", "w")
        f.write("Iter,LWrist_x,LWrist_y,RWrist_x,RWrist_y,LElbow_x,LElbow_y,RElbow_x,RElbow_y,LShoulder_x,LShoulder_y,RShoulder_x,RShoulder_y,LHip_x,LHip_y,RHip_x,RHip_y,LKnee_x,LKnee_y,RKnee_x,RKnee_y,LAnkle_x,LAnkle_y,RAnkle_x,RAnkle_y\n")
        cap = cv2.VideoCapture(video_path)
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            # model video writing
            while cap.isOpened():
                ret, frame = cap.read()

                if(not ret):
                    break
                
                # Recolor image to RGB
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False

                # Make detection
                results = pose.process(image)

                # Recolor back to BGR
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                # Extract landmarks
                try:
                    landmarks = results.pose_landmarks.landmark

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

                    timeStamp = cap.get(cv2.CAP_PROP_POS_MSEC)
                    timeStamp = timeStamp / 1000

                    f.write(str(timeStamp) + ";" + str(wristL) + ";" + str(wristR) + ";" + str(elbowL) + ";" + str(elbowR) + ";" + str(shoulderL) + ";" + str(shoulderR) + ";" + str(hipL) + ";" + str(hipR) + ";" + str(kneeL) + ";" + str(kneeR) + ";" + str(ankleL) + ";" + str(ankleR) + "\n")
                
                except:
                    pass
                
                # Render detections
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                        mp_drawing.DrawingSpec(color=(245,117,66), thickness=5, circle_radius=5), 
                                        mp_drawing.DrawingSpec(color=(245,66,230), thickness=5, circle_radius=5) 
                                        )

                ret, buffer = cv2.imencode('.jpg', image)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    elif(counter == 2):
        f2 = open("abhiPipelineYour.txt", "w")
        f2.write("Iter,LWrist_x,LWrist_y,RWrist_x,RWrist_y,LElbow_x,LElbow_y,RElbow_x,RElbow_y,LShoulder_x,LShoulder_y,RShoulder_x,RShoulder_y,LHip_x,LHip_y,RHip_x,RHip_y,LKnee_x,LKnee_y,RKnee_x,RKnee_y,LAnkle_x,LAnkle_y,RAnkle_x,RAnkle_y\n")
        cap2 = cv2.VideoCapture(video_path)
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            # your video writing
            while cap2.isOpened:
                ret2, frame2 = cap2.read()

                if(not ret2):
                    break
                
                # Recolor image to RGB
                image2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
                image2.flags.writeable = False

                # Make detection
                results2 = pose.process(image2)

                # Recolor back to BGR
                image2.flags.writeable = True
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

                    timeStamp = cap2.get(cv2.CAP_PROP_POS_MSEC)
                    timeStamp = timeStamp / 1000

                    f2.write(str(timeStamp) + ";" + str(wristL) + ";" + str(wristR) + ";" + str(elbowL) + ";" + str(elbowR) + ";" + str(shoulderL) + ";" + str(shoulderR) + ";" + str(hipL) + ";" + str(hipR) + ";" + str(kneeL) + ";" + str(kneeR) + ";" + str(ankleL) + ";" + str(ankleR) + "\n")

                except:
                    pass
                
                
                # Render detections
                mp_drawing.draw_landmarks(image2, results2.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                        mp_drawing.DrawingSpec(color=(245,117,66), thickness=5, circle_radius=5), 
                                        mp_drawing.DrawingSpec(color=(245,66,230), thickness=5, circle_radius=5) 
                                            )
                
                ret, buffer = cv2.imencode('.jpg', image2)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    app.app_context()
    # yield judge("abhiPipelineModel.txt", "abhiPipelineYour.txt")
    # return render_template('submitted.html', paragraph=judge("abhiPipelineModel.txt", "abhiPipelineYour.txt"))
    
@app.route('/submitted')
def submitted():
    paragraph = judge("abhiPipelineModel.txt", "abhiPipelineYour.txt")
    paragraph.replace("\n", "<br>")
    return render_template('submitted.html', paragraph=paragraph)

@app.route('/video_feed/<int:video_id>')
def video_feed(video_id):
    if 0 <= video_id < len(video_files):
        return Response(generate_frames(video_files[video_id]),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "Video not found", 404

def calcAngle(pointOne, pointTwo, pointThree):
    # pointOne is wrist/foot.
    # pointTwo is elbow/knee
    # pointThree is shoulder/hip

    vectorOne = [pointOne[0] - pointTwo[0], pointOne[1] - pointTwo[1]]
    vectorTwo = [pointThree[0] - pointTwo[0], pointThree[1] - pointTwo[1]]
    

    dotProduct = vectorOne[0] * vectorTwo[0] + vectorOne[1] * vectorTwo[1]
    
    magnitudeOne = sqrt(vectorOne[0] * vectorOne[0] + vectorOne[1] * vectorOne[1])
    magnitudeTwo = sqrt(vectorTwo[0] * vectorTwo[0] + vectorTwo[1] * vectorTwo[1])
    
    return round(degrees(acos(dotProduct/(magnitudeOne * magnitudeTwo))), 3)

def readFile(file):
    parts = [[],[],[],[],[],[],[],[],[],[],[],[]]
    ms = []
    # Read the file line by line
    with open(file, 'r') as file:
        next(file)
        for line in file:
            split = line.strip().split(";")
            # split will be list of [x, y]s
            # for each part coords
            ms.append(split[0])
            for x in range(1, len(split)):
                # each [x, y]
                coords = ast.literal_eval(split[x])
                parts[x-1].append(coords)
    return ms, parts

# judge("abhiPipelineModel.txt", "abhiPipelineYour.txt")

if __name__ == '__main__':
    app.run(debug=True)
