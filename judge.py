import ast
from math import *




def judge():
    msOne, coordsOne = readFile('coordsOne.txt')
    msTwo, coordsTwo = readFile('coordsTwo.txt')
    # coordsOne and coordsTwo are lists of coordinates of body parts, where One is ideal and Two is user input
    # THESE LISTS SHOULD BE STORED AS [LWrist,RWrist,LElbow,RElbow,LShoulder,RShoulder,LHip,RHip,LKnee,RKnee,LAnkle,RAnkle]

    parts = {
        2: "Left Elbow",
        3: "Right Elbow",
        4: "Left Shoulder",
        5: "Right Shoulder",
        8: "Left Knee",
        9: "Right Knee",
    }

    leniency = {
        2: [10,0.00001],
        3: [10,0.00001],
        4: [5,0.00001],
        5: [5,0.00001],
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
                
                if delta is not None:
                    prevDelta = delta
                    acc = delta - prevDelta
                    
                prevOpen = curr_state

            prevAngle = curr
            if delta is not None:
                prevDelta = delta

        keyFramesOne.append(part_key_frames)
        angleOne.append(part_angle_one)

    b = 0
    for j in parts:
        for k in range(len(keyFramesOne[b])):
            print(parts[j] + ": " + ("open" if angleOne[b][k] > 0 else "close") + " (" + str(msOne[keyFramesOne[b][k]]) + ")")
        b+=1
    
    print("")
    print("")

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
                
                if delta is not None:
                    prevDelta = delta
                    acc = delta - prevDelta
                    
                prevOpen = curr_state

            prevAngle = curr
            if delta is not None:
                prevDelta = delta

        keyFramesTwo.append(part_key_frames)
        angleTwo.append(part_angle_two)

    b = 0
    for j in parts:
        for k in range(len(keyFramesTwo[b])):
            print(parts[j] + ": " + ("open" if angleTwo[b][k] > 0 else "close") + " (" + str(msTwo[keyFramesTwo[b][k]]) + ")")
        b+=1

    
            





    

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

judge()