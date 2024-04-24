from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, EqualTo, Email


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=20)])
    password = StringField("Password", validators=[DataRequired(), Length(max=100)])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=20)])
    email = StringField("Email", validators=[DataRequired(), Length(max=50), Email()])
    password = StringField(
        "Password",
        validators=[
            DataRequired(),
            Length(max=100),
            EqualTo(fieldname="confirmPassword", message="Your Passwords Do Not Match"),
        ],
    )
    confirmPassword = StringField(
        "Confirm Password", validators=[DataRequired(), Length(max=100)]
    )
    submit = SubmitField("Register")

    
class VehicleForm(FlaskForm):
    vehicle_model = StringField("Model", validators=[DataRequired(), Length(max=20)])
    license_plate = StringField("License Plate", validators=[DataRequired(), Length(max=100)])
    submit = SubmitField("Login")
