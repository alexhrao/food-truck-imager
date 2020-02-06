from google.cloud import storage
from datetime import datetime
from cv2 import cv2

def upload_coc(img_filename):
    storage_client = storage.Client()
    bucket = storage_client.bucket('cocfoodtrucks')
    img_name = datetime.now().isoformat().replace('-', '_').replace(':', '_').replace('.', '_')
    blob = bucket.blob(img_name)
    blob.upload_from_filename(img_filename)

if __name__=="__main__":
    cam = cv2.VideoCapture(1)
    ret, frame = cam.read()
    cv2.imwrite('C:/Users/alexhrao/tmp.png', frame)
    upload_coc('C:/Users/alexhrao/tmp.png')
    cam.release()
    cv2.destroyAllWindows()