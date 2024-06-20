from flask import Blueprint, render_template,request, flash, redirect, url_for, Response, jsonify, g
from flask_login import login_required, current_user, logout_user
from website.models import Users, Booking, Events
from website import db
import mysql.connector
import cv2, os
from PIL import Image
import numpy as np
from datetime import datetime
from aiohttp import web


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="flask_db"
)

mycursor = mydb.cursor()


views = Blueprint('views', __name__)


def generate_dataset(nbr):
    face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def face_cropped(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)
        # scaling factor=1.3
        # Minimum neighbor = 5

        if faces is ():
            return None
        for (x, y, w, h) in faces:
            cropped_face = img[y:y + h, x:x + w]
        return cropped_face

    cap = cv2.VideoCapture(0)

    mycursor.execute("select ifnull(max(img_id), 102) from images")
    row = mycursor.fetchone()
    lastid = row[0]

    img_id = lastid
    max_imgid = img_id + 25
    count_img = 0

    while True:
        # cap.open(address)
        ret, img = cap.read()
        if face_cropped(img) is not None:
            count_img += 1
            img_id += 1
            face = cv2.resize(face_cropped(img), (300, 300))
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

            file_name_path = "website/dataset/"+nbr+"."+ str(img_id) + ".jpg"
            cv2.imwrite(file_name_path, face)
            # cv2.putText(face, str(count_img), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

            mycursor.execute("""INSERT INTO `images` (`img_id`, `img_person`) VALUES
                                ('{}', '{}')""".format(img_id, nbr))
            mydb.commit()

            frame = cv2.imencode('.jpg', face)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            # print(img_id)

            if cv2.waitKey(1) == 13 or int(img_id) == int(max_imgid):
                break
                cap.release()
                cv2.destroyAllWindows()



@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    data = Events.query.first()

    return render_template("home.html", data=data)

@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = Users.query.first()
    
    return render_template('profile.html', data=user)

@views.route('/orders')
@login_required
def orders():
    
    data = db.session.query(Events.title, Events.venue, Events.date_events).join(Booking). \
        filter(Events.id == Booking.events_id).all()
    
    return render_template('orders.html', data=data)

@views.route('/booking/<int:id>', methods=['GET', 'POST'])
@login_required
def booking(id):
    book_events = Events.query.get(id)
    user = current_user
    
    if request.method == "POST":
        if id:
            user_id = current_user.id
            
            book_date = datetime.now()
            
            mycursor.execute("""INSERT INTO `booking` (`user_id`, `events_id`, `book_date`) VALUES
                                ('{}', '{}', '{}')""".format(user_id, id, book_date))
            mydb.commit()
            flash('Orders successfully!', category='successful')
            return redirect(url_for('views.orders'))
    else:
        return render_template('booking.html', booking=book_events, user=user)

@views.route('/', methods=['GET', 'POST'])
@login_required
def booking_submit():
    if request.method == 'POST':
        user_id = current_user.id
            
        events_id = Events.query.get(id)
        book_date = request.form.get('txt_book_date')
            
        booking = Booking(user_id=user_id,events_id=events_id, book_date=book_date,)
        db.session.add(booking)
        db.session.commit()
        flash('Orders successfully!', category='successful')
            
        return redirect(url_for('views.profile'))
    else:
        return render_template('profile.html')

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Train Classifier >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@views.route('/train_classifier/<nbr>')
@login_required
def train_classifier(nbr):
    dataset_dir = "website/dataset/"

    path = [os.path.join(dataset_dir, f) for f in os.listdir(dataset_dir)]
    faces = []
    ids = []

    for image in path:
        img = Image.open(image).convert('L');
        imageNp = np.array(img, 'uint8')
        id = int(os.path.split(image)[1].split(".")[1])

        faces.append(imageNp)
        ids.append(id)
    ids = np.array(ids)

    # Train the classifier and save
    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.train(faces, ids)
    clf.write("classifier.xml")
    
    data = current_user
    data.is_verif = 1
    db.session.add(data)
    db.session.commit()
    
    flash('Verification successfully!', category='successful')

    return redirect(url_for("views.profile"))

@views.route('/vfdataset_page/<id>')
@login_required
def vfdataset_page(id):
    return render_template('verification.html', id=id)
    # return web.FileResponse('verification.html', id=id)

@views.route('/vidfeed_dataset/<nbr>')
@login_required
def vidfeed_dataset(nbr):
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(generate_dataset(nbr), mimetype='multipart/x-mixed-replace; boundary=frame')
    # return web.FileResponse('verification.html', id=id)


@views.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))