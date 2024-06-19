from flask import Blueprint, render_template, request, flash, redirect, url_for
from website.models import Users
from werkzeug.security import generate_password_hash, check_password_hash
from website import db
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import func, literal

auth = Blueprint('auth', __name__)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Users.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='successful')
                login_user(user, remember=True)
                if user.is_admin == 1:
                    return redirect(url_for('admin.index'))
                else:
                    return redirect(url_for("views.home"))
            else:
                flash('Incorrect Password, please try again.', category='error')
        else:
            flash('Email does not exist', category='error')

    return render_template("auth/login.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    
    if request.method == 'POST':
        id_user = db.session.query(func.ifnull(func.max(Users.id) + 1, literal(101))).scalar()
        
        email = request.form.get('txtemail')
        username = request.form.get('txtname')
        address = request.form.get('txtaddress')
        password1 = request.form.get('txtpass')
        

        user = Users.query.filter_by(email=email).first()
        if user:
            flash('Email Already Exist', category='error')
        elif len(email) < 8:
            flash('Email must be greater than 8 characters.', category='error')
        elif len(username) < 1:
            flash('First name must be greater than 1 characters.', category='error')
        elif len(password1) < 5:
            flash('Passwords must be atleast 5 characters.', category='error')
        else:
            user = Users(id=id_user,email=email, username=username, address=address, password=generate_password_hash(password1))
            db.session.add(user)
            db.session.commit()
            # return redirect(url_for('auth.vfdataset_page', id=id_user))
            login_user(user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("auth/sign_up.html", user=current_user)



