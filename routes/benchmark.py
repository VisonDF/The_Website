from flask import Blueprint, render_template
from models.function_impl import FunctionImpl

bp = Blueprint("benchmark", __name__)

@bp.route("/")
def index():

    return render_template(
        "benchmark/benchmark.html"
    )
