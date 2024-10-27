import cv2
import mediapipe as mp
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# cap = cv2.VideoCapture('Dribble.mp4')

input_video_path = 'FullDribble.mp4'

# f = open("yurBrodie.txt", "r")
# s = f.readline()
# f = open("yurBrodie.txt", "w")
# f.write("Iter,LWrist_x,LWrist_y,RWrist_x,RWrist_y,LElbow_x,LElbow_y,RElbow_x,RElbow_y,LShoulder_x,LShoulder_y,RShoulder_x,RShoulder_y,LHip_x,LHip_y,RHip_x,RHip_y,LKnee_x,LKnee_y,RKnee_x,RKnee_y,LAnkle_x,LAnkle_y,RAnkle_x,RAnkle_y\n")

cap = cv2.VideoCapture(input_video_path)
cap2 = cv2.VideoCapture(0)

counter = 0
## Setup mediapipe instance
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        ret2, frame2 = cap2.read()
        
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

    cap.release()
    cv2.destroyAllWindows()