from flask import Blueprint, render_template
from models.dev import Dev

bp = Blueprint("dev", __name__)

@bp.route("/")
def index():
    articles = Dev.query.all()
    return render_template("dev/dev_cards.html",
                           articles=articles)

@bp.route("/<title>")
def show_families(article):
    article = Dev.query.filter_by(title=title).first_or_404()

    return render_template("dev/dev.html", 
                           article=article)




