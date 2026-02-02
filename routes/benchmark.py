from flask import Blueprint, render_template
from models.benchmark import Benchmark
from extensions import cache

bp = Blueprint("benchmark", __name__)

@bp.route("/")
@cache.cached(timeout=300, query_string=False)
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
