from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from models.admin_user import AdminUser

bp = Blueprint("auth", __name__)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = AdminUser.query.filter_by(
            username=request.form["username"]
        ).first()

        if user and check_password_hash(user.password_hash, request.form["password"]):
            login_user(user)
            session.permanent = True
            return redirect(url_for("admin.dashboard"))

    return render_template("login.html")

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))


