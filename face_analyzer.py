
import time
import json
import os
import pymongo
import face_recognition
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

    #get face length
    #get midpoint of each eyebrow and find the midpoint between them. This is the top of the face
    print(landmark_map['left_eyebrow'][2])
    print(landmark_map['right_eyebrow'][2])

    #get the lowest point on the chin. This is the bottom of the face.
    print(landmark_map['chin'][8])

    #now determine if this is a frontal view, or turned view of the face. 

    

if __name__ == "__main__":

    usersToProcess = ["usr-samant3482068042"]
    for user in usersToProcess:
        #processImages(user)
        face_landmarks_list = getLandmarks(user)
        for landmark_map in face_landmarks_list:
            faceSpecs = getFaceSpecs(landmark_map[0])
        
    
    
    #drawGuides("1-2.jpeg")
