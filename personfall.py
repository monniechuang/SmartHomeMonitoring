# -*- coding: utf-8 -*-

from darkflow.net.build import TFNet
import cv2
import numpy as np
from urllib.request import urlopen
import sys
import requests 
import wget
import math
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
cred = credentials.Certificate("C:/Users/Chuang/Desktop/carematch-c8be7-firebase-adminsdk-w2so4-581ef4450b.json")
firebase_admin.initialize_app(cred)
db=firestore.client()
options = {"model": "cfg/yolo.cfg", "load": "bin/yolov2.weights", "threshold": 0.4}
token = 'rzmkZIv1vWzT7rixNkgJXhVT1HCKnvfi14s30GaRZS8'
tfnet = TFNet(options)
time_record = round(time.time()) 


stream = urlopen('http://192.168.50.104:5001/stream')
bytes = bytes()
while True:
    people = []
    chairs = []
    bytes += stream.read(1024)
    a = bytes.find(b'\xff\xd8')
    b = bytes.find(b'\xff\xd9')
    if a != -1 and b != -1:
        jpg = bytes[a:b+2]
        bytes = bytes[b+2:]
        i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR) #<class 'numpy.ndarray'> # image decode
        result = tfnet.return_predict(i)

        
        for detection in result:
            if detection['label'] == 'chair':   
                chairs.append(detection)
                
                cv2.rectangle(i, (detection['topleft']['x'], detection['topleft']['y']), 
                              (detection['bottomright']['x'], detection['bottomright']['y']), 
                              3)
                cv2.putText(i, detection['label'], 
                            (detection['topleft']['x'], detection['topleft']['y'] - 13),
                            
                            cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)

                cv2.putText(i, str(math.floor(detection['confidence']*100)), 
                            (detection['topleft']['x'], detection['topleft']['y'] + 13),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)	
                chair_mid=(detection['bottomright']['y']+detection['topleft']['y'])/2
                print("cm"+str(chair_mid))
                
            if detection['label'] == 'person':   
                people.append(detection)
                
                cv2.rectangle(i, (detection['topleft']['x'], detection['topleft']['y']), 
                              (detection['bottomright']['x'], detection['bottomright']['y']), 
                              3)
                cv2.putText(i, detection['label'], 
                            (detection['topleft']['x'], detection['topleft']['y'] - 13),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)

                cv2.putText(i, str(math.floor(detection['confidence']*100)), 
                            (detection['topleft']['x'], detection['topleft']['y'] + 13),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)		
                x = detection['bottomright']['x'] - detection['topleft']['x']
                y = detection['bottomright']['y'] - detection['topleft']['y']
                person_bottom=detection['bottomright']['y']
                record = "x:"+str(x)+" y:"+str(y) 
                print("pb"+str(person_bottom))
  
        mychair = chairs[0];
        mychair_mid = (mychair['bottomright']['y']+mychair['topleft']['y'])/2
        
        for person in people:
            x = person['bottomright']['x'] - person['topleft']['x']
            y = person['bottomright']['y'] - person['topleft']['y']
            person_bottom = person['bottomright']['y']
            
            if x > 500 and y < 250 and mychair_mid < person_bottom:
                url = 'http://192.168.50.104:5001/image'
                wget.download(url, 'C:/Users/Chuang/Desktop/darkflow/fall/fall'+str(x+y)+'.jpeg')  #路徑要取代
                file = {'imageFile': open('C:/Users/Chuang/Desktop/darkflow/fall/fall'+str(x+y)+'.jpeg', 'rb') } #路徑要取代
                param = {
                        'message':'家中老人可能跌倒在家中,請透過App的即時監控功能查看,家中老人是否有危險且盡速通知看護或報警\n'+'http://192.168.50.104:5001/stream' #文字訊息
                        }
                headers = {
                        "Authorization": "Bearer " + token, 
                        }
                session = requests.Session()
                r = session.post("https://notify-api.line.me/api/notify", params=param, headers = headers, files = file)
               
        
       
          
        cv2.imshow('care&match cam', i)
        
        if cv2.waitKey(1) == 27:
            
            exit(0)
