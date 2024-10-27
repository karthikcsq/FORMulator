# abhi method for corrections
import ast
from math import *

# cords 1 is original perfect dance
# cords 2 is karthik perfect dance


def judge(modelFile, yourFile):
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
    # for j in parts:
    #     # for k in range(len(keyFramesOne[b])):
    #         # print(parts[j] + ": " + ("open" if angleOne[b][k] > 0 else "close") + " (" + str(msOne[keyFramesOne[b][k]]) + ")")
    #     # b+=1
    
    # print("")
    # print("")

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

    # b = 0
    # for j in parts:
    #     for k in range(len(keyFramesTwo[b])):
    #         print(parts[j] + ": " + ("open" if angleTwo[b][k] > 0 else "close") + " (" + str(msTwo[keyFramesTwo[b][k]]) + ")")
    #     b+=1

    # Everything before is finiding key features acorss 2 videos and writing them down

    for x in range(len(keyFramesOne)):
        if len(keyFramesOne[x]) > 0 and len(keyFramesTwo[x]) > 0:
            offset = float(msTwo[keyFramesTwo[x][0]]) - float(msOne[keyFramesOne[x][0]]) 
            # print("x: " + str(x))
            break

    missed = False
    b = 0
    for j in parts:
        strOne = None
        for k in range(len(keyFramesOne[b])):
            if (len(keyFramesTwo[b]) < k or keyFramesTwo[b] != keyFramesOne[b]) and strOne != None:
                # print("You missed the move: " + strOne + "!")
                missed = True
            
            timeOne = float(msOne[keyFramesOne[b][k]])
            timeTwo = float(float(msTwo[keyFramesOne[b][k]]) + offset)

            if(b >= len(angleTwo) or  k >= len(angleTwo[b])):
                strOne = parts[j] + " " + ("open" if angleOne[b][k] > 0 else "close")
                print("missed " + str(strOne) + " at time: " + str(timeTwo - offset))
                continue
            else:
                strOne = parts[j] + " " + ("open" if angleOne[b][k] > 0 else "close")
                strTwo = parts[j] + " " + ("open" if angleTwo[b][k] > 0 else "close")
            
            
            if (strOne != strTwo):
                print("You did: " + strTwo + " instead of " + strOne)
            elif (timeOne - (timeTwo - offset) > 0.05):
                print("You did: " + str(strTwo) + " " + str(timeOne - (timeTwo - offset)) + " ms earlier than supposed to at " + str(timeTwo - offset))
            elif (timeOne - (timeTwo - offset) < -0.05):
                print("You did: " + str(strTwo) + " " + str( - (timeOne - (timeTwo - offset)) ) + " ms later than supposed to at " + str(timeTwo - offset))
        b+=1
    
    if(not missed):
        print("Congratulations! You've perfected the form!")


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

judge("abhiPipelineModel.txt", "abhiPipelineYour.txt")