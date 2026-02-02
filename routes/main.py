from flask import Blueprint, render_template
from extensions import cache

bp = Blueprint("main", __name__)

@bp.route("/")
@cache.cached(timeout=60, query_string=False)
def index():
    return render_template("index.html")
