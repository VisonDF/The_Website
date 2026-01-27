from flask import Blueprint, render_template
from models.function_family import FunctionFamily
from models.function_impl import FunctionImpl
from models.benchmark import Benchmark
from models.benchmark_dataset import BenchmarkDataset

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

@bp.route("/<lvl>+<slug>+<network>+<gpu>")
def show_functions(lvl, slug, network, gpu):

    if lvl != 'low' and lvl != 'high':
        return render_template("404.html")

    family = FunctionFamily.query.filter_by(slug=slug).first_or_404()

    query  = FunctionImpl.query.filter_by(family_id=family.id, api_level=lvl)

    if network != "any":
        network_val = (network == "yes")
        query = query.filter_by(network=network_val)

    if gpu != "any":
        gpu_val = (gpu == "yes")        
        query = query.filter_by(gpu=gpu_val)

    functions = query.all()

    return render_template("docs/doc_cards.html", 
                           cards=functions, 
                           lvl=lvl, 
                           family=slug,
                           network=network,
                           gpu=gpu)

@bp.route("/function/<int:function_id>")
def function_doc(function_id):
    fn = FunctionImpl.query.get_or_404(function_id)

    benchmark = fn.benchmark

    # Siblings (same family)
    siblings = (
        FunctionImpl.query
        .filter_by(family_id=fn.family_id)
        .filter(FunctionImpl.id != fn.id)
        .all()
    )

    return render_template(
        "docs/function.html",
        fn=fn,
        siblings=siblings,
        benchmark=benchmark,
    )







