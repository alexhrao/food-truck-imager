from google.cloud import storage
from datetime import datetime
from cv2 import cv2
from threading import Timer
import json
import sys

def parse_config(config):
    with open(config) as fd:
        conf = json.load(fd)
    return conf

def upload_coc(img_filename, bucket):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket)
    img_name = datetime.now().isoformat().replace('-', '_').replace(':', '_').replace('.', '_')
    blob = bucket.blob(img_name)
    blob.upload_from_filename(img_filename)

def take_snapshot(cam, bucket, interval):
    if cam is not None and cam.isOpened():
        _, frame = cam.read()
        cv2.imwrite('./{0}.png'.format(bucket), frame)
        upload_coc('./{0}.png'.format(bucket), bucket)
        Timer(interval, take_snapshot, args=[cam, bucket, interval]).start()

if __name__=="__main__":
    conf = parse_config(sys.argv[1])
    cams = list()
    tickers = list()
    for c in conf:
        cam = cv2.VideoCapture(c['index'])
        cams.append(cam)
        ticker = Timer(c['interval'], take_snapshot, args=[cam, c['bucket'], c['interval']])
        tickers.append(ticker)
    for ticker in tickers:
        ticker.start()
    while True:
        print("Press q to quit...", end=" ")
        ctrl = input()
        if (ctrl == 'q'):
            break
    for cam in cams:
        cam.release()
    cv2.destroyAllWindows()
