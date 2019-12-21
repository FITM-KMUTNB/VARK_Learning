
from flask import render_template, url_for, request, flash, redirect
from varkapp import app, db, bcrypt
from varkapp.forms import RegistrationForm, LoginForm
from varkapp.models import get_content, User

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    chapter, topic, content = get_content()
    return render_template('index.html', title = "VARK", chapter=chapter, topic=topic, content=content)

@app.route('/registration', methods=['GET', 'POST'])
def registration():
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
    title = "Sign In"
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')

    return render_template('login.html', title=title, form=form)


