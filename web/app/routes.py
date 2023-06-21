from app import app
from flask import render_template, request, jsonify, redirect, flash, url_for
import time
from app.models.forms import *
from app.instances import *
from app.functions import *

#============================================Truely Routes============================================
#PRINTER DASHBOARD
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

    # Name and baurate change
    form = SettingsForm()

    database_get = db.collection(current_user.uid).document(current_user.current).get().to_dict()
    name = database_get['name']  
    baudrate = database_get['baudrate']

    if request.method == 'POST':
        form_type = request.form.get('form-type')

        if form_type == 'name-form':
            name = form.new_name.data
            db.collection(current_user.uid).document(current_user.current).update({'name': name})
            flash('Nome alterado com sucesso.')

        elif form_type == 'baudrate-form':
            baudrate = form.baudrate.data
            db.collection(current_user.uid).document(current_user.current).update({'baudrate': baudrate})
            flash('Taxa de trasmissão alterada com sucesso')

        elif form_type == 'delete-form':
            if form.delete.data == current_user.current:
                db.collection(current_user.uid).document(current_user.current).delete()
                flash('Dispositivo removido com sucesso.')
                return redirect(url_for('devices'))

    form.new_name.data = name
    form.baudrate.data = baudrate

    # Mobile/Desktop responsiviness
    user_agent = request.headers.get('User-Agent')

    if 'Mobile' in user_agent:
        dashboard_page = 'dashboard-mobile.html'
    else:
        dashboard_page = 'dashboard-desktop.html'

    return render_template(dashboard_page, hash=current_user.current, name=name, baud=baudrate, form=form)

#-----------------------------------------------------------------------------------------------------
#REGISTERED DEVICES
@app.route('/devices')
@login_required
def devices():
    devices = db.collection(current_user.uid).get()

    return render_template('devices.html', devices=devices)

#-----------------------------------------------------------------------------------------------------
#NEW DEVICE
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
        flash('Dispositivo cadastrado com sucesso.')
        return redirect(url_for('devices'))

    return render_template('new_device.html', form=form)

#-----------------------------------------------------------------------------------------------------
#ROOT/HOME
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

#-----------------------------------------------------------------------------------------------------
#LOGIN
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

#-----------------------------------------------------------------------------------------------------
#SIGNUP
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

#-----------------------------------------------------------------------------------------------------
#USER DASHBOARD/EDIT USER
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
#=====================================================================================================

#========================================Only Function's Routes=======================================
#CONNECT(BOOT)
@app.route('/connect')
@login_required
def connect():
    if get_status() == 'idle':
        db.collection(current_user.uid).document(current_user.current).update({'status': 'boot'})        
    return ''

#-----------------------------------------------------------------------------------------------------
#DELETE(ADM FUNCTION)
@app.route('/delete')
def delete():

    user = User.query.order_by(User.id).all()

    for i in user:
        dbUser.session.delete(i)
        dbUser.session.commit()

    return redirect(url_for('login'))

#-----------------------------------------------------------------------------------------------------
#DISCONNECT
@app.route('/disconnect')
@login_required
def disconnect():
    if get_status() == 'ready':
        db.collection(current_user.uid).document(current_user.current).update({'status': 'disconnect',
                                                                               'updated': 'status'})
    return ''

#-----------------------------------------------------------------------------------------------------
@app.route('/get-status')
@login_required
def get_status_route():
    status = db.collection(current_user.uid).document(current_user.current).get().to_dict()['status']
    return jsonify(status=status)

#-----------------------------------------------------------------------------------------------------
#GET TEMPERATURE
@app.route('/get-temp', methods=['GET'])
@login_required
def get_temp():

    temp = db.collection(current_user.uid).document(current_user.current).get()
    temp_ex = temp.to_dict()['hotend']['current']
    temp_bed = temp.to_dict()['heatbed']['current']
    temp_ex_ref = temp.to_dict()['hotend']['setpoint']
    temp_bed_ref = temp.to_dict()['heatbed']['setpoint']
    status = temp.to_dict()['status']
    delay = 1000

    match status:
        case 'ready':
            status = 'Pronto'
        case 'idle':
            status = 'Desconectado'
        case 'printing':
            status = 'Imprimindo'
        case 'paused':
            status = 'Pausado'
        case 'boot':
            status = 'Conectando...'
        case 'busy':
            status = 'Ocupado'
        case _:
            status = 'None'

    return jsonify(temp_ex=temp_ex, 
                   temp_bed=temp_bed, 
                   delay=delay, 
                   status=status, 
                   temp_ex_ref=temp_ex_ref, 
                   temp_bed_ref=temp_bed_ref)

#-----------------------------------------------------------------------------------------------------
#LOGOUT
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("Logout feito com sucesso.")
    return redirect(url_for('login'))

#-----------------------------------------------------------------------------------------------------
#PAUSE PRINTING
@app.route('/pause')
@login_required
def pause():
    if get_status() == 'printing':
        db.collection(current_user.uid).document(current_user.current).update({'status': 'pause-print',
                                                                               'updated': 'status'})
    return ''

#-----------------------------------------------------------------------------------------------------
#GCODE PERSONALIZED
@app.route('/personalized', methods=['POST'])
@login_required
def personalized():

    if get_status() in ['ready', 'paused']:
        value = request.form.get("gCode")
        if value:
            db.collection(current_user.uid).document(current_user.current).update({'command':str(value), 
                                                                                'updated' : 'command'})
    return ''

#-----------------------------------------------------------------------------------------------------
#MOVE CONTROLLERS
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

#-----------------------------------------------------------------------------------------------------
#SET TEMP EXT
@app.route('/set-temp-ex', methods=['POST'])
@login_required
def set_temp_ex():
    if get_status() in ['ready', 'paused']:
        setTempEx = request.form.get("setTempEx")
        print(setTempEx)
        if setTempEx:
            db.collection(current_user.uid).document(current_user.current).update({'command':f'M104 S{setTempEx}',
                                                                                    'updated' : 'command'})
    return ''

#-----------------------------------------------------------------------------------------------------
#SET TEMP BED
@app.route('/set-temp-bed', methods=['POST'])
@login_required
def set_temp_bed():
    if get_status() in ['ready', 'paused']:
        setTempBed = request.form.get("setTempBed")
        if setTempBed:
            db.collection(current_user.uid).document(current_user.current).update({'command':f'M140 S{setTempBed}',
                                                                                    'updated' : 'command'})
    return ''

#-----------------------------------------------------------------------------------------------------
#SET TEMP BED
@app.route('/default-commands', methods=['POST'])
@login_required
def default_commands():
    if get_status() in ['ready', 'paused']:
        value = request.form.get("value")
        command = request.form.get('command')

        match command:
            case 'homing':
                if value != 'A':
                    db.collection(current_user.uid).document(current_user.current).update({'command':f'G28 {value}',
                                                                                            'updated' : 'command'})
                else:
                    db.collection(current_user.uid).document(current_user.current).update({'command':'G28',
                                                                                            'updated' : 'command'})
            case 'disable_steppers':
                db.collection(current_user.uid).document(current_user.current).update({'command':'M18',
                                                                                            'updated' : 'command'})
            case _:
                pass

    return ''

#-----------------------------------------------------------------------------------------------------
#START PRINTING/RESUME PRINTING
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

#-----------------------------------------------------------------------------------------------------
#STOP PRINTING
@app.route('/stop')
@login_required
def stop():
    if get_status() in ['printing', 'paused']:
        db.collection(current_user.uid).document(current_user.current).update({'status': 'stop-print',
                                                                               'updated': 'status'})
    return ''

#-----------------------------------------------------------------------------------------------------
#STREAMING VIEW CONTROLLER
@app.route('/toggle-streaming')
@login_required
def toggle_streaming():

    test = db.collection(current_user.uid).document(current_user.current).get().to_dict()['streaming'] == False
    db.collection(current_user.uid).document(current_user.current).update({'streaming': test, 'updated':'streaming'})

    return ''

#-----------------------------------------------------------------------------------------------------
#UPLOAD FILE
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


#=====================================================================================================