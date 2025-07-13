import cv2
def nhan_dien_khuon_mat():
    RCN = cv2.face.LBPHFaceRecognizer_create()
    RCN.read('mohinh/nhan_dien_mat.yml')
    FaceCASC = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    EyeCASC = cv2.CascadeClassifier('haarcascade_eye.xml')
    fort = cv2.FONT_HERSHEY_SIMPLEX
    name_tag = ['Khanh', 'Toan', 'None']
    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)
    minTO = 0.1 * cam.get(3)
    minCAO = 0.1 * cam.get(4)
    thong_ke_do_chinh_xac = []
    for _ in range(100):
        ret, anh = cam.read()
        if not ret:
            continue
        anh = cv2.flip(anh, 1)
        make_gray = cv2.cvtColor(anh, cv2.COLOR_BGR2GRAY)
        nhung_khuong_mat = FaceCASC.detectMultiScale(make_gray, 1.3, 5, minSize=(int(minTO), int(minCAO)))
        for (x, y, w, h) in nhung_khuong_mat:
            cv2.rectangle(anh, (x, y), (x + w, y + h), (0, 206, 209), 2)
            roi_gray = make_gray[y:y + h, x:x + w]
            roi_color = anh[y:y + h, x:x + w]
            mat = EyeCASC.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in mat:
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (255, 0, 0), 2)
            id, confidence = RCN.predict(roi_gray)
            if confidence < 100:
                id = name_tag[id]
                confidence = 100 - confidence
            else:
                id = "none"
                confidence = 100 - confidence
            thong_ke_do_chinh_xac.append(confidence)
            cv2.putText(anh, str(id), (x + 5, y + h - 5), fort, 1, (255, 255, 255), 1)
        cv2.imshow('DO AN VI DIEU KHIEN KHANH+TOAN', anh)
        cv2.waitKey(1)
    cam.release()
    cv2.destroyAllWindows()
    if thong_ke_do_chinh_xac:
        do_chinh_xac_trung_binh = sum(thong_ke_do_chinh_xac) / len(thong_ke_do_chinh_xac)
        return do_chinh_xac_trung_binh > 60
    return False
if __name__ == "__main__":
    ket_qua = nhan_dien_khuon_mat()
    print(f"Kết quả nhận diện: {'True' if ket_qua else 'False'}")