from flask import Blueprint, render_template
from models.pipeline import Pipeline

bp = Blueprint("pipeline", __name__)

@bp.route("/")
def index():
    pipelines = Pipeline.query.order_by(Pipeline.created_at.desc()).all()
    return render_template("pipeline/pipeline_cards.html",
                           pipelines=pipelines)

@bp.route("/<int:cur_id>")
def article(cur_id):
    pipeline = Pipeline.query.filter_by(id=cur_id).first_or_404()

    return render_template("pipeline/pipeline.html", 
                           pipeline=pipeline)




