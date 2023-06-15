from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, BooleanField, ValidationError, SelectField
from wtforms.validators import DataRequired, EqualTo, Length

class RegisterForm(FlaskForm):
    name = StringField("Nome", validators=[DataRequired(), Length(max=25)])
    email = EmailField("Email", validators=[DataRequired()])
    password1 = PasswordField("Senha", validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField("Confirmação de Senha", validators=[DataRequired(),
                                                                  EqualTo('password1', message='As senhas devem ser iguais.'),
                                                                  Length(min=8)])
    submit = SubmitField("Registrar")

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Entrar")   

class NewDeviceForm(FlaskForm):
    id = StringField("ID", validators=[DataRequired()])
    name = StringField("Nome", validators=[DataRequired(), Length(max=15)])
    baud = SelectField("Taxa de transmissão (bps)", validators=[DataRequired()], 
                       choices=['9600', '19200', '250000'], coerce=int)
    submit = SubmitField("Adicionar")

class UserFormPassword(FlaskForm):
    #name = StringField("Nome", validators=[DataRequired(), Length(max=25)])
    old_password = PasswordField("Senha antiga")
    new_password = PasswordField("Nova senha", validators=[Length(min=8)])
    new_password2 = PasswordField("Confirmação de senha", 
                                  validators=[
                                              EqualTo('new_password', message='As senhas devem ser iguais.'),
                                              Length(min=8)])
    submit = SubmitField("Editar")

class UserFormName(FlaskForm):
    name = StringField("Nome", validators=[DataRequired(), Length(max=25)])