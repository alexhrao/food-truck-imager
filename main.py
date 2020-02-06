from google.cloud import storage
from datetime import datetime
from cv2 import cv2
from threading import Timer

cam = cv2.VideoCapture(0)
def upload_coc(img_filename):
    storage_client = storage.Client()
    bucket = storage_client.bucket('cocfoodtrucks')
    img_name = datetime.now().isoformat().replace('-', '_').replace(':', '_').replace('.', '_')
    blob = bucket.blob(img_name)
    blob.upload_from_filename(img_filename)

def take_snapshot():
    if cam is not None and cam.isOpened():
        ret, frame = cam.read()
        cv2.imwrite('./tmp.png', frame)
        upload_coc('./tmp.png')
        Timer(3.0, take_snapshot).start()

if __name__=="__main__":
    Timer(3.0, take_snapshot).start()
    flag = True
    while True:
        print("Press q to quit...", end=" ")
        ctrl = input()
        if (ctrl == 'q'):
            break
    cam.release()
    cv2.destroyAllWindows()
