from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Length


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    subject = StringField("Subject", validators=[DataRequired(), Length(max=150)])
    message = TextAreaField(
        "Message", validators=[DataRequired(), Length(min=10, max=500)]
    )
    submit = SubmitField("Send Message")
