from flask import Blueprint, render_template
from models.pipeline import Pipeline
from extensions import cache

bp = Blueprint("pipeline", __name__)

@bp.route("/")
@cache.cached(timeout=300, query_string=False)
def index():
    pipelines = Pipeline.query.order_by(Pipeline.created_at.desc()).all()
    return render_template("pipeline/pipeline_cards.html",
                           pipelines=pipelines)

@bp.route("/<int:cur_id>")
@cache.cached(timeout=300, query_string=False)
def article(cur_id):
    pipeline = Pipeline.query.filter_by(id=cur_id).first_or_404()

    return render_template("pipeline/pipeline.html", 
                           pipeline=pipeline)




