from flask import Blueprint, render_template, Response, jsonify
from flask_login import login_required
import mysql.connector
import cv2
import time
from datetime import date


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="flask_db"
)

mycursor = mydb.cursor()


home = Blueprint('admin', __name__)

# cap = cv2.VideoCapture(1)
is_camera_on = False

cnt = 0
pause_cnt = 0
justscanned = False


def face_recognition():  # generate frame by frame from camera
    def draw_boundary(img, classifier, scaleFactor, minNeighbors, color, text, clf):
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        features = classifier.detectMultiScale(gray_image, scaleFactor, minNeighbors)

        global justscanned
        global pause_cnt

        pause_cnt += 1

        coords = []

        for (x, y, w, h) in features:
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            id, pred = clf.predict(gray_image[y:y + h, x:x + w])
            confidence = int(100 * (1 - pred / 300))

            if confidence > 80 and not justscanned:
                global cnt
                cnt += 1

                n = (100 / 30) * cnt
                # w_filled = (n / 100) * w
                w_filled = (cnt / 30) * w

                cv2.putText(img, str(int(n))+' %', (x + 20, y + h + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (153, 255, 255), 2, cv2.LINE_AA)

                cv2.rectangle(img, (x, y + h + 40), (x + w, y + h + 50), color, 2)
                cv2.rectangle(img, (x, y + h + 40), (x + int(w_filled), y + h + 50), (153, 255, 255), cv2.FILLED)

                mycursor.execute("select a.img_person, b.username, b.email "
                                "  from images a "
                                "  left join users b on a.img_person = b.id "
                                " where img_id = " + str(id))
                row = mycursor.fetchone()
                pnbr = row[0]
                pname = row[1]  
                pskill = row[2]

                if int(cnt) == 30:
                    cnt = 0

                    mycursor.execute("insert into attendance (accs_date, accs_prsn) values('"+str(date.today())+"', '" + pnbr + "')")
                    mydb.commit()

                    cv2.putText(img, pname + ' | ' + pskill, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (153, 255, 255), 2, cv2.LINE_AA)
                    time.sleep(1)

                    justscanned = True
                    pause_cnt = 0

            else:
                if not justscanned:
                    cv2.putText(img, 'UNKNOWN', (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
                else:
                    cv2.putText(img, ' ', (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2,cv2.LINE_AA)

                if pause_cnt > 80:
                    justscanned = False

            coords = [x, y, w, h]
        return coords

    def recognize(img, clf, faceCascade):
        coords = draw_boundary(img, faceCascade, 1.1, 10, (255, 255, 0), "Face", clf)
        return img

    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.read("classifier.xml")

    wCam, hCam = 400, 400

    cap = cv2.VideoCapture(1)
    cap.set(3, wCam)
    cap.set(4, hCam)

    # while True:
    while True:
        ret, img = cap.read()
        img = recognize(img, clf, faceCascade)

        frame = cv2.imencode('.jpg', img)[1].tobytes()
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

        key = cv2.waitKey(1)
        if key == 27:
            break

@home.route('/admin')
@login_required
def index():
    users = mycursor.execute("select *"
                    "from users"
                    " where users.id != 101 "
                    " order by 1 desc")
    
    users = mycursor.fetchall()
    
    attendance = mycursor.execute("select count(*)"
                    " from attendance "
                    " order by 1 desc")
    
    row = mycursor.fetchone()
    attendance = row[0]
    
    today_attendance = mycursor.execute("select count(*)"
                    " from attendance "
                    " where accs_date = curdate() "
                    " order by 1 desc")
    row = mycursor.fetchone()
    today_attendance = row[0]

    return render_template('admin/index.html', users=users, attendance=attendance, today_attendance=today_attendance)

@home.route('/attendance')
@login_required
def fr_page():
    mycursor.execute("select a.accs_id, a.accs_prsn, b.username, b.email, a.accs_added "
                    "  from attendance a "
                    "  left join users b on a.accs_prsn = b.id "
                    " where a.accs_date = curdate() "
                    " order by 1 desc")
    data = mycursor.fetchall()

    return render_template('admin/fr_page.html', data=data)

@home.route('/video_feed')
@login_required
def video_feed():
    # Video streaming route. Put this in the src attribute of an img tag
    return Response(face_recognition(), mimetype='multipart/x-mixed-replace; boundary=frame')
    # return Response(live_cam(), mimetype='multipart/x-mixed-replace; boundary=frame')

@home.route('/countTodayScan')
@login_required
def countTodayScan():

    mycursor.execute("select count(*) "
                    "  from attendance ")
    row = mycursor.fetchone()
    rowcount = row[0]

    return jsonify({'rowcount': rowcount})

@home.route('/loadData', methods = ['GET', 'POST'])
@login_required
def loadData():

    mycursor.execute("select a.accs_id, a.accs_prsn, b.username, b.email, date_format(a.accs_added, '%H:%i:%s') "
                    "  from attendance a "
                    "  left join users b on a.accs_prsn = b.id "
                    " order by 1 desc")
    data = mycursor.fetchall()

    return jsonify(response = data)