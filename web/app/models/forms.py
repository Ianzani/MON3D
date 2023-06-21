from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, BooleanField, ValidationError, SelectField
from wtforms.validators import DataRequired, EqualTo, Length

baudrate_choices = [
    9600,
    19200,
    38400,
    57600,
    74880,
    115200,
    230400,
    250000,
    500000,
    750000,
    1000000
]

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
    name = StringField("Nome", validators=[DataRequired(), Length(max=16)])
    baud = SelectField("Taxa de transmissão (bps)", validators=[DataRequired()], 
                       choices=baudrate_choices, coerce=int)
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

class SettingsForm(FlaskForm):
    new_name = StringField("Nome do Dispositivo", validators=[DataRequired(), Length(max=16)])
    baudrate = SelectField("Taxa de transmissão (bps)", validators=[DataRequired()], 
                       choices=baudrate_choices, coerce=int)
    delete = StringField("", validators=[DataRequired()])

    submit = SubmitField("Salvar")

