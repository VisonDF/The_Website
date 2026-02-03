from sqlalchemy import func
from flask import Flask
from db import db
from routes import admin, auth
from flask_login import LoginManager

login_manager = LoginManager()

def create_app():

    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    app.config["DEBUG"] = False
    app.config["TEMPLATES_AUTO_RELOAD"] = False

    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp, url_prefix="/admin")

    return app









