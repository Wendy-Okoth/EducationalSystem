from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Config (replace with your own)
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:1freedom@localhost/edu_system"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "supersecretkey"

    db.init_app(app)
    migrate.init_app(app, db)

    from . import models  # make sure models are imported so migrations see them

    # ✅ Register Blueprints here
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from .routes.student import student_bp
    from .routes.teacher import teacher_bp
    from .routes.admin import admin_bp


    app.register_blueprint(student_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(admin_bp)
 

    return app

