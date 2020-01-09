from flask import render_template, url_for, request, flash, redirect
from varkapp import app, db, bcrypt
from varkapp.forms import RegistrationForm, LoginForm
from varkapp.models import get_content, User
from flask_login import login_user, current_user, logout_user, login_required
import pdfplumber
import re

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    chapter, topic, content = get_content()
    return render_template('index.html', title = "VARK", chapter=chapter, topic=topic, content=content)

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    title = "Registration"
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(studentid=form.studentid.data, firstname=form.firstname.data, 
                    lastname=form.lastname.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('registration.html', title = title, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    title = "Sign In"
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', title=title, form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/exercise/', methods=['GET', 'POST'])
def exercise():
    
    if request.method == 'POST':
        quiz_number = request.form.get('quiz_number')
        select_choice = []
        for select in range(1, int(quiz_number)+1):
            select_choice.append(request.form['choice'+str(select)])
        print(select_choice)
        return redirect(url_for('index'))
    else:
        testfile = request.args.get('testfile', default='', type=str)
        pdf = pdfplumber.open("varkapp/"+testfile)
        text = []
        for page in range(0, len(pdf.pages)):
            pages = pdf.pages[page].extract_text().splitlines()
            for line in pages:
                my_new_string = re.sub('�', 'า', line)
                text.append(my_new_string)
    
        return render_template('exercise.html', content = text)