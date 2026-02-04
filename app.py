from sqlalchemy import func
from flask import Flask
from db import db
from routes import admin, auth
from flask_login import LoginManager
from models import AdminUser
from models import FunctionImpl
from models import BenchmarkDataset, PipelineDataset

def function_family_usage_count(family_id):
    return (
        FunctionImpl.query
        .filter_by(family_id=family_id)
        .count()
    )

def usage_dataset(ds):
    bench_count = (
        BenchmarkDataset.query
        .filter_by(dataset_id=ds.id)
        .count()
    )

    pipeline_count = (
        PipelineDataset.query
        .filter_by(dataset_id=ds.id)
        .count()
    )

    return {
        "benchmarks": bench_count,
        "pipelines": pipeline_count,
        "total": bench_count + pipeline_count,
    }

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

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
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp, url_prefix="/admin")

    app.jinja_env.filters["function_family_usage_count"] = (
        function_family_usage_count
    )
    app.jinja_env.filters["usage_dataset"] = usage_dataset
    return app









