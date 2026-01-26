from flask import (Blueprint, 
                   render_template, 
                   request, 
                   redirect, 
                   url_for, 
                   current_app, 
                   abort)
from flask_login import login_required
from models.dataset import Dataset
from models.function_family import FunctionFamily
from models.function_impl import FunctionImpl
from models.benchmark import Benchmark
from models.benchmark_dataset import BenchmarkDataset
from models.dev import Dev
from db import db
from werkzeug.utils import secure_filename
from collections import defaultdict
import os

bp = Blueprint("admin", __name__)

## Action ##

@bp.route("/")
@login_required
def dashboard():
    return render_template("admin/admin_panel.html")

@bp.route("/f_impl/<int:function_id>", methods=["GET", "POST"])
def edit_function_impl(function_id):
    fn = FunctionImpl.query.get_or_404(function_id)
    families = FunctionFamily.query.order_by(FunctionFamily.display_name).all()
    datasets = Dataset.query.order_by(Dataset.name, Dataset.version).all()

    if request.method == "POST":
        fn.real_name = request.form["real_name"]
        fn.api_level = request.form["api_level"]
        fn.family_id = int(request.form["family_id"])

        default_dataset_id = request.form.get("default_dataset_id")
        fn.default_dataset_id = (
            int(default_dataset_id) if default_dataset_id else None
        )

        fn.signature_html = request.form.get("signature_html")
        fn.description_html = request.form.get("description_html")

        db.session.commit()

        return redirect(url_for("admin.dashboard", function_id=fn.id))

    return render_template(
        "admin/actions/edit_function_impl.html",
        fn=fn,
        families=families,
        datasets=datasets,
    )

@bp.route("/f_impl/<int:function_id>/delete", methods=["POST"])
def delete_function_impl(function_id):
    fn = FunctionImpl.query.get_or_404(function_id)

    db.session.delete(fn)
    db.session.commit()

    return redirect(url_for("admin.show_function_impl"))

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
            default_dataset_id=(
                int(request.form["default_dataset_id"])
                if request.form.get("default_dataset_id")
                else None
            ),
        )

        db.session.add(fn)
        db.session.commit()

        # Redirect to edit page immediately
        return redirect(url_for("admin.show_function_impl", function_id=fn.id))

    return render_template(
        "admin/actions/add_function_impl.html",
        families=families,
        datasets=datasets,
    )

@bp.route("/f_bench/<int:function_id>", methods=["GET", "POST"])
def edit_bench(function_id):
    fn = FunctionImpl.query.get_or_404(function_id)

    if request.method == "POST":
        benchmark_id = request.form.get("benchmark_id")
        title = request.form.get("title")
        description_html = request.form.get("description_html")

        bench = Benchmark.query.get_or_404(benchmark_id)
        bench.title = title
        bench.description_html = description_html

        db.session.commit()

        return redirect(url_for("admin.dashboard"))

    benchmark = (
        Benchmark.query
        .filter_by(function_impl_id=function_id)
        .first()
    )

    return render_template(
        "admin/actions/edit_function_benchmarks.html",
        fn=fn,
        benchmark=benchmark,
    )

@bp.route("/f_impl/<int:function_id>/delete", methods=["POST"])
def delete_function_bench(function_id):
    fn = Benchmark.query.get_or_404(function_id)

    db.session.delete(fn)
    db.session.commit()

    return redirect(url_for("admin.dashboard"))

@bp.route("/f_bench/add", methods=["GET", "POST"])
@login_required
def add_function_benchmark():

    # FunctionImpls that DO NOT already have a benchmark
    functions_without_bench = (
        FunctionImpl.query
        .outerjoin(Benchmark)
        .filter(Benchmark.id.is_(None))
        .order_by(FunctionImpl.real_name)
        .all()
    )

    if request.method == "POST":
        function_impl_id = int(request.form["function_impl_id"])

        bench = Benchmark(
            function_impl_id=function_impl_id,
            title=request.form["title"],
            description_html=request.form["description_html"],
        )

        db.session.add(bench)
        db.session.commit()

        return redirect(url_for("admin.dashboard"))

    return render_template(
        "admin/actions/add_function_benchmarks.html",
        functions=functions_without_bench,
    )

@bp.route("/benchmark/<int:benchmark_id>/datasets", methods=["GET", "POST"])
def edit_benchmark_datasets(benchmark_id):
    benchmark = Benchmark.query.get_or_404(benchmark_id)
    all_datasets = Dataset.query.all()

    if request.method == "POST":
        selected_ids = request.form.getlist("dataset_ids")

        # Clear existing associations
        BenchmarkDataset.query.filter_by(
            benchmark_id=benchmark.id
        ).delete()

        # Add new associations
        for ds_id in selected_ids:
            db.session.add(
                BenchmarkDataset(
                    benchmark_id=benchmark.id,
                    dataset_id=int(ds_id)
                )
            )

        db.session.commit()

        return redirect(
            url_for("admin.show_benchs", function_id=benchmark.function_impl_id)
        )

    return render_template(
        "admin/actions/edit_benchmark_datasets.html",
        benchmark=benchmark,
        all_datasets=all_datasets,
    )

@bp.route("/datasets/edit", methods=["GET"])
def edit_datasets():
    datasets = Dataset.query.order_by(
        Dataset.created_at.desc()
    ).all()

    return render_template(
        "admin/actions/edit_datasets.html",
        datasets=datasets,
    )

@bp.route("/datasets/<int:dataset_id>/edit", methods=["GET", "POST"])
def edit_dataset(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)

    if request.method == "POST":
        dataset.name = request.form["name"]
        dataset.version = request.form["version"]
        dataset.description = request.form.get("description")

        db.session.commit()
        return redirect(url_for("admin.edit_datasets"))

    return render_template(
        "admin/actions/edit_dataset.html",
        dataset=dataset,
    )

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

        dataset_dir = os.path.join(
            current_app.root_path,
            "static",
            "datasets"
        )
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

        return redirect(url_for("admin.edit_datasets"))

    datasets = Dataset.query.order_by(Dataset.created_at.desc()).all()

    return render_template(
        "admin/actions/add_datasets.html",
        datasets=datasets,
    )

@bp.route("/datasets/<int:dataset_id>/delete", methods=["POST"])
def delete_dataset(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)

    # Check if dataset is used
    usage_count = (
        BenchmarkDataset.query
        .filter_by(dataset_id=dataset.id)
        .count()
    )

    if usage_count > 0:
        abort(400, "Dataset is still used by benchmarks")

    # Remove file from filesystem
    if dataset.download_url:
        file_path = os.path.join(
            current_app.root_path,
            dataset.download_url.lstrip("/")
        )
        if os.path.exists(file_path):
            os.remove(file_path)

    db.session.delete(dataset)
    db.session.commit()

    return redirect(url_for("admin.edit_datasets"))

@bp.route("/taxonomy", methods=["GET", "POST"])
def taxonomy():
    families = FunctionFamily.query.order_by(
        FunctionFamily.display_name
    ).all()

    functions = FunctionImpl.query.order_by(
        FunctionImpl.real_name
    ).all()

    if request.method == "POST":
        for fn in functions:
            field_name = f"family_{fn.id}"
            new_family_id = request.form.get(field_name)

            if new_family_id and int(new_family_id) != fn.family_id:
                fn.family_id = int(new_family_id)

        db.session.commit()

        return redirect(url_for("admin.dashboard"))

    # Group functions by current family
    grouped = defaultdict(list)
    for fn in functions:
        grouped[fn.family_id].append(fn)

    return render_template(
        "admin/actions/taxonomy.html",
        families=families,
        grouped_functions=grouped,
    )

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

        return redirect(url_for("admin.show_function_family"))

    families = (
        FunctionFamily.query
        .order_by(FunctionFamily.display_name)
        .all()
    )

    return render_template(
        "admin/actions/add_function_family.html",
        families=families,
    )

@bp.route("/function_family/<int:family_id>", methods=["GET", "POST"])
def edit_function_family(family_id):
    family = FunctionFamily.query.get_or_404(family_id)

    if request.method == "POST":
        family.slug = request.form["slug"]
        family.display_name = request.form["display_name"]
        family.description = request.form.get("description")

        db.session.commit()

        return redirect(url_for("admin.show_function_family"))

    return render_template(
        "admin/actions/edit_function_family.html",
        family=family,
    )

@bp.route("/function_family/<int:family_id>/delete", methods=["POST"])
def delete_function_family(family_id):
    family = FunctionFamily.query.get_or_404(family_id)

    usage = (
        FunctionImpl.query
        .filter_by(family_id=family.id)
        .count()
    )

    if usage > 0:
        abort(400, "Family still has functions assigned")

    db.session.delete(family)
    db.session.commit()

    return redirect(url_for("admin.add_function_family"))


## SHOW ##

@bp.route("/datasets/show", methods=["GET"])
def show_datasets():
    datasets = Dataset.query.order_by(
        Dataset.created_at.desc()
    ).all()

    return render_template(
        "admin/show/datasets.html",
        datasets=datasets,
    )

@bp.route("/function_family/show", methods=["GET"])
def show_function_family():
    families = FunctionFamily.query.order_by(
        FunctionFamily.display_name
    ).all()

    return render_template(
        "admin/show/function_family.html",
        families=families,
    )

@bp.route("/function_impl/show", methods=["GET"])
def show_function_impl():
    functions = (
        FunctionImpl.query
        .order_by(FunctionImpl.real_name)
        .all()
    )

    return render_template(
        "admin/show/function_impl.html",
        functions=functions,
    )

@bp.route("/benchmarks/show", methods=["GET"])
def show_benchs():
    benchmarks = (
        Benchmark.query
        .join(FunctionImpl)
        .order_by(FunctionImpl.real_name)
        .all()
    )

    return render_template(
        "admin/show/benchmarks.html",
        benchmarks=benchmarks,
    )

@bp.route("/dev/show", methods=["GET"])
def show_dev():
    articles = (
        Dev.query
        .order_by(Dev.created_at.desc())
        .all()
    )
    
    return render_template(
        "admin/show/dev.html",
        articles=articles,
    )

@bp.route("/dev/add", methods=["GET", "POST"])
def add_dev():
    if request.method == "POST":
        article = Dev(
            title=request.form["title"],
            description_html=request.form.get("description_html"),
        )
        db.session.add(article)
        db.session.commit()

        return redirect(url_for("admin.show_dev"))

    return render_template(
        "admin/actions/add_dev.html"
    )

@bp.route("/dev/<int:article_id>", methods=["GET", "POST"])
def edit_dev(article_id):

    fn = Dev.query.get_or_404(article_id)
    
    if request.method == "POST":
        fn.title            = request.form["title"]
        fn.description_html = request.form.get("description_html")

        db.session.commit()

        return redirect(url_for("admin.show_dev"))

    return render_template(
        "admin/actions/edit_dev.html",
        title=fn.title,
        description_html=fn.description_html
    )







