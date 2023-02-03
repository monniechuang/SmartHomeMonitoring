# -*- coding: utf-8 -*-

from darkflow.net.build import TFNet
import cv2

from datetime import datetime
from io import BytesIO
import time
import requests
from PIL import Image, ImageDraw
import numpy as np
import threading
import queue


options = {"model": "cfg/yolo.cfg", "load": "bin/yolov2.weights", "threshold": 0.4}
tfnet = TFNet(options)
token = 'rzmkZIv1vWzT7rixNkgJXhVT1HCKnvfi14s30GaRZS'
onePerson_record = round(time.time()) 

def lineNotify(token, msg, camID):
    headers = {
            "Authorization": "Bearer " + token, 
            }
    url = "C:/Users/Chuang/Desktop/darkflow/people/people"+str(camID)+".jpg"
    imageFile = {'imageFile': open(url, 'rb')}
    payload = {'message': msg}
    try:
        session = requests.Session()
        r = session.post("https://notify-api.line.me/api/notify", headers = headers, params = payload, files=imageFile, timeout=3)
        return r.content
    except:
        return None

def getPeopleCount(url, cam_id):
    global onePerson_record
    
    try:
        r = requests.get(url, timeout=5)
        curr_img = Image.open(BytesIO(r.content))
        curr_img_cv2 = cv2.cvtColor(np.array(curr_img), cv2.COLOR_RGB2BGR)
        result = tfnet.return_predict(curr_img_cv2)
        draw = ImageDraw.Draw(curr_img)

        peopleSeen = 0
        for detection in result:

            if detection['label'] == 'person':
                
                peopleSeen += 1
                draw.rectangle([detection['topleft']['x'], detection['topleft']['y'], 
                        detection['bottomright']['x'], detection['bottomright']['y']],
                        outline=(255, 0, 0))
                draw.text([detection['topleft']['x'], detection['topleft']['y'] - 13], detection['label'], fill=(255, 0, 0))

        
        accumulatedTime = round(time.time()) - onePerson_record 
        
        if peopleSeen == 1 and accumulatedTime > 6:
            curr_img.save('people/people%d.jpg' %(cam_id))
            
            message = "家中老人一個人獨處的時間超過1分鐘\n"+'請利用居家環境監控確認狀況\n'+'http://192.168.50.104:5001/stream'
            print(lineNotify(token, message, cam_id))
            
            print("一個人獨處的時間超過1分鐘")
            time.sleep(1)
        elif peopleSeen >= 2:
            onePerson_record = round(time.time())
           
        
        return peopleSeen

    except:
        print("camID:", cam_id, " timeout.")
        return -1
            
       

while True:
    que = queue.Queue();    
    thread_list = list();
    
    cam_1 = threading.Thread(target=lambda q, arg1, arg2: q.put(getPeopleCount(arg1, arg2)), args=(que, 'http://192.168.50.104:5001/image', 1))

    cam_1.start()
    thread_list.append(cam_1);
    
    for t in thread_list:
        t.join()
    
    if que.qsize() == 1:
        cam1_count = que.get()
    else:
        print("queue error")  
    print('running again')
    time.sleep(5)
    

	



