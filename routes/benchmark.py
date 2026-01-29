from flask import Blueprint, render_template
from models.benchmark import Benchmark

bp = Blueprint("benchmark", __name__)

@bp.route("/")
def index():

    benchs = (
        Benchmark.query
        .filter(Benchmark.highlighted == True)
        .all()
    )

    return render_template(
        "benchmark/benchmark.html",
        benchs=benchs
    )
