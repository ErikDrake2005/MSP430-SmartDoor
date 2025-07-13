import cv2
import numpy as np
from PIL import Image
import os

duong_dan_dataset = 'dataset'
DTT = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
RCN = cv2.face.LBPHFaceRecognizer_create()

def soanDuLieu(duong_dan):
    Mau = []
    IDs = []
    for file in os.listdir(duong_dan):
        if not file.lower().endswith(('.jpg', '.png', '.jpeg')):
            continue
        path_img = os.path.join(duong_dan, file)
        img_pil = Image.open(path_img).convert('L')
        img_np  = np.array(img_pil, dtype='uint8')
        face_id = int(file.split('.')[1])
        faces = DTT.detectMultiScale(img_np)
        for x, y, w, h in faces:
            roi = img_np[y:y+h, x:x+w]
            Mau.append(roi)
            IDs.append(face_id)

    return Mau, IDs

print('Đang huấn luyện...')
MAT, IDs = soanDuLieu(duong_dan_dataset)
RCN.train(MAT, np.array(IDs))
RCN.write('mohinh/nhan_dien_mat.yml')
print('Xong')

