from app import app
from flask import render_template, request, jsonify, redirect, flash, url_for
from firebase_admin import credentials, initialize_app, storage, firestore
import os
import time
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
import hashlib

from app.models.forms import *

#=====================Firebase=======================================
cred = credentials.Certificate(os.environ.get('FIREBASE_KEY_PATH'))
initialize_app(cred, {'storageBucket': os.environ.get('FIREBASE_BUCKET_PATH')})
#====================================================================

#================================Instancia Firebase==================
db = firestore.client()
bucket = storage.bucket()
#====================================================================

#=====================Banco de Dados Usuários========================
dbUser = SQLAlchemy(app)
migrate = Migrate(app, dbUser, render_as_batch=True)
#====================================================================

#========================Inicialização FlaskLogin====================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Acesso negado.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
#====================================================================

#===================Classe Tabela Banco de Dados===============================
class User(dbUser.Model, UserMixin):
    id = dbUser.Column(dbUser.Integer, primary_key=True)
    uid = dbUser.Column(dbUser.String, nullable = False, unique = True)
    name = dbUser.Column(dbUser.String(100), nullable = False)
    email = dbUser.Column(dbUser.String(100), nullable = False, unique = True)
    password_hash = dbUser.Column(dbUser.String(100), nullable = False)
    current = dbUser.Column(dbUser.String(100))
    date_added = dbUser.Column(dbUser.DateTime, default = datetime.utcnow)

    def __init__(self, name, email, password, uid):
        self.name = name
        self.email = email
        self.password_hash = password
        self.uid = uid

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return '<Name %r>' % self.name
#======================================================================

#=====================Hash email=======================================
def hash_email(email):
    return hashlib.sha256(email.encode('utf-8')).hexdigest()
#======================================================================

def get_status() -> str:
    return db.collection(current_user.uid).document(current_user.current).get().to_dict()['status']

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def info():
    buffer = current_user.current
    if not buffer:
        flash('Sem dispositivos cadastrados.')
        return redirect(url_for('devices'))
    current_user.current = str(request.form.get("deviceId"))
    if current_user.current != 'None':
        dbUser.session.commit()
    else:
        current_user.current = buffer

    name = db.collection(current_user.uid).document(current_user.current).get().to_dict()['name']
    db.collection(current_user.uid).document(current_user.current).update({'streaming': False, 
                                                                           'updated':'streaming'})
    return render_template('dashboard.html', name=name)

@app.route('/personalized', methods=['POST'])
@login_required
def personalized():

    if get_status() in ['ready', 'paused']:
        value = request.form.get("gCode")
        if value:
            db.collection(current_user.uid).document(current_user.current).update({'command':str(value), 
                                                                                'updated' : 'command'})
    return ''

@app.route('/position', methods=['POST'])
@login_required
def position():
    if get_status() in ['ready', 'paused']:
        value = request.form.get("value")
        step = request.form.get('step')
        if value:
            db.collection(current_user.uid).document(current_user.current).update({'command':f'G91_G0 {value}{step}_G90',
                                                                                    'updated' : 'command'})
    return ''

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'arquivo' in request.files:
            arquivo = request.files['arquivo']
            if arquivo.filename.split('.')[1] == 'gcode':
                arquivo.save('./files/' + arquivo.filename)
                blob = bucket.blob(current_user.uid+'/'+current_user.current+'/printfile.gcode')
                blob.upload_from_filename("files/" + arquivo.filename)
                os.remove("./files/" + arquivo.filename)
    return ''
    
@app.route('/get-temp', methods=['GET'])
@login_required
def get_temp():

    temp = db.collection(current_user.uid).document(current_user.current).get()
    temp_ex = temp.to_dict()['hotend']['current']
    temp_bed = temp.to_dict()['heatbed']['current']
    delay = 60000

    return jsonify(temp_ex=temp_ex, temp_bed=temp_bed, delay=delay)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                return redirect(url_for('devices'))
        flash('Email ou senha inválidos.')       

    return render_template('login.html', form=form)
     
@app.route('/signup', methods = ['GET', 'POST'])
def new_user():
    form = RegisterForm()

    if form.validate_on_submit():
        if not User.query.filter_by(email=form.email.data).all():
            password = generate_password_hash(form.password1.data, 'scrypt')
            uid = hash_email(form.email.data)
            user = User(form.name.data, form.email.data, password, uid)
            dbUser.session.add(user)
            dbUser.session.commit()

            flash('Cadastro feito com sucesso.')
            return redirect(url_for('login'))
        
        flash('Email já cadastrado.')

    return render_template('signup.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("Logout feito com sucesso.")
    return redirect(url_for('login'))

@app.route('/delete')
def delete():

    user = User.query.order_by(User.id).all()

    for i in user:
        dbUser.session.delete(i)
        dbUser.session.commit()

    return redirect(url_for('login'))

@app.route('/devices/new-device', methods=['GET', 'POST'])
@login_required
def new_device():
    form = NewDeviceForm()

    if form.validate_on_submit():
        try:
            db.collection("QueuedRaspberrys").document(form.id.data).update({'user':current_user.uid, 
                                                                            'name': form.name.data, 
                                                                            'baudrate': form.baud.data,
                                                                            'icon': request.form['campo']})
        except:
            flash('ID inválido.')
            return render_template('new_device.html', form=form)

        time.sleep(4)
        return redirect(url_for('devices'))

    return render_template('new_device.html', form=form)

@app.route('/devices')
@login_required
def devices():
    devices = db.collection(current_user.uid).get()

    return render_template('devices.html', devices=devices)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    form_pass = UserFormPassword()
    form_name = UserFormName()

    if form_name.validate_on_submit():
        if not current_user.name == form_name.name.data:
            current_user.name = form_name.name.data
            dbUser.session.commit()
            flash('Nome alterado com sucesso.')

    if form_pass.validate_on_submit():
        if check_password_hash(current_user.password_hash, form_pass.old_password.data):
            current_user.password_hash = generate_password_hash(form_pass.new_password.data, 'scrypt')
            dbUser.session.commit()
            flash('Senha alterada com sucesso.')
        else:
            flash('Senha antiga inválida.')
    return render_template('user.html', 
                           form_pass=form_pass, 
                           form_name=form_name, 
                           email=current_user.email, 
                           name=current_user.name)

@app.route('/toggle-streaming')
@login_required
def toggle_streaming():

    test = db.collection(current_user.uid).document(current_user.current).get().to_dict()['streaming'] == False
    db.collection(current_user.uid).document(current_user.current).update({'streaming': test, 'updated':'streaming'})

    return ''

@app.route('/connect')
@login_required
def connect():
    if get_status() == 'idle':
        db.collection(current_user.uid).document(current_user.current).update({'status': 'boot'})        
    return ''

@app.route('/disconnect')
@login_required
def disconnect():
    if get_status() == 'ready':
        db.collection(current_user.uid).document(current_user.current).update({'status': 'disconnect',
                                                                               'updated': 'status'})
    return ''

@app.route('/start')
@login_required
def start():
    if get_status() == 'ready':
        db.collection(current_user.uid).document(current_user.current).update({'status': 'start-print',
                                                                               'updated': 'status'})
    elif get_status() == 'paused':
        db.collection(current_user.uid).document(current_user.current).update({'status': 'resume-print',
                                                                               'updated': 'status'})
    return ''

@app.route('/pause')
@login_required
def pause():
    if get_status() == 'printing':
        db.collection(current_user.uid).document(current_user.current).update({'status': 'pause-print',
                                                                               'updated': 'status'})
    return ''

@app.route('/stop')
@login_required
def stop():
    if get_status() in ['printing', 'paused']:
        db.collection(current_user.uid).document(current_user.current).update({'status': 'stop-print',
                                                                               'updated': 'status'})
    return ''