from flask import Blueprint, render_template
from models.dev import Dev

bp = Blueprint("dev", __name__)

@bp.route("/")
def index():
    articles = Dev.query.all()
    return render_template("development/dev_cards.html",
                           articles=articles)

@bp.route("/<int:cur_id>")
def article(cur_id):
    article = Dev.query.filter_by(id=cur_id).first_or_404()

    return render_template("development/dev.html", 
                           article=article)




