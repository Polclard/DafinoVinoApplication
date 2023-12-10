from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

# init SQLAlchemy so we can use it later in our models
db = None


def create_app():
    global db
    db = SQLAlchemy()
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    with app.app_context():
        db.create_all()
        db.session.commit()

    # region intialize one Admin
    # from .models import UserRole
    # new_admin = User(email="Admin@Admin", name="Admin", password=generate_password_hash("Admin"), role=UserRole.ADMIN)
    #
    # # add the new user to the database
    # with app.app_context():
    #     db.session.add(new_admin)
    #     db.session.commit()
    # endregion

    return app
