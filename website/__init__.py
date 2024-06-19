from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'x-ticket-app'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/flask_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)


    from .views import views
    from .auth.index import auth
    from .admin.index import home
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(home, url_prefix='/')

    from .models import Users, Images
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Users.query.get(int(id))
    return app



def create_database(app):
    db.create_all(app=app)
    print('Created Database!')

