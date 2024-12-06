from flask import Blueprint, render_template

bp = Blueprint("main", __name__)


@bp.route("/")
def home():
    return render_template("index.html", title="Dunamis Max")


@bp.route("/blog")
def blog():
    return render_template("blog.html", title="Blog")
