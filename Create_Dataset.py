import cv2
""" Cai nay de tao dataset huan luyen mo hinh"""
"""Tac gia: Khanh dep trai"""
vd=cv2.VideoCapture(0)
vd.set(3,640)
vd.set(4,480)
nhan_dien_dep_trai=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
Face_ID=input("\nNhap ID cho dataset: ")
count=0
while True:
    ret, anh=vd.read()
    anh=cv2.flip(anh, 1)
    make_gray=cv2.cvtColor(anh, cv2.COLOR_BGR2GRAY)
    chup_dep_trai=nhan_dien_dep_trai.detectMultiScale(make_gray, 1.3, 5)
    for(cao, to, den, hoi) in chup_dep_trai:
        cv2.rectangle(anh, (cao,to), (cao+to,den+hoi),(220,20,60),2)
        count+=1
        cv2.imwrite('dataset/Khanh.'+str(Face_ID)+'.'+str(count)+'.jpg',make_gray[to:to+hoi,cao:cao+den])
        cv2.imshow('image', anh)
    k=cv2.waitKey(100)&0xff
    if k==27:
        break
    elif count>=300:
        break
vd.release()
cv2.destroyAllWindows()
