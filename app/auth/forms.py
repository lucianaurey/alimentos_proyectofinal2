from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField(
        "Correo electrónico",
        validators=[DataRequired(message="El correo es obligatorio."), Length(max=160)],
    )
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(message="La contraseña es obligatoria."), Length(max=128)],
    )
    rol = SelectField(
        "Rol de acceso",
        choices=[
            ("admin",       "Administrador"),
            ("empleado",    "Empleado"),
            ("repartidor",  "Repartidor"),
        ],
        validators=[DataRequired()],
    )
    remember = BooleanField("Recordarme")
    submit   = SubmitField("Acceder al sistema")