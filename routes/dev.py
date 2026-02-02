from flask import Blueprint, render_template
from models.dev import Dev
from extensions import cache

bp = Blueprint("dev", __name__)

@bp.route("/")
@cache.cached(timeout=300, query_string=False)
def index():
    articles = Dev.query.all()
    return render_template("development/dev_cards.html",
                           articles=articles)

@bp.route("/<int:cur_id>")
@cache.cached(timeout=300, query_string=False)
def article(cur_id):
    article = Dev.query.filter_by(id=cur_id).first_or_404()

    return render_template("development/dev.html", 
                           article=article)




