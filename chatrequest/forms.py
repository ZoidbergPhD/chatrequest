from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SignUpForm(FlaskForm):

    rsn = StringField('Username', validators=[DataRequired('Enter your Runescape display name.')], render_kw={'maxlength': 12})
    recaptcha = RecaptchaField()
    submit = SubmitField('Submit')
