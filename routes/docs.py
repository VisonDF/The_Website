from flask import Blueprint, render_template
from models.function_family import FunctionFamily
from models.function_impl import FunctionImpl

bp = Blueprint("docs", __name__)

@bp.route("/")
def index():
    return render_template("docs/index_docs.html")

@bp.route("/<lvl>")
def show_families(lvl):

    if lvl != 'low' and lvl != 'high':
        return render_template("404.html")

    families = FunctionFamily.query.all()
    return render_template("docs/doc_cards.html", 
                           cards=families, 
                           lvl=lvl,
                           family="")

@bp.route("/<lvl>+<slug>")
def show_functions(lvl, slug):

    if lvl != 'low' and lvl != 'high':
        return render_template("404.html")

    family    = FunctionFamily.query.filter_by(slug=slug).first_or_404()
    functions = FunctionImpl.query.filter_by(family_id=family.id).filter_by(api_level=lvl).all()

    return render_template("docs/doc_cards.html", 
                           cards=functions, 
                           lvl=lvl, 
                           family=slug)

@bp.route("/function/<int:function_id>")
def function_doc(function_id):
    fn = FunctionImpl.query.get_or_404(function_id)
    return render_template("docs/function.html", fn=fn)



