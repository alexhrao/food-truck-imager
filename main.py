from google.cloud import storage, firestore
from datetime import datetime
from cv2 import cv2
from threading import Timer
import json
import sys
import socket
import time

db = firestore.Client()
dt_range = [11, 14]
tickers = list()

def parse_config(location):
    loc_config = db.collection('locations').document(location).get().to_dict()
    out = list()
    for view in loc_config['views']:
        conf = {
            'bucket': view['bucket'],
            'index': view['cameraConfig']['index'],
            'interval': view['cameraConfig']['interval'],
            'transformations': view['cameraConfig']['transformations']
        }
        out.append(conf)
    return out

def upload_coc(img_filename, bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    img_id = datetime.now().isoformat().replace('-', '_').replace(':', '_').replace('.', '_')
    img_name = '{0}.png'.format(img_id)
    blob = bucket.blob(img_name)
    blob.upload_from_filename(img_filename)
    doc_ref = db.collection('images').document(bucket_name)
    doc_ref.update({ 'lastSnapshot.filename': img_name, 'lastSnapshot.updateTime': firestore.SERVER_TIMESTAMP })
    coll_ref = db.collection('images').document(bucket_name).collection('labels')
    doc = coll_ref.document(img_id)
    doc.set({
        'bucket': bucket_name,
        'filename': img_name,
        'labels': [],
        'valid': True,
        'seen': False
    })

def take_snapshot(cam, bucket, config):
    if cam is not None and cam.isOpened():
        _, frame = cam.read()
        for transform in config['transformations']:
            if transform['action'] == 'flip':
                if transform['axis'] == 'x':
                    frame = cv2.flip(frame, 0)
                elif transform['axis'] == 'y':
                    frame = cv2.flip(frame, 1)
                elif transform['axis'] == 'xy':
                    frame = cv2.flip(frame, -1)
            elif transform['action'] == 'rotate':
                if transform['direction'] == 'CW90':
                    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                elif transform['direction'] == 'CCW90':
                    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                elif transform['direction'] == '180':
                    frame = cv2.rotate(frame, cv2.ROTATE_180)
        cv2.imwrite('./{0}.png'.format(bucket), frame)
        upload_coc('./{0}.png'.format(bucket), bucket)
        dt = datetime.now()
        if (dt.hour < dt_range[0]) | (dt.hour > dt_range[1]):
            ticker = Timer(30.0 * 60.0, take_snapshot, args=[cam, bucket, config])
        else:
            ticker = Timer(config['interval'], take_snapshot, args=[cam, bucket, config])
        tickers[config['index']] = ticker
        ticker.start()

if __name__=="__main__":
    conf = parse_config(sys.argv[1])
    cams = list()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            server.bind(('localhost', 10000))
            break
        except OSError as ex:
            time.sleep(1.0)
    for i, c in enumerate(conf):
        cam = cv2.VideoCapture(c['index'])
        cams.append(cam)
        ticker = Timer(c['interval'], take_snapshot, args=[cam, c['bucket'], { 'interval': c['interval'], 'index': i, 'transformations': c['transformations'] }])
        tickers.append(ticker)
    for ticker in tickers:
        ticker.start()
    server.listen(1)
    print('listening for command...')
    conn, cl_addr = server.accept()
    for cam in cams:
        cam.release()
    cv2.destroyAllWindows()
    for ticker in tickers:
        ticker.cancel()
