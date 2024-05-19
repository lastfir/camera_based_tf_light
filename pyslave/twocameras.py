import cv2
import pandas as pd
from ultralytics import YOLO
import os
import time
import math

model = YOLO('best.pt')

cap1 = cv2.VideoCapture('try.mp4')
cap2 = cv2.VideoCapture(0)  # Assuming the second camera is index 2

class_list = ['Car', 'Jeep', 'Motorcycle', 'Tricycle', 'Truck']
start_time = time.time()
count = 0
total_up_count = 0
total_up_countf2 = 0
off = total_up_count

cy1 = 222
cy2 = 268
offset = 10

class Tracker:
    def __init__(self):
        self.center_points = {}
        self.id_count = 0

    def update(self, objects_rect):
        objects_bbs_ids = []
        for rect in objects_rect:
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2
            same_object_detected = False
            for id, pt in self.center_points.items():
                dist = math.hypot(cx - pt[0], cy - pt[1])
                if dist < 35:
                    self.center_points[id] = (cx, cy)
                    objects_bbs_ids.append((x, y, w, h, id))
                    same_object_detected = True
                    break
            if not same_object_detected:
                self.center_points[self.id_count] = (cx, cy)
                objects_bbs_ids.append((x, y, w, h, self.id_count))
                self.id_count += 1
        new_center_points = {}
        for obj_bb_id in objects_bbs_ids:
            _, _, _, _, object_id = obj_bb_id
            center = self.center_points[object_id]
            new_center_points[object_id] = center
        self.center_points = new_center_points.copy()
        return objects_bbs_ids

tracker1 = Tracker()
tracker2 = Tracker()

vh_down1 = {}
UP1 = []
vh_up1 = {}
DOWN1 = []

vh_down2 = {}
f2out = []
vh_up2 = {}
f2in = []

while True:
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()

    if not ret1 or not ret2:
        print("Error: Unable to capture video")
        break

    count += 1
    if count % 3 != 0:
        continue

    frame1 = cv2.resize(frame1, (550, 450))
    frame2 = cv2.resize(frame2, (550, 450))

    results1 = model.predict(frame1, verbose=False)
    results2 = model.predict(frame2, verbose=False)

    # Process results for camera 1
    a1 = results1[0].boxes.data
    px1 = pd.DataFrame(a1).astype("float")
    list1 = []

    for index, row in px1.iterrows():
        x1 = int(row[0])
        y1 = int(row[1])
        x2 = int(row[2])
        y2 = int(row[3])
        d = int(row[5])
        c = class_list[d]
        list1.append([x1, y1, x2, y2])
        if c in class_list:  # Check if the detected class is in the target classes
            cv2.rectangle(frame1, (x1, y1), (x2, y2), (0, 255, 0), 1)
            cv2.putText(frame1, str(c), (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 244), 1)

    bbox_id1 = tracker1.update(list1)

    for bbox in bbox_id1:
        x3, y3, x4, y4, id1 = bbox
        cx = int(x3 + x4) // 2
        cy = int(y3 + y4) // 2
        if cy2 < (cy + offset) and cy2 > (cy - offset):
            vh_down1[id1] = cy
        if id1 in vh_down1:
            if cy1 < (cy + offset) and cy1 > (cy - offset):
                cv2.circle(frame1, (cx, cy), 4, (0, 0, 255), -1)
                cv2.putText(frame1, str(id1), (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
                if f2in and DOWN1.count(id1) == 0:
                    DOWN1.append(id1)
                    total_up_countf2 -= 1

        if cy1 < (cy + offset) and cy1 > (cy - offset):
            vh_up1[id1] = cy
        if id1 in vh_up1:
            if cy2 < (cy + offset) and cy2 > (cy - offset):
                cv2.circle(frame1, (cx, cy), 4, (0, 0, 255), -1)
                cv2.putText(frame1, str(id1), (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
                if total_up_countf2 == 0 and UP1.count(id1) == 0:
                    UP1.append(id1)
                    total_up_count += 1

    downcount1 = len(DOWN1)
    upcount1 = len(UP1)

    cv2.line(frame1, (10, cy1), (500, cy1), (0, 0, 255), 1)
    cv2.putText(frame1, "Out frame1", (244, 314), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame1, "Out count frame1: " + str(downcount1), (60, 80), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 0), 2)

    cv2.line(frame1, (10, cy2), (500, cy2), (0, 255, 0), 1)
    cv2.putText(frame1, "In frame1", (181, 363), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0), 2)
    cv2.putText(frame1, "In count frame1: " + str(total_up_count), (60, 40), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 0), 2)

    # Process results for camera 2
    a2 = results2[0].boxes.data
    px2 = pd.DataFrame(a2).astype("float")
    list2 = []

    for index, row in px2.iterrows():
        x1 = int(row[0])
        y1 = int(row[1])
        x2 = int(row[2])
        y2 = int(row[3])
        d = int(row[5])
        c = class_list[d]
        list2.append([x1, y1, x2, y2])
        if c in class_list:  # Check if the detected class is in the target classes
            cv2.rectangle(frame2, (x1, y1), (x2, y2), (0, 255, 0), 1)
            cv2.putText(frame2, str(c), (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)

    bbox_id2 = tracker2.update(list2)
    for bbox in bbox_id2:
        x3, y3, x4, y4, id2 = bbox
        cx = int(x3 + x4) // 2
        cy = int(y3 + y4) // 2
        if cy1 < (cy + offset) and cy1 > (cy - offset):
            vh_down2[id2] = cy
        if id2 in vh_down2:
            if cy2 < (cy + offset) and cy2 > (cy - offset):
                cv2.circle(frame2, (cx, cy), 4, (0, 0, 255), -1)
                cv2.putText(frame2, str(id2), (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
                if UP1 and f2out.count(id2) == 0:
                    f2out.append(id2)
                    total_up_count -= 1

        if cy2 < (cy + offset) and cy2 > (cy - offset):
            vh_up2[id2] = cy
        if id2 in vh_up2:
            if cy1 < (cy + offset) and cy1 > (cy - offset):
                cv2.circle(frame2, (cx, cy), 4, (0, 0, 255), -1)
                cv2.putText(frame2, str(id2), (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
                if total_up_count == 0 and f2in.count(id2) == 0:
                    f2in.append(id2)
                    total_up_countf2 += 1

    frame2in = len(f2in)
    frame2out = len(f2out)

    cv2.line(frame2, (10, cy1), (500, cy1), (0, 255, 0), 1)
    cv2.putText(frame2, "Out frame2", (181, 363), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0), 2)
    cv2.putText(frame2, "Out count frame2: " + str(frame2out), (60, 80), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 0), 2)

    cv2.line(frame2, (10, cy2), (500, cy2), (0, 0, 255), 1)
    cv2.putText(frame2, "In frame2", (274, 314), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame2, "In count frame2: " + str(total_up_countf2), (60, 40), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 0), 2)

    # Display frames from both cameras
    end_time = time.time()
    elapsed_time = end_time - start_time
    fps = count / elapsed_time
    cv2.putText(frame1, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame2, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("FRAME1", frame1)
    cv2.imshow("FRAME2", frame2)

    if cv2.waitKey(1) & 0xFF == 27:
        break


cap1.release()
cap2.release()
cv2.destroyAllWindows()

