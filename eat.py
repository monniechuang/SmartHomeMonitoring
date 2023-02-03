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
options = {"model": "cfg/yolo.cfg", "load": "bin/yolov2.weights", "threshold": 0.1}
token = 'rzmkZIv1vWzT7rixNkgJXhVT1HCKnvfi14s30GaRZS8'
tfnet = TFNet(options)
stream = urlopen('http://192.168.50.104:5001/stream')
bytes = bytes()
while True:
    people = []
    bowls = []
    bytes += stream.read(1024)
    a = bytes.find(b'\xff\xd8')
    b = bytes.find(b'\xff\xd9')
    
    if a != -1 and b != -1:
        jpg = bytes[a:b+2]
        bytes = bytes[b+2:]
        i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR) #<class 'numpy.ndarray'> # image decode
        result = tfnet.return_predict(i)
        
        for detection in result:
            if detection['label'] == 'bowl':   
                bowls.append(detection)
                
                cv2.rectangle(i, (detection['topleft']['x'], detection['topleft']['y']), 
                              (detection['bottomright']['x'], detection['bottomright']['y']), 
                              3)
                cv2.putText(i, detection['label'], 
                            (detection['topleft']['x'], detection['topleft']['y'] - 13),
                            
                            cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)

                cv2.putText(i, str(math.floor(detection['confidence']*100)), 
                            (detection['topleft']['x'], detection['topleft']['y'] + 13),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)	
                bowl=detection['topleft']['x']
                bowl=detection['topleft']['y']
                
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
        myperson = people[0];
        person_top = detection['topleft']['y']
        person_bottom =detection['bottomright']['y']
        person_right =detection['bottomright']['x']
        print("person",str(person_right))
        
        
        for bowl in bowls:
            mybowl_top = bowl['topleft']['y']
            mybowl_left = bowl['topleft']['x']
            print("bowl",str(mybowl_left))
            
            
            if person_bottom > mybowl_top > person_top:
                currentTime = int(time.strftime('%H'))   
                if 6 <=currentTime< 10:
                    url = 'http://192.168.50.104:5001/image'
                    wget.download(url, 'C:/Users/Chuang/Desktop/darkflow/fall/fall'+str(x+y+currentTime)+'.jpeg')  #路徑要取代
                    file = {'imageFile': open('C:/Users/Chuang/Desktop/darkflow/fall/fall'+str(x+y+currentTime)+'.jpeg', 'rb') } #路徑要取代
                    param = {
                            'message':'家中老人可能在用早餐\n'+'請利用居家環境監控確認狀況\n'+'http://192.168.50.104:5001/stream' #文字訊息
                            }
                    headers = {
                            "Authorization": "Bearer " + token, 
                            }
                    session = requests.Session()
                    r = session.post("https://notify-api.line.me/api/notify", params=param, headers = headers, files = file)
                if 10 <currentTime< 14:
                    url = 'http://192.168.50.104:5001/image'
                    wget.download(url, 'C:/Users/Chuang/Desktop/darkflow/fall/fall'+str(x+y+currentTime)+'.jpeg')  #路徑要取代
                    file = {'imageFile': open('C:/Users/Chuang/Desktop/darkflow/fall/fall'+str(x+y+currentTime)+'.jpeg', 'rb') } #路徑要取代
                    param = {
                            'message':'家中老人可能在用午餐\n'+'請利用居家環境監控確認狀況\n'+'http://192.168.50.104:5001/stream' #文字訊息
                            }
                    headers = {
                            "Authorization": "Bearer " + token, 
                            }
                    session = requests.Session()
                    r = session.post("https://notify-api.line.me/api/notify", params=param, headers = headers, files = file)
                if 17 <currentTime< 20:
                    url = 'http://192.168.50.104:5001/image'
                    wget.download(url, 'C:/Users/Chuang/Desktop/darkflow/fall/fall'+str(x+y+currentTime)+'.jpeg')  #路徑要取代
                    file = {'imageFile': open('C:/Users/Chuang/Desktop/darkflow/fall/fall'+str(x+y+currentTime)+'.jpeg', 'rb') } #路徑要取代
                    param = {
                            'message':'家中老人可能在用晚餐\n'+'請利用居家環境監控確認狀況\n'+'http://192.168.50.104:5001/stream' #文字訊息
                            }
                    headers = {
                            "Authorization": "Bearer " + token, 
                            }
                    session = requests.Session()
                    r = session.post("https://notify-api.line.me/api/notify", params=param, headers = headers, files = file)
        
       
                    
        
        cv2.imshow('care&match cam', i)
        
        if cv2.waitKey(1) == 27:
            
            exit(0)