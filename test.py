import serial
from guizero import App, Window, TextBox, PushButton
import time
from SCAN import nhan_dien_khuon_mat as NDKM

ser = serial.Serial('COM4', 9600, timeout=1)

def receive():
    try:
        byte_received = ser.read(1)
        return byte_received.decode('ascii') if byte_received else None
    except (UnicodeDecodeError, serial.SerialException) as e:
        print(f"Lỗi giao tiếp: {e}")
        return None

def doi_mk(pw):
    if len(pw) == 4 and pw.isdigit():
        with open('pass.txt', 'w') as mk:
            mk.write(pw)
        ser.write(b'D')
        print("Đã đổi mật khẩu mới là:", pw)

def check(face_result, password):
    if face_result:
        return True
    else:
        with open('pass.txt') as mk:
            stored_pass = mk.readline().strip()
            return password == stored_pass if password else False

def reset():
    global program_stt, data_pass
    program_stt = 0
    data_pass = ''
    ser.write(b'C')
    print("Đã reset trạng thái")


def GUI():
    app = App(title="Đồ Án Vi Điều Khiển Khanh + Toàn", layout="grid", width=190, height=60)
    result = [None]
    face_result = [False]

    def open_password_window():
        password = input_password(title="Nhập Mật Khẩu", send_to_msp430=True)
        if password:
            result[0] = password
            app.destroy()

    def face_id_action():
        print("Face_ID được chọn")
        face_result[0] = NDKM()
        app.destroy()

    PushButton(app, text="PASSWORD", command=open_password_window, grid=[0, 1], width=10, height=2)
    PushButton(app, text="FACE_ID", command=face_id_action, grid=[1, 1], width=10, height=2)
    app.display()

    if face_result[0]:
        return check(True, None)
    elif result[0] is not None:
        return check(False, result[0])
    else:
        return False

def input_password(title="Nhập Mật Khẩu", send_to_msp430=True):
    result = [None]
    app = App(title=title, layout="grid", width=190, height=260)
    textbox = TextBox(app, grid=[0, 0, 3, 1], width=10)
    textbox.text_size = 14
    textbox.focus()

    def set_number(number):
        current_text = textbox.value
        if len(current_text) < 4:
            textbox.value = current_text + number
            if send_to_msp430:
                ser.write(number.encode())
            if len(textbox.value) == 4:
                result[0] = textbox.value
                app.after(100, app.destroy)

    def on_closing():
        result[0] = None
        app.destroy()

    PushButton(app, text="1", command=set_number, args=["1"], grid=[0, 1], width=5, height=2)
    PushButton(app, text="2", command=set_number, args=["2"], grid=[1, 1], width=5, height=2)
    PushButton(app, text="3", command=set_number, args=["3"], grid=[2, 1], width=5, height=2)
    PushButton(app, text="4", command=set_number, args=["4"], grid=[0, 2], width=5, height=2)
    PushButton(app, text="5", command=set_number, args=["5"], grid=[1, 2], width=5, height=2)
    PushButton(app, text="6", command=set_number, args=["6"], grid=[2, 2], width=5, height=2)
    PushButton(app, text="7", command=set_number, args=["7"], grid=[0, 3], width=5, height=2)
    PushButton(app, text="8", command=set_number, args=["8"], grid=[1, 3], width=5, height=2)
    PushButton(app, text="9", command=set_number, args=["9"], grid=[2, 3], width=5, height=2)
    PushButton(app, text="0", command=set_number, args=["0"], grid=[0, 4, 3, 1], width=23, height=2, align="center")

    app.tk.protocol("WM_DELETE_WINDOW", on_closing)
    app.display()
    return result[0]

while True:
    reset()
    try:
        if program_stt == 0:
            xac_minh = GUI()
            if xac_minh:
                program_stt = 1
                ser.write(b'T')
            else:
                ser.write(b'F')
        elif program_stt == 1:
            start_time = time.time()
            while time.time() - start_time < 10:
                if receive() == 'O':
                    print('Đã mở cửa')
                    break
            else:
                print("Hết thời gian chờ 'O'")
                reset()
                continue
            start_time = time.time()
            while time.time() - start_time < 40:
                fromMSP430 = receive()
                if fromMSP430 == 'C':
                    print('Đã đóng cửa')
                    ser.write(b'C')
                    break
                elif fromMSP430 == 'N':
                    print('Yêu cầu đổi mật khẩu từ MSP430')
                    new_pw = input_password(title="Nhập Mật Khẩu Mới", send_to_msp430=False)
                    if new_pw:
                        doi_mk(new_pw)
            else:
                print("Hết thời gian chờ 'C' hoặc 'N'")
                reset()
                continue
            start_time = time.time()
            while time.time() - start_time < 10:
                if receive() == 'E':
                    print("Nhận 'E', reset hệ thống")
                    reset()
                    break
            else:
                print("Hết thời gian chờ 'E'")
                reset()
    except KeyboardInterrupt:
        print("Chương trình dừng bởi người dùng")
        ser.close()
        break
    except Exception as e:
        print(f"Lỗi không mong muốn: {e}")