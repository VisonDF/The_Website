from flask import Blueprint, render_template
from models.get_started import GetStarted
from extensions import cache

bp = Blueprint("get_started", __name__)

@bp.route("/")
@cache.cached(timeout=300, query_string=False)
def index():
    items = (
        GetStarted.query
        .order_by(
            GetStarted.priority.asc(),
            GetStarted.id.asc(),
        )
        .all()
    )

    return render_template(
        "get_started/get_started.html",
        items=items,
    )
