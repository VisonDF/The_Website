from flask import Flask
from flask_login import LoginManager
from db import db
from routes import main, docs, get_started, admin, auth, dev
from models.benchmark_dataset import BenchmarkDataset
from models.function_impl import FunctionImpl
from models.admin_user import AdminUser

login_manager = LoginManager()

def dataset_usage_count(dataset_id):
    return (
        BenchmarkDataset.query
        .filter_by(dataset_id=dataset_id)
        .count()
    )

def function_family_usage_count(family_id):
    return (
        FunctionImpl.query
        .filter_by(family_id=family_id)
        .count()
    )

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return AdminUser.query.get(int(user_id))

     # Register Jinja filters
    app.jinja_env.filters["dataset_usage_count"] = dataset_usage_count
    app.jinja_env.filters["function_family_usage_count"] = function_family_usage_count

    app.register_blueprint(main.bp)
    app.register_blueprint(dev.bp,        url_prefix="/dev")
    app.register_blueprint(docs.bp,        url_prefix="/docs")
    app.register_blueprint(get_started.bp, url_prefix="/get_started")
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp, url_prefix="/admin")

    return app



