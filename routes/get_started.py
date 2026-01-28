from flask import Blueprint, render_template
from models.get_started import GetStarted

bp = Blueprint("get_started", __name__)

@bp.route("/")
def index():
    items = GetStarted.query.all()
    return render_template("get_started/get_started.html", items=items)



