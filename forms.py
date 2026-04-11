from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=4, max=20)])
    submit = SubmitField('Ingresar')