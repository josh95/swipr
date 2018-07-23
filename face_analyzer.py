
import time
import json
import os
import pymongo
import math
import face_recognition
import csv
from PIL import Image, ImageDraw



def drawGuides(imageUrl):
    # Find all facial features and draws lines on the image as a proof of concept.
    image = face_recognition.load_image_file(imageUrl)
    face_landmarks_list = face_recognition.face_landmarks(image)

    for face_landmarks in face_landmarks_list:
        # Print the location of each facial feature in this image
        facial_features = [
            'chin',
            'left_eyebrow',
            'right_eyebrow',
            'nose_bridge',
            'nose_tip',
            'left_eye',
            'right_eye',
            'top_lip',
            'bottom_lip'
        ]

        # Let's trace out each facial feature in the image with a line!
        im = Image.open(imageUrl)
        pil_image = Image.new('RGB', (im.size))

        d = ImageDraw.Draw(pil_image)

        for facial_feature in facial_features:
            d.line(face_landmarks[facial_feature], width=4, fill="red")

    pil_image.show()
    pil_image.save("test.jpeg")


def processImages(user):
    #uses face_recognition package to read in images
    groupPics = []
    soloPics = []
    
    #sort out solo and group pics. Also delete any pictures where a face could not be found
    for picture in os.listdir("pictures/" + user):
        image = face_recognition.load_image_file("pictures/" + user + "/" + picture)
        face_locations_list = face_recognition.face_locations(image)
        if len(face_locations_list) > 1:
            groupPics.append((picture, face_locations_list))
        elif len(face_locations_list) == 1:
            soloPics.append(image)
        else:
            os.remove("pictures/" + user + "/" + picture)
            print("removed:  " + user + "/" + picture)

    #narrow down the group pictures to only be of the person
    for picture, face_locations in groupPics:
        singleOut(soloPics, picture, face_locations)
        os.remove("pictures/" + user + "/" + picture)


def getLandmarks(user):
    #read in the images in the folder and return a list of the face landmarks data
    face_landmarks_list = []
    for picture in os.listdir("pictures/" + user):
        image = face_recognition.load_image_file("pictures/" + user + "/" + picture)
        face_landmarks_list.append(face_recognition.face_landmarks(image))
    return face_landmarks_list
    
        

def singleOut(soloPics, groupPic, face_locations):
    #given a group picture and a set of images just showing the person, crop the group photos to only contain that person. 

    originalImg = Image.open("pictures/" + user + "/" + groupPic)

    facesList = []
    
    for index, faceLoc in enumerate(face_locations):
        #creates a bunch of cropped images of each face 
        faceLoc = (faceLoc[3] , faceLoc[0] , faceLoc[1], faceLoc[2])
        img2 = originalImg.crop(faceLoc)
        imgLoc = "pictures/" + user + "/" + str(index) + "-" + groupPic
        facesList.append(imgLoc)
        img2.save(imgLoc)

    for img in facesList:
        unknown_image = face_recognition.load_image_file(img)
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        known_encoding = []
        for soloImg in soloPics:
            known_encoding.append(face_recognition.face_encodings(soloImg)[0])
        results = face_recognition.compare_faces(known_encoding, unknown_encoding).count(True)

        if results < (len(known_encoding)/2):
            #delete the cropped faces that the face recognizer thinks is not the target person
            print("deleting " + img)
            os.remove(img)


def getFaceSpecs(landmark_map):
    
    def slope(p1, p2):
        try:
            m = (p2[1]-p1[1])/(p2[0]-p1[0])
        except ZeroDivisionError:
            return float('inf')
        return m

    def distance(p1, p2):
        dist = math.sqrt( (p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 )
        return dist

    def midpoint(p1, p2):
        return ( (p1[0] + p2[0]) / 2 , (p1[1] + p2[1]) / 2 )

    def getEyeSpacing():
        #how far apart a person's eyes are
        return distance(landmark_map['left_eye'][3] , landmark_map['right_eye'][0])

    def getEyeYPosition():
        #hoe high up on a person's face their eyes are. Relative to bottom of face.
        eyeMid = midpoint(landmark_map['left_eye'][3] , landmark_map['right_eye'][0])
        return distance(eyeMid, landmark_map['chin'][8])

    def getEyeDimensions(facing):
        #eye height and eye width. Can be used on a side view picture
        if facing == "front":
            x = (distance(landmark_map['right_eye'][0], landmark_map['right_eye'][3]) + distance(landmark_map['left_eye'][0], landmark_map['left_eye'][3]) )/2
            y = (distance(landmark_map['right_eye'][2], landmark_map['right_eye'][4]) + distance(landmark_map['left_eye'][2], landmark_map['left_eye'][4]) )/2

        if facing == "left":
            x = distance(landmark_map['right_eye'][0], landmark_map['right_eye'][3])
            y = distance(landmark_map['right_eye'][2], landmark_map['right_eye'][4])
        if facing == "right":
            x = distance(landmark_map['left_eye'][0], landmark_map['left_eye'][3])
            y = distance(landmark_map['left_eye'][2], landmark_map['left_eye'][4])
        return x,y

    def getNostrilWidth():
        return distance(landmark_map['nose_tip'][4] , landmark_map['nose_tip'][0])
        
    def getMouthWidth():
        #get mouth width. lip size
        return distance(landmark_map['top_lip'][0], landmark_map['top_lip'][6])

    def getLipDims():
        #upper and lower lip thickness
        upper = distance(landmark_map['top_lip'][3], landmark_map['top_lip'][9])
        lower = distance(landmark_map['bottom_lip'][3], landmark_map['bottom_lip'][9])
        return upper, lower

    def chinJawWidth():
        #width of chin and jaw
        chin = distance(landmark_map['chin'][7], landmark_map['chin'][9])
        jaw = distance(landmark_map['chin'][4], landmark_map['chin'][12])
        return chin, jaw


    #get face length
    #get midpoint of each eyebrow and find the midpoint between them. This is the top of the face
    leftEyeBr = landmark_map['left_eyebrow'][2]
    rightEyeBr = landmark_map['right_eyebrow'][2]

    topOfHeadMidpoint = midpoint(leftEyeBr, rightEyeBr)

    #get the lowest point on the chin. This is the bottom of the face.
    chin = landmark_map['chin'][8]

    faceHeight = distance( topOfHeadMidpoint, chin )
    faceWidth = distance( landmark_map['chin'][1], landmark_map['chin'][15] )
    
    print("nose to face edge")
    NTFEratio = distance(landmark_map['chin'][16],landmark_map['nose_bridge'][3])/distance(landmark_map['chin'][0],landmark_map['nose_bridge'][3])

    faceDetailDict = {"height": faceHeight,
                      "width": faceWidth,
                      "lwratio": faceHeight/ faceWidth,
        }
    upperLip , lowerLip = getLipDims()
    faceDetailDict["upperLipThick"] = upperLip / faceHeight
    faceDetailDict["lowerLipThick"] = lowerLip / faceHeight
    faceDetailDict["eyeYPosition"] = getEyeYPosition()/ faceHeight

    
    
    if NTFEratio < .67:
        eyeWidth, eyeHeight = getEyeDimensions("right")
        faceDetailDict["facing"] = "right"
        faceDetailDict["eyeWidth"] = eyeWidth / faceWidth
        faceDetailDict["eyeHeight"] = eyeHeight / faceHeight
        
        
    elif NTFEratio > 1.5:
        eyeWidth, eyeHeight = getEyeDimensions("left")
        faceDetailDict["facing"] = "left"
        faceDetailDict["eyeWidth"] = eyeWidth / faceWidth
        faceDetailDict["eyeHeight"] = eyeHeight / faceHeight
        
    else:
        print("facing forwards")
        eyeWidth , eyeHeight = getEyeDimensions("front")
        chinWidth , jawWidth = chinJawWidth()
        faceDetailDict["facing"] = "front"
        faceDetailDict["eyeWidth"] = eyeWidth / faceWidth
        faceDetailDict["eyeHeight"] = eyeHeight / faceHeight
        faceDetailDict["eyeSpacing"] = getEyeSpacing() / faceWidth
        faceDetailDict["nostrilWidth"] = getNostrilWidth() / faceWidth
        faceDetailDict["chinWidth"] = chinWidth / faceWidth
        faceDetailDict["jawWidth"] = jawWidth /faceWidth

    return faceDetailDict
        
    

if __name__ == "__main__":
    with open('OKcupidFaceDetails.csv', 'w', newline = "") as csvfile:
        fieldnames = ["height", "width", "lwratio","facing","eyeWidth","eyeHeight","eyeSpacing","nostrilWidth",
                      "chinWidth","jawWidth", "eyeYPosition", "upperLipThick", "lowerLipThick"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        
        usersToProcess = ["usr-alexa5554417525", "usr-10177844739085885402",  "usr-katie3840951519", "usr-alexan1884739531"]
        for user in usersToProcess:
            processImages(user)
            face_landmarks_list = getLandmarks(user)
            for landmark_map in face_landmarks_list:
                faceSpecs = getFaceSpecs(landmark_map[0])

                #write output

                writer.writerow(faceSpecs)
        
    
    
    #drawGuides("1-2.jpeg")
