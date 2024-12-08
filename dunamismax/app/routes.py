from flask import Blueprint, render_template, flash, redirect, url_for
from .forms import ContactForm

bp = Blueprint("main", __name__)


@bp.route("/")
def home():
    return render_template("index.html", title="Dunamis Max")


@bp.route("/blog")
def blog():
    return render_template("blog.html", title="Blog")


@bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # Process the form data (e.g., send an email or store in database)
        flash("Thank you for your message! We will get back to you soon.", "success")
        return redirect(url_for("main.contact"))
    return render_template("contact.html", title="Contact Us", form=form)
