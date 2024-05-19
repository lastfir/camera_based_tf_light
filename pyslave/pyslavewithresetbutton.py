import cv2
import pandas as pd
from ultralytics import YOLO
from tracker import *
import serial
import time

# Set up the serial connection (adjust the port name as needed)
ser = serial.Serial('COM11', 9600)
time.sleep(2)  # Wait for the connection to initialize

def send_command(command):
    ser.write(command.upper().encode() + b'\n')  # Send the command to the Arduino in uppercase

def ledseq1():
    send_command('SEQ1')

def ledseq2():
    send_command('SEQ2')

def idle():
    send_command('IDLE')

def ledoff():
    send_command('OFF')

def reset_counts():
    global total_up_count, total_up_countf2
    total_up_count = 0
    total_up_countf2 = 0
    idle()

# Initialize total counts
total_up_count = 0
total_up_countf2 = 0

# Load the YOLO model
model = YOLO('best.pt')

# Open video captures
cap1 = cv2.VideoCapture('in2d.mp4')
cap2 = cv2.VideoCapture('out2d.mp4')  # Assuming the second camera is index 1

# Define the class list
class_list = ['Car', 'Jeep', 'Motorcycle', 'Tricycle', 'Truck']
count = 0

# Initialize the trackers
tracker1 = Tracker()
tracker2 = Tracker()

# Define the lines for counting
line1 = 322
line2 = 368
offset = 10

# Initialize vehicle dictionaries and counts
vh_out1 = {}
in_count_f1 = []
vh_in1 = {}
out_count_f1 = []

vh_out2 = {}
out_count_f2 = []
vh_in2 = []
in_count_f2 = []

while True:
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()
    
    if not ret1 or not ret2:
        break
    
    count += 1
    if count % 3 != 0:
        continue
    
    frame1 = cv2.resize(frame1, (640, 450))
    frame2 = cv2.resize(frame2, (640, 450))

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
    bbox_id1 = tracker1.update(list1)
        
    for bbox in bbox_id1:
        x3, y3, x4, y4, id1 = bbox
        cx = int(x3 + x4) // 2
        cy = int(y3 + y4) // 2
        if line2 < (cy + offset) and line2 > (cy - offset):
            vh_out1[id1] = cy
        if id1 in vh_out1:
            if line1 < (cy + offset) and line1 > (cy - offset):
                cv2.circle(frame1, (cx, cy), 4, (0, 0, 255), -1)
                cv2.putText(frame1, str(id1), (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
                if in_count_f2 and out_count_f1.count(id1) == 0:
                    out_count_f1.append(id1)
                    total_up_countf2 -= 1

        if line1 < (cy + offset) and line1 > (cy - offset):
            vh_in1[id1] = cy
        if id1 in vh_in1:
            if line2 < (cy + offset) and line2 > (cy - offset):
                cv2.circle(frame1, (cx, cy), 4, (0, 0, 255), -1)
                cv2.putText(frame1, str(id1), (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
                if in_count_f1.count(id1) == 0 and out_count_f2.count(id1) == 0:
                    in_count_f1.append(id1)
                    total_up_countf2 += 1

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
    bbox_id2 = tracker2.update(list2)
        
    for bbox in bbox_id2:
        x3, y3, x4, y4, id2 = bbox
        cx = int(x3 + x4) // 2
        cy = int(y3 + y4) // 2
        if line2 < (cy + offset) and line2 > (cy - offset):
            vh_out2[id2] = cy
        if id2 in vh_out2:
            if line1 < (cy + offset) and line1 > (cy - offset):
                cv2.circle(frame2, (cx, cy), 4, (0, 0, 255), -1)
                cv2.putText(frame2, str(id2), (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
                if in_count_f1 and out_count_f2.count(id2) == 0:
                    out_count_f2.append(id2)
                    total_up_count -= 1

        if line1 < (cy + offset) and line1 > (cy - offset):
            vh_in2[id2] = cy
        if id2 in vh_in2:
            if line2 < (cy + offset) and line2 > (cy - offset):
                cv2.circle(frame2, (cx, cy), 4, (0, 0, 255), -1)
                cv2.putText(frame2, str(id2), (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
                if in_count_f2.count(id2) == 0 and out_count_f1.count(id2) == 0:
                    in_count_f2.append(id2)
                    total_up_count += 1

    # Display counts on frames
    cv2.putText(frame1, "Status", (50, 30), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(frame1, "Vehicle passed 1: " + str(total_up_countf2), (50, 60), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
    cv2.putText(frame2, "Status", (50, 30), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(frame2, "Vehicle passed 2: " + str(total_up_count), (50, 60), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)

    # Show frames
    cv2.imshow("RGB", frame1)
    cv2.imshow("Depth", frame2)

    # Check for reset command from Arduino
    if ser.in_waiting > 0:
        arduino_command = ser.readline().decode().strip()
        if arduino_command == "RESET":
            reset_counts()

    # Check for key press to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video captures and close windows
cap1.release()
cap2.release()
cv2.destroyAllWindows()
ser.close()
