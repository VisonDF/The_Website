from functools import lru_cache
from sqlalchemy import func
from flask import Flask
from db import db
from routes import admin, auth
from models.benchmark_dataset import BenchmarkDataset
from models.function_impl import FunctionImpl
from models.admin_user import AdminUser
from flask_caching import Cache
from extensions import cache, login_manager

@lru_cache(maxsize=4096)
def dataset_usage_count(dataset_id):
    return (
        db.session.query(func.count(BenchmarkDataset.id))
        .filter_by(dataset_id=dataset_id)
        .scalar()
    )

@lru_cache(maxsize=4096)
def function_family_usage_count(family_id):
    return (
        db.session.query(func.count(FunctionImpl.id))
        .filter_by(family_id=family_id)
        .scalar()
    )

@lru_cache(maxsize=1024)
def load_user_cached(user_id):
    return AdminUser.query.get(user_id)

@login_manager.user_loader
def load_user(user_id):
    return load_user_cached(int(user_id))

def create_app():

    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    cache.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    app.config["DEBUG"] = False
    app.config["TEMPLATES_AUTO_RELOAD"] = False

     # Register Jinja filters
    app.jinja_env.filters["dataset_usage_count"] = dataset_usage_count
    app.jinja_env.filters["function_family_usage_count"] = function_family_usage_count

    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp, url_prefix="/admin")

    return app









