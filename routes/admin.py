from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    current_app,
    abort,
    flash,
)
from flask_login import login_required
from werkzeug.utils import secure_filename

from models.dataset import Dataset
from models.function_family import FunctionFamily
from models.function_impl import FunctionImpl
from models.benchmark import Benchmark
from models.benchmark_dataset import BenchmarkDataset
from models.dev import Dev
from models.get_started import GetStarted
from models.pipeline import Pipeline
from models.pipeline_dataset import PipelineDataset
from db import db
from typing import Optional

from collections import defaultdict
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import os
import shutil

# -------------------------------------------------------------------
# Jinja environment (you use it to render templates to static files)
# -------------------------------------------------------------------
env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=True,
)

# -------------------------------------------------------------------
# Build output roots
# -------------------------------------------------------------------
BUILD_DIR = Path("builds")
BUILD_DIR.mkdir(exist_ok=True)

DOCS_DIR = BUILD_DIR / "docs"  # builds/docs/...

# Your filter axes for docs/show_functions
NETWORK = ["any", "yes", "no"]
GPU = ["any", "yes", "no"]

FILTER_COMBINATIONS = [
    "anyany",
    "yesany",
    "anyyes",
    "yesyes",
    "noany",
    "anyno",
    "nono",
    "noyes",
]

bp = Blueprint("admin", __name__)

# -------------------------------------------------------------------
# Small helpers
# -------------------------------------------------------------------
def _write_html(path: Path, html: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def _rm_tree(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)


def _bool_yes(value: Optional[str]) -> bool:
    return (value or "").strip().lower() == "yes"


# -------------------------------------------------------------------
# Rebuild helpers (THIS encodes your dependency graph)
# -------------------------------------------------------------------
def rebuild_function_page(fn: FunctionImpl) -> None:
    """
    Rebuild ONLY the function detail page:
      builds/docs/function_doc/<fn.id>/index.html

    Trigger when:
      - FunctionImpl fields change (summary/metadata/etc.)
      - Benchmark changes (title/desc/highlighted)
      - BenchmarkDataset changes (datasets list)

    Notes:
      - It is correct that benchmark changes affect ONLY this page.
      - We read fn.benchmark and embed it, but we do not mutate it here.
    """
    fn = FunctionImpl.query.get(fn.id)

    benchmark = fn.benchmark
    siblings = (
        FunctionImpl.query.filter_by(family_id=fn.family_id)
        .filter(FunctionImpl.id != fn.id)
        .all()
    )

    html = env.get_template("docs/function.html").render(
        fn=fn,
        siblings=siblings,
        benchmark=benchmark,
    )

    out = DOCS_DIR / "function_doc" / str(fn.id) / "index.html"
    _write_html(out, html)


def rebuild_show_functions_for(fn: FunctionImpl) -> None:
    """
    Rebuild ONLY the show_functions listings for a given (family_id, api_level):
      builds/docs/show_functions/<family>/<api>/<network><gpu>/index.html

    Trigger when:
      - FunctionImpl changes that affect cards/listing (summary, name, network/gpu, family, api)
      - FunctionImpl create/delete
      - Taxonomy reassignment

    MUST NOT be triggered by benchmark changes.
    """
    all_fns = (
        FunctionImpl.query.filter_by(api_level=fn.api_level, family_id=fn.family_id)
        .all()
    )

    api_level, complement_api_level = (
        ("low", "high") if str(fn.api_level) == "low" else ("high", "low")
    )

    base = DOCS_DIR / "show_functions" / str(fn.family_id) / api_level

    for network in NETWORK:
        for gpu in GPU:
            filtered = [
                f
                for f in all_fns
                if (network == "any" or f.network == (network == "yes"))
                and (gpu == "any" or f.gpu == (gpu == "yes"))
            ]

            html = env.get_template("docs/doc_cards.html").render(
                lvl=api_level,
                family=True,
                network=network,
                gpu=gpu,
                cards=filtered,
                family_id=fn.family_id
            )

            out_dir = base / f"{network}{gpu}"
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "index.html").write_text(html, encoding="utf-8")

    base = DOCS_DIR / "show_functions" / str(fn.family_id) / complement_api_level

    for network in NETWORK:
        for gpu in GPU:
            filtered = None

            html = env.get_template("docs/doc_cards.html").render(
                lvl=complement_api_level,
                family=True,
                network=network,
                gpu=gpu,
                cards=filtered,
                family_id=fn.family_id
            )

            out_dir = base / f"{network}{gpu}"
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "index.html").write_text(html, encoding="utf-8")

def rebuild_family_listings() -> None:
    """
    Rebuild family listings:
      builds/docs/show_families/<low|high>/index.html
    """
    families = FunctionFamily.query.order_by(FunctionFamily.display_name).all()

    out_base = DOCS_DIR / "show_families"
    for lvl in ("low", "high"):
        html = env.get_template("docs/doc_cards.html").render(
            lvl=lvl,
            family=False,
            cards=families,
        )
        out = out_base / lvl / "index.html"
        _write_html(out, html)


def rebuild_get_started_index() -> None:
    """
    Rebuild get started page:
      builds/get_started/index.html
    """
    items = (
        GetStarted.query.order_by(GetStarted.priority.asc(), GetStarted.id.asc()).all()
    )
    html = env.get_template("get_started/get_started.html").render(items=items)
    out = BUILD_DIR / "get_started" / "index.html"
    _write_html(out, html)


def rebuild_dev_pages(article_id: Optional[int] = None) -> None:
    """
    Rebuild dev list and optionally a single article page.
      builds/dev/show_dev/index.html
      builds/dev/dev/<id>/index.html
    """
    articles = Dev.query.order_by(Dev.created_at.desc()).all()

    list_html = env.get_template("development/dev_cards.html").render(articles=articles)
    _write_html(BUILD_DIR / "dev" / "show_dev" / "index.html", list_html)

    if article_id is not None:
        article = Dev.query.get(article_id)
        if article is not None:
            art_html = env.get_template("development/dev.html").render(article=article)
            _write_html(BUILD_DIR / "dev" / "dev" / str(article.id) / "index.html", art_html)


def rebuild_pipeline_pages(pipeline_id: Optional[int] = None) -> None:
    """
    Rebuild pipeline list and optionally a single pipeline page.
      builds/pipeline/show_pipeline/index.html
      builds/pipeline/pipeline/<id>/index.html
    """
    pipelines = Pipeline.query.order_by(Pipeline.created_at.desc()).all()

    list_html = env.get_template("pipeline/pipeline_cards.html").render(pipelines=pipelines)
    _write_html(BUILD_DIR / "pipeline" / "show_pipeline" / "index.html", list_html)

    if pipeline_id is not None:
        pipeline = Pipeline.query.get(pipeline_id)
        if pipeline is not None:
            page_html = env.get_template("pipeline/pipeline.html").render(pipeline=pipeline)
            _write_html(BUILD_DIR / "pipeline" / "pipeline" / str(pipeline.id) / "index.html", page_html)

def rebuild_highlight_bench() -> None:

    benchs = (
        Benchmark.query
        .filter(Benchmark.highlighted.is_(True))
        .order_by(Benchmark.created_at.desc())
        .all()
    )

    html = env.get_template("benchmark/benchmark.html").render(benchs=benchs)
    _write_html(BUILD_DIR / "benchmark" / "index.html", html)


# -------------------------------------------------------------------
# Admin protection
# -------------------------------------------------------------------
@bp.before_request
@login_required
def _protect_admin():
    pass


# -------------------------------------------------------------------
# Dashboard
# -------------------------------------------------------------------
@bp.route("/")
def dashboard():
    return render_template("admin/admin_panel.html")


# -------------------------------------------------------------------
# FunctionImpl CRUD
# -------------------------------------------------------------------
@bp.route("/f_impl/<int:function_id>", methods=["GET", "POST"])
def edit_function_impl(function_id: int):
    fn = FunctionImpl.query.get_or_404(function_id)
    families = FunctionFamily.query.order_by(FunctionFamily.display_name).all()
    datasets = Dataset.query.order_by(Dataset.name, Dataset.version).all()

    if request.method == "POST":
        old_family_id = fn.family_id
        old_api_level = fn.api_level

        fn.real_name = request.form["real_name"]
        fn.api_level = request.form["api_level"]
        fn.family_id = int(request.form["family_id"])
        fn.network = _bool_yes(request.form.get("network"))
        fn.gpu = _bool_yes(request.form.get("gpu"))
        fn.summary = request.form["summary"]

        default_dataset_id = request.form.get("default_dataset_id")
        fn.default_dataset_id = int(default_dataset_id) if default_dataset_id else None

        fn.signature_html = request.form.get("signature_html")
        fn.description_html = request.form.get("description_html")

        db.session.commit()

        # Always rebuild its function page
        rebuild_function_page(fn)

        # Rebuild listings affected by this function:
        # - its NEW (family, api)
        rebuild_show_functions_for(fn)
        # - and if it moved family or api level, rebuild the OLD bucket too
        if old_family_id != fn.family_id or old_api_level != fn.api_level:
            class _Tmp:
                pass
            tmp = _Tmp()
            tmp.family_id = old_family_id
            tmp.api_level = old_api_level
            rebuild_show_functions_for(tmp)  # type: ignore[arg-type]

        return redirect(url_for("admin.show_function_impl"))

    return render_template(
        "admin/actions/edit_function_impl.html",
        fn=fn,
        families=families,
        datasets=datasets,
    )


@bp.route("/f_impl/add", methods=["GET", "POST"])
def add_function_impl():
    families = FunctionFamily.query.order_by(FunctionFamily.display_name).all()
    datasets = Dataset.query.order_by(Dataset.name, Dataset.version).all()

    if request.method == "POST":
        fn = FunctionImpl(
            real_name=request.form["real_name"],
            api_level=request.form["api_level"],
            family_id=int(request.form["family_id"]),
            signature_html=request.form.get("signature_html"),
            description_html=request.form.get("description_html"),
            network=_bool_yes(request.form.get("network")),
            gpu=_bool_yes(request.form.get("gpu")),
            summary=request.form["summary"],
            default_dataset_id=(
                int(request.form["default_dataset_id"])
                if request.form.get("default_dataset_id")
                else None
            ),
        )
        db.session.add(fn)
        db.session.commit()

        rebuild_function_page(fn)
        rebuild_show_functions_for(fn)

        return redirect(url_for("admin.show_function_impl"))

    return render_template(
        "admin/actions/add_function_impl.html",
        families=families,
        datasets=datasets,
    )


@bp.route("/f_impl/<int:function_id>/delete", methods=["POST"])
def delete_function_impl(function_id: int):
    fn = FunctionImpl.query.get_or_404(function_id)

    # Keep bucket info before deleting
    family_id = fn.family_id
    api_level = fn.api_level

    db.session.delete(fn)
    db.session.commit()

    # Rebuild the listings bucket that contained it
    class _Tmp:
        pass
    tmp = _Tmp()
    tmp.family_id = family_id
    tmp.api_level = api_level
    rebuild_show_functions_for(tmp)  # type: ignore[arg-type]

    # Remove the function page folder
    _rm_tree(DOCS_DIR / "function_doc" / str(function_id))

    return redirect(url_for("admin.show_function_impl"))


# -------------------------------------------------------------------
# Datasets CRUD
# -------------------------------------------------------------------
@bp.route("/datasets/edit", methods=["GET"])
def edit_datasets():
    datasets = Dataset.query.order_by(Dataset.created_at.desc()).all()
    return render_template("admin/actions/edit_datasets.html", 
                          datasets=datasets)

@bp.route("/datasets/<int:dataset_id>/edit", methods=["GET", "POST"])
def edit_dataset(dataset_id: int):
    dataset = Dataset.query.get_or_404(dataset_id)

    if request.method == "POST":
        dataset.name = request.form["name"]
        dataset.version = request.form["version"]
        dataset.description = request.form.get("description")
        db.session.commit()
        return redirect(url_for("admin.edit_datasets"))

    return render_template("admin/actions/edit_dataset.html", dataset=dataset)


@bp.route("/datasets", methods=["GET", "POST"])
def add_datasets():
    if request.method == "POST":
        name = request.form["name"]
        version = request.form["version"]
        description = request.form.get("description")
        file = request.files.get("file")

        if not file or file.filename == "":
            raise ValueError("No file uploaded")

        filename = secure_filename(file.filename)

        dataset_dir = os.path.join(current_app.root_path, "static", "datasets")
        os.makedirs(dataset_dir, exist_ok=True)

        filepath = os.path.join(dataset_dir, filename)
        file.save(filepath)

        download_url = f"/static/datasets/{filename}"

        dataset = Dataset(
            name=name,
            version=version,
            description=description,
            download_url=download_url,
        )
        db.session.add(dataset)
        db.session.commit()

        return redirect(url_for("admin.show_datasets"))

    datasets = Dataset.query.order_by(Dataset.created_at.desc()).all()
    return render_template("admin/actions/add_datasets.html", datasets=datasets)


@bp.route("/datasets/<int:dataset_id>/delete", methods=["POST"])
def delete_dataset(dataset_id: int):
    dataset = Dataset.query.get_or_404(dataset_id)

    usage_count = (
        BenchmarkDataset.query.filter_by(dataset_id=dataset.id).count()
    )
    if usage_count > 0:
        abort(400, "Dataset is still used by benchmarks")

    if dataset.download_url:
        file_path = os.path.join(
            current_app.root_path,
            dataset.download_url.lstrip("/"),
        )
        if os.path.exists(file_path):
            os.remove(file_path)

    db.session.delete(dataset)
    db.session.commit()

    return redirect(url_for("admin.show_datasets"))


# -------------------------------------------------------------------
# Taxonomy (reassign functions to families)
# -------------------------------------------------------------------
@bp.route("/taxonomy", methods=["GET", "POST"])
def taxonomy():
    families = FunctionFamily.query.order_by(FunctionFamily.display_name).all()
    functions = FunctionImpl.query.order_by(FunctionImpl.real_name).all()

    if request.method == "POST":
        for fn in functions:
            field_name = f"family_{fn.id}"
            new_family_id = request.form.get(field_name)

            if new_family_id and int(new_family_id) != fn.family_id:
                old_family_id = fn.family_id
                old_api_level = fn.api_level

                fn.family_id = int(new_family_id)
                db.session.commit()

                rebuild_function_page(fn)
                rebuild_show_functions_for(fn)

                # Also rebuild old bucket where it came from
                class _Tmp:
                    pass
                tmp = _Tmp()
                tmp.family_id = old_family_id
                tmp.api_level = old_api_level
                rebuild_show_functions_for(tmp)  # type: ignore[arg-type]

        return redirect(url_for("admin.dashboard"))

    grouped = defaultdict(list)
    for fn in functions:
        grouped[fn.family_id].append(fn)

    return render_template(
        "admin/actions/taxonomy.html",
        families=families,
        grouped_functions=grouped,
    )


# -------------------------------------------------------------------
# FunctionFamily CRUD
# -------------------------------------------------------------------
@bp.route("/function_family/add", methods=["GET", "POST"])
def add_function_family():
    if request.method == "POST":
        family = FunctionFamily(
            slug=request.form["slug"],
            display_name=request.form["display_name"],
            description=request.form.get("description"),
        )
        db.session.add(family)
        db.session.commit()

        rebuild_family_listings()

        # Create skeleton dirs for show_functions filters
        out_functions_base = DOCS_DIR / "show_functions" / str(family.id)
        for lvl in ("low", "high"):
            for combo in FILTER_COMBINATIONS:
                (out_functions_base / lvl / combo).mkdir(parents=True, exist_ok=True)

        class _Tmp:
            pass
        tmp = _Tmp()
        tmp.family_id = family.id
        tmp.api_level = "low"
        rebuild_show_functions_for(tmp) 

        return redirect(url_for("admin.show_function_family"))

    families = FunctionFamily.query.order_by(FunctionFamily.display_name).all()
    return render_template("admin/actions/add_function_family.html", families=families)


@bp.route("/function_family/<int:family_id>", methods=["GET", "POST"])
def edit_function_family(family_id: int):
    family = FunctionFamily.query.get_or_404(family_id)

    if request.method == "POST":
        family.slug = request.form["slug"]
        family.display_name = request.form["display_name"]
        family.description = request.form.get("description")
        db.session.commit()

        rebuild_family_listings()
        return redirect(url_for("admin.show_function_family"))

    return render_template("admin/actions/edit_function_family.html", family=family)


@bp.route("/function_family/<int:family_id>/delete", methods=["POST"])
def delete_function_family(family_id: int):

    print("DELETE ROUTE HIT")
    family = FunctionFamily.query.get_or_404(family_id)

    usage = FunctionImpl.query.filter_by(family_id=family.id).count()
    if usage > 0:
        abort(400, "Family still has functions assigned")

    db.session.delete(family)
    db.session.commit()

    rebuild_family_listings()
    _rm_tree(DOCS_DIR / "show_functions" / str(family_id))

    print("ok")

    return redirect(url_for("admin.show_function_family"))


# -------------------------------------------------------------------
# SHOW pages (admin UI)
# -------------------------------------------------------------------
@bp.route("/datasets/show", methods=["GET"])
def show_datasets():
    datasets = Dataset.query.order_by(Dataset.created_at.desc()).all()
    return render_template("admin/show/datasets.html", datasets=datasets)


@bp.route("/function_family/show", methods=["GET"])
def show_function_family():
    families = FunctionFamily.query.order_by(FunctionFamily.display_name).all()
    return render_template("admin/show/function_family.html", families=families)


@bp.route("/function_impl/show", methods=["GET"])
def show_function_impl():
    functions = FunctionImpl.query.order_by(FunctionImpl.real_name).all()
    return render_template("admin/show/function_impl.html", functions=functions)


@bp.route("/benchmarks/show", methods=["GET"])
def show_benchs():
    benchmarks = (
        Benchmark.query.join(FunctionImpl)
        .order_by(FunctionImpl.real_name)
        .all()
    )
    return render_template("admin/show/benchmarks.html", benchmarks=benchmarks)


# -------------------------------------------------------------------
# Dev CRUD + rebuild
# -------------------------------------------------------------------
@bp.route("/dev/show", methods=["GET"])
def show_dev():
    articles = Dev.query.order_by(Dev.created_at.desc()).all()
    return render_template("admin/show/dev.html", articles=articles)


@bp.route("/dev/add", methods=["GET", "POST"])
def add_dev():
    if request.method == "POST":
        article = Dev(
            title=request.form["title"],
            description_html=request.form.get("description_html"),
        )
        db.session.add(article)
        db.session.commit()

        rebuild_dev_pages(article.id)
        return redirect(url_for("admin.show_dev"))

    return render_template("admin/actions/add_dev.html")


@bp.route("/dev/<int:article_id>", methods=["GET", "POST"])
def edit_dev(article_id: int):
    article = Dev.query.get_or_404(article_id)

    if request.method == "POST":
        article.title = request.form["title"]
        article.description_html = request.form.get("description_html")
        db.session.commit()

        rebuild_dev_pages(article.id)
        return redirect(url_for("admin.show_dev"))

    return render_template("admin/actions/edit_dev.html", article=article)


@bp.route("/dev/<int:article_id>/delete", methods=["POST"])
def delete_dev(article_id: int):
    article = Dev.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()

    _rm_tree(BUILD_DIR / "dev" / "dev" / str(article_id))
    rebuild_dev_pages(None)

    return redirect(url_for("admin.show_dev"))


# -------------------------------------------------------------------
# Get Started CRUD + rebuild
# -------------------------------------------------------------------
@bp.route("/get_started/show", methods=["GET"])
def show_get_started():
    plans = GetStarted.query.order_by(GetStarted.priority.asc(), GetStarted.id.asc()).all()
    return render_template("admin/show/get_started.html", plans=plans)


@bp.route("/get_started/add", methods=["GET", "POST"])
def add_get_started():
    fns = (
        FunctionImpl.query.outerjoin(
            GetStarted,
            GetStarted.function_impl_id == FunctionImpl.id
        )
        .filter(GetStarted.id.is_(None))
        .order_by(FunctionImpl.real_name)
        .all()
    )

    if request.method == "POST":
        fn = FunctionImpl.query.filter_by(id=request.form["function_impl"]).first_or_404()

        plan = GetStarted(
            goal=request.form["goal"],
            priority=int(request.form["priority"]) if request.form.get("priority") else None,
            function_impl=fn,
            api_level=fn.api_level
        )
        db.session.add(plan)
        db.session.commit()

        rebuild_get_started_index()
        return redirect(url_for("admin.show_get_started"))

    return render_template("admin/actions/add_get_started.html", fns=fns)


@bp.route("/get_started/<int:plan_id>", methods=["GET", "POST"])
def edit_get_started(plan_id: int):
    plan = GetStarted.query.get_or_404(plan_id)
    fns = FunctionImpl.query.order_by(FunctionImpl.real_name).all()

    if request.method == "POST":
        plan.goal = request.form["goal"]
        plan.priority = int(request.form["priority"]) if request.form.get("priority") else None

        fn = FunctionImpl.query.filter_by(id=request.form["function_impl"]).first_or_404()
        plan.function_impl = fn

        db.session.commit()
        rebuild_get_started_index()

        return redirect(url_for("admin.show_get_started"))

    return render_template("admin/actions/edit_get_started.html", plan=plan, fns=fns)


@bp.route("/get_started/<int:plan_id>/delete", methods=["POST"])
def delete_get_started(plan_id: int):
    plan = GetStarted.query.get_or_404(plan_id)
    db.session.delete(plan)
    db.session.commit()

    rebuild_get_started_index()
    return redirect(url_for("admin.show_get_started"))


# -------------------------------------------------------------------
# Pipeline CRUD + rebuild
# -------------------------------------------------------------------
@bp.route("/pipeline/show", methods=["GET"])
def show_pipeline():
    pipelines = Pipeline.query.all()
    return render_template("admin/show/pipeline.html", pipelines=pipelines)


@bp.route("/pipeline/add", methods=["GET", "POST"])
def add_pipeline():
    if request.method == "POST":
        pipeline = Pipeline(
            title=request.form["title"],
            description_html=request.form.get("description_html"),
        )
        db.session.add(pipeline)
        db.session.commit()

        rebuild_pipeline_pages(pipeline.id)
        return redirect(url_for("admin.show_pipeline"))

    return render_template("admin/actions/add_pipeline.html")


@bp.route("/pipeline/<int:pipeline_id>", methods=["GET", "POST"])
def edit_pipeline(pipeline_id: int):
    pipeline = Pipeline.query.get_or_404(pipeline_id)

    if request.method == "POST":
        pipeline.title = request.form["title"]
        pipeline.description_html = request.form.get("description_html")
        db.session.commit()

        rebuild_pipeline_pages(pipeline.id)
        return redirect(url_for("admin.show_pipeline"))

    return render_template("admin/actions/edit_pipeline.html", pipeline=pipeline)


@bp.route("/pipeline/<int:pipeline_id>/datasets", methods=["GET", "POST"])
def edit_pipeline_datasets(pipeline_id: int):
    pipeline = Pipeline.query.get_or_404(pipeline_id)
    all_datasets = Dataset.query.all()

    if request.method == "POST":
        selected_ids = map(int, request.form.getlist("dataset_ids"))

        PipelineDataset.query.filter_by(
            pipeline_id=pipeline.id
        ).delete(synchronize_session=False)

        for ds_id in selected_ids:
            db.session.add(PipelineDataset(pipeline_id=pipeline.id, dataset_id=ds_id))

        db.session.commit()
        rebuild_pipeline_pages(pipeline.id)

        return redirect(url_for("admin.show_pipeline"))

    return render_template(
        "admin/actions/edit_pipeline_datasets.html",
        pipeline=pipeline,
        all_datasets=all_datasets,
    )


@bp.route("/pipeline/<int:pipeline_id>/delete", methods=["POST"])
def delete_pipeline(pipeline_id: int):
    pipeline = Pipeline.query.get_or_404(pipeline_id)
    db.session.delete(pipeline)
    db.session.commit()

    _rm_tree(BUILD_DIR / "pipeline" / "pipeline" / str(pipeline_id))
    rebuild_pipeline_pages(None)

    return redirect(url_for("admin.show_pipeline"))




# -------------------------------------------------------------------
# Benchmark endpoints (relationship anchored; no show_functions rebuild)
# -------------------------------------------------------------------
@bp.route("/benchmark/edit/<int:function_impl_id>", methods=["GET", "POST"])
def edit_benchmark(function_impl_id):

    fn = FunctionImpl.query.get_or_404(function_impl_id)

    if request.method == "POST":

        title = (request.form.get("title") or "").strip()
        description_html = request.form.get("description_html") or ""
        highlighted = _bool_yes(request.form.get("highlighted"))

        bench = fn.benchmark
        bench.title = title
        bench.description_html = description_html
        bench.highlighted = highlighted

        db.session.commit()

        # Benchmark changes affect ONLY the function page
        rebuild_function_page(fn)

        rebuild_highlight_bench()

        flash("Benchmark saved.", "success")
        return redirect(url_for("admin.show_benchs"))

    return render_template("admin/actions/edit_function_benchmarks.html", 
                           fn=fn)

@bp.route("/benchmark/add", methods=["GET", "POST"])
def add_benchmark():

    fns = (
        FunctionImpl.query
        .outerjoin(Benchmark)
        .filter(Benchmark.id.is_(None))
        .order_by(FunctionImpl.real_name)
        .all()
    )

    if request.method == "POST":

        title            = (request.form.get("title") or "").strip()
        description_html = request.form.get("description_html") or ""
        highlighted      = _bool_yes(request.form.get("highlighted"))
        function_impl_id = int(request.form["function_impl_id"])
        fn               = FunctionImpl.query.get_or_404(function_impl_id)

        bench = Benchmark(
            function_impl=fn,
            title=title,
            description_html=description_html,
            highlighted=highlighted,
        )
        db.session.add(bench)

        db.session.commit()

        # Benchmark changes affect ONLY the function page
        rebuild_function_page(fn)

        rebuild_highlight_bench()

        flash("Benchmark saved.", "success")

        return redirect(url_for("admin.show_benchs"))

    return render_template("admin/actions/add_function_benchmarks.html",
                          functions=fns)

@bp.route("/benchmark/datasets/edit/<int:bench_id>", methods=["GET", "POST"])
def edit_benchmark_datasets(bench_id):

    bench = Benchmark.query.get_or_404(bench_id)

    if request.method == "POST":

        selected_ids = map(int, request.form.getlist("dataset_ids"))

        BenchmarkDataset.query.filter_by(
            benchmark_id=bench.id
        ).delete(synchronize_session=False)

        for did in selected_ids:
            db.session.add(BenchmarkDataset(benchmark_id=bench.id, dataset_id=did))

        db.session.commit()

        fn = FunctionImpl.query.get_or_404(bench.function_impl_id)

        # Dataset changes affect ONLY the function page
        rebuild_function_page(fn)

        flash("Benchmark datasets updated.", "success")
        return redirect(url_for("admin.show_benchs"))

    all_datasets = (
        Dataset.query
        .order_by(Dataset.name, Dataset.version)
        .all()
    )

    return render_template("admin/actions/edit_benchmark_datasets.html",
                          benchmark=bench,
                          all_datasets=all_datasets)

@bp.route("/benchmark/delete", methods=["POST"])
def delete_benchmark():
    function_impl_id = request.form.get("function_impl_id", type=int)
    fn = FunctionImpl.query.get_or_404(function_impl_id)

    if fn.benchmark:
        db.session.delete(fn.benchmark)
        db.session.commit()

    rebuild_function_page(fn)

    flash("Benchmark deleted.", "success")
    return redirect(url_for("admin.edit_function_impl", function_id=fn.id))





