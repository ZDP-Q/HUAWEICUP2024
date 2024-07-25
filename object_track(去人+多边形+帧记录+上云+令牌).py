# -*- coding: utf-8 -*-
import cv2
import numpy as np
from Upload2Cloud import send_json_to_url,send_delete_to_url
from ultralytics import YOLO
from detect_region import DetectionRegion
from dict import class_names
from GetToken import TokenServer

import time
import threading
from GetToken import TokenServer
from myStatic import  MyClass

def http_get_token():
    port = 8880
    server = TokenServer(port)
    server.start_server()
baseurl = "http://10.161.148.203:8881"
#baseurl = "http://10.161.148.203:8881/Unrestricted/cin"
# 创建线程
thread = threading.Thread(target=http_get_token)
# 启动线程
thread.start()

while 1 > 0:
    time.sleep(0.05)
    print(f"Received token: {MyClass.get_class_var()}")
    if MyClass.get_class_var()!=0:
        break

# 加载YOLOv8模型
model = YOLO("yolov8x.pt")
model.conf = 0.3

#video_path = "track1.mp4"
#cap = cv2.VideoCapture(video_path)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("摄像头无法打开")



# 设置分辨率
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

DetectRegion = DetectionRegion()
DetectRegion.set_points(250,200)
DetectRegion.set_points(250,600)
DetectRegion.set_points(900,200)
DetectRegion.set_points(900,600)

object_list = []  # 种类列表
id_array=[]       # id列表
last_frame_array=[]
while cap.isOpened():
    success, frame = cap.read()

    if success:
        # Run YOLOv8 tracking on the frame, persisting tracks between frames
        results = model.track(frame, persist=True)
        for track in results:
            xywh = track.boxes.xywh# 获取边界框坐标
            num = xywh.shape[0]#框的数量-int
            cls = track.boxes.cls# 获取类别索引
            id = track.boxes.id#获取目标id
            conf = track.boxes.conf  # 获取置信度
            if id is not None:
                id_cls_centerpoints = []
                for i in range(num):
                    id_cls_centerpoint=(int(id[i].item()), int(cls[i].item()), int(xywh[i,0].item()), int(xywh[i,1].item()))# id,类别,x,y
                    id_cls_centerpoints.append(id_cls_centerpoint)
            else:
                num = 0

        annotated_frame = results[0].plot()
        cv2.line(annotated_frame, (250,200), (250,600),  (0, 255, 0), thickness=1)
        cv2.line(annotated_frame, (250,200), (900,200), (0, 255, 0), thickness=1)
        cv2.line(annotated_frame, (900,600), (250,600), (0, 255, 0), thickness=1)
        cv2.line(annotated_frame, (900,600), (900,200), (0, 255, 0), thickness=1)

        for i in range(num):
            cv2.circle(annotated_frame, (id_cls_centerpoints[i][2],id_cls_centerpoints[i][3]), 5, (0, 0, 255), -1)

            if(DetectRegion.is_point_inside((id_cls_centerpoints[i][2],id_cls_centerpoints[i][3]))):
                is_inside = 1
            else:
                is_inside = -1

            # print(len(last_frame_array)," ",i,"/",num)
            for m in range(len(last_frame_array)):
                #print("idcls:",id_cls_centerpoints[i])
                #print("lastt_frame:",last_frame_array[m])
                if id_cls_centerpoints[i][0] == last_frame_array[m][0]: #这一帧和上一帧存在相同id
                    # print(last_frame_array[m][2],is_inside)
                    if last_frame_array[m][2] == -1 and is_inside == 1: #添加移入项
                        add_new_object = True
                        for j in range(len(object_list)):
                            object = object_list[j]
                            if object == id_cls_centerpoints[i][1] and id_cls_centerpoints[i][1] != 0:
                                col_index = object_list.index(object)
                                # 如果名字已存在，检查 ID 是否已存在
                                if id_cls_centerpoints[i][0] not in id_array[col_index]:
                                    id_array[col_index].append(id_cls_centerpoints[i][0])
                                    json_data = {
                                        'token': MyClass.get_class_var(),
                                        'message': class_names[id_cls_centerpoints[i][1]],
                                        'id': id_cls_centerpoints[i][0]
                                    }
                                    add_url = '/common/input'
                                    send_json_to_url(json_data, MyClass.get_class_var(), url=baseurl + add_url)
                                add_new_object = False
                                break

                        if id_cls_centerpoints[i][1] == 0:
                            add_new_object=False

                        if add_new_object:
                            object_list.append(id_cls_centerpoints[i][1])
                            id_array.append([id_cls_centerpoints[i][0]])
                            json_data = {
                                'token': MyClass.get_class_var(),
                                'message': class_names[id_cls_centerpoints[i][1]],
                                'id': id_cls_centerpoints[i][0]
                            }
                            add_url='/common/input'
                            send_json_to_url(json_data,MyClass.get_class_var(),url=baseurl+add_url)
                    elif last_frame_array[m][2] == 1 and is_inside == -1: #删除移出项
                        delete_new_object = True
                        for j in range(len(object_list)):
                            if id_cls_centerpoints[i][1] == object_list[j]:
                                for n in range(len(id_array[j])):
                                    if id_cls_centerpoints[i][0] == id_array[j][n]:
                                        del id_array[j][n]
                                        delete_url = '/common/output/'
                                        send_delete_to_url(MyClass.get_class_var(), url=baseurl+delete_url+str(id_cls_centerpoints[i][0]))
                                        break
                                if len(id_array[j]) == 0:  # 如果类别下没有任何id，则删除这个类
                                    del object_list[j]
                                    del id_array[j]
                                    break

            add_new_frame = True
            for m in range(len(last_frame_array)):
                if id_cls_centerpoints[i][0] == last_frame_array[m][0]:
                    add_new_frame = False
                    print(last_frame_array)
                    last_frame_array_np = np.array(last_frame_array, dtype=int)
                    last_frame_array_np[m][2] = is_inside
                    last_frame_array.clear()
                    last_frame_array = last_frame_array_np.tolist()

            if add_new_frame:
                part_frame = (id_cls_centerpoints[i][0], id_cls_centerpoints[i][1], is_inside)
                last_frame_array.append(part_frame)
                print("new part frame", part_frame)

        print("last:", last_frame_array)
        print(object_list)

        y_index=30
        for i in range(len(object_list)):
            name=class_names[object_list[i]]
            id_str = ' '.join(str(id) for id in id_array[i])
            text = f"{name}: {id_str}"
            cv2.putText(annotated_frame, text, (10, y_index), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,0), 2)
            y_index += 30
        # Display the annotated frame
        cv2.imshow("YOLOv8 Tracking", annotated_frame)

        print("------------------------------------------------")

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()