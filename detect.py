import cv2

distanceCutoff = 150
cars_cascade = cv2.CascadeClassifier('cars.xml')

def detect_cars_and_pedestrain(frame):
    cars = cars_cascade.detectMultiScale(frame, 1.15, 4)

    close = False
    for (x, y, w, h) in cars:
        
        #cv2.rectangle(frame, (x, y), (x+w, y+h), color=(0, 255, 0), thickness=2)
        if y > distanceCutoff:
            close = True
            cv2.rectangle(frame, (x+1, y+1), (x+w,y+h), color=(255,0,255), thickness=5)
        else:
            cv2.rectangle(frame, (x+1, y+1), (x+w,y+h), color=(275,7,75), thickness=2)

    return frame, close