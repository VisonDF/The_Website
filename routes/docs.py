from flask import Blueprint, render_template
from models.function_family import FunctionFamily
from models.function_impl import FunctionImpl

bp = Blueprint("docs", __name__)

@bp.route("/")
def index():
    families = FunctionFamily.query.all()
    return render_template("docs/index.html", families=families)

@bp.route("/<slug>")
def family(slug):
    family = FunctionFamily.query.filter_by(slug=slug).first_or_404()
    functions = FunctionImpl.query.filter_by(family_id=family.id).all()
    return render_template("docs/family.html", family=family, functions=functions)

@bp.route("/function/<int:function_id>")
def function_doc(function_id):
    fn = FunctionImpl.query.get_or_404(function_id)
    return render_template("docs/function.html", fn=fn)



