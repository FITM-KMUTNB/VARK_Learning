from flask import render_template, url_for, request, flash, redirect, jsonify
from varkapp import app, db, bcrypt
from varkapp.forms import RegistrationForm, LoginForm
from varkapp.models import get_content, User, Topic, Exercise
from flask_login import login_user, current_user, logout_user, login_required
import pdfplumber
import glob
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    chapter, topic, content = get_content()
    
    return render_template('index.html', title = "VARK", chapter=chapter, topic=topic, content=content,\
    Exercise=Exercise, User=User, Topic=Topic)

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    title = "Registration"
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(gender=form.gender.data, firstname=form.firstname.data, 
                    lastname=form.lastname.data, age=form.age.data, email=form.email.data, password=hashed_password, user_type='User')
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

testfile = dict()
chapterid = dict()
topicid = dict()
learntype = dict()
@app.route('/exercise/', methods=['GET', 'POST'])
def exercise():
    global testfile
    global topicid
    global chapterid
    global learntype
    #receive answer from template
    if request.method == 'POST':

        # get choice from template
        quiz_number = request.form.get('quiz_number')
        select_choice = []
        for select in range(1, int(quiz_number)+1):
            select_choice.append(request.form['choice'+str(select)].replace(".",""))
        
        # get anwser file path
        file_path = testfile[current_user.email].split("/")
        del file_path[-1]
        answer_file = "varkapp/"
        for p in range(len(file_path)):
            answer_file += file_path[p]+"/"
              
        for file in glob.glob(answer_file+"/*.txt"):
            answer_file = file

        # read answer in text file
        Text_file = open(answer_file, 'r')
        answer_choice = []
        for check_c in Text_file:
            check_c = check_c.replace("\n","")
      
            if len(check_c.split()) > 1:
                ans, topic = check_c.split()
            else:
                ans = check_c
            answer_choice.append(ans)
        
        # check score
        full_point = len(answer_choice)
        get_points = 0
        for ans in range(len(answer_choice)):
            if select_choice[ans] == answer_choice[ans]:
                get_points += 1
        
        # commit to database
        db_topicid = Topic.query.filter_by(chapter_id=chapterid[current_user.email], number=topicid[current_user.email]).first().id
        userid = User.query.filter_by(email=current_user.email).first().id
        
        # Add to Exercise table
        exerciseDB = Exercise.query.filter_by(user_id=userid, topic_id=db_topicid).first()
        # if this exercise have done before --> update score
        if exerciseDB:
            print(exerciseDB, " : Exercise exist!")
            percent = (get_points/full_point) * 100
            exerciseDB.learntype = learntype[current_user.email]
            exerciseDB.getpoint = get_points
            exerciseDB.percent = percent
            db.session.commit()
            print("Update database.")
            print(Exercise.query.filter_by(user_id=userid, topic_id=db_topicid).first())
        # add new exercise score
        else:
            if learntype[current_user.email] == None:
                learntype[current_user.email] = "-"
            percent = (get_points/full_point) * 100
            exerciseDB = Exercise(learntype=learntype[current_user.email], fullpoint=full_point, getpoint=get_points,percent=percent,\
                                    user_id=userid, topic_id=db_topicid)
            db.session.add(exerciseDB)
            db.session.commit()
            print(Topic.query.filter_by(id=db_topicid).first(), " : Submit")

        # Exercise Result
     
        print("User : ",  User.query.filter_by(email=current_user.email).first().firstname)
        print("Select : ", select_choice)
        print("Answer : ", answer_choice)
        print("Learn type : ", learntype[current_user.email])
        print("correct : ", get_points)

        return redirect(url_for('index'))

    # display excercise
    else:
        # question number for check question line in text.
        q_number = []
        for num in range(1,20):
            q_number.append(str(num))
            q_number.append(str(num)+'.')
            for num2 in range(1,20):
                for num3 in range(1,20):
                    q_number.append(str(num)+"."+str(num2)+"."+str(num3))
        
        # extract exercise file
        testfile[current_user.email] = request.args.get('testfile', default='', type=str)

        # keep chapter id and topic id for query in database.
        chapterid[current_user.email] = request.args.get('chapterid', default='', type=str)
        topicid[current_user.email] = request.args.get('topicid', default='', type=str)
    
        pdf = pdfplumber.open("varkapp/"+testfile[current_user.email])
        print(testfile[current_user.email])
        text = []
        for page in range(0, len(pdf.pages)):
            pages = pdf.pages[page].extract_text().splitlines()
            for line in pages:
                
                # Replace "า" to '�' if before '�' is not 'ำ"
                if '�' in line:
                    my_new_string = ""
                    cutt = line.split("�")
                      
                    for index in range(len(cutt)):
                        if len(cutt[index]) > 0:
                            prev_char = len(cutt[index])
                            if cutt[index][prev_char-1] != "ำ" and cutt[index][prev_char-1] != " " and index != len(cutt)-1:
                                my_new_string += cutt[index]+"า"
                                
                            else:
                                my_new_string += cutt[index]
                        
                    my_new_string2 = ""
                    
                    # Remove "า" in case if "ำา" exist in my_new_string
                    if 'า' in my_new_string:
                        cutt = my_new_string.split("า")
                        
                        for index in range(len(cutt)):
                            if len(cutt[index]) > 0:
                                prev_char = len(cutt[index])
                                if cutt[index][prev_char-1] != "ำ" and cutt[index][prev_char-1] != " " and index != len(cutt)-1:
                                    my_new_string2 += cutt[index]+"า"
                                    
                                else:
                                    my_new_string2 += cutt[index]
                        text.append(my_new_string2)      
                    else:
                        text.append(my_new_string)

                 # Remove "า" in case if "ำา" exist in line
                elif  'า' in line:
                    cutt = line.split("า")
                    my_new_string = "" 
                    for index in range(len(cutt)):
                        if len(cutt[index]) > 0:
                            prev_char = len(cutt[index])
                            if cutt[index][prev_char-1] != "ำ" and cutt[index][prev_char-1] != " " and index != len(cutt)-1:
                                my_new_string += cutt[index]+"า"
                                
                            else:
                                my_new_string += cutt[index]
                            
                    text.append(my_new_string)

                else:
                    text.append(line)

        #{ข้อ1 : {ก: choice, ข: choice}}
        exercise_content = dict() 
        tempt_choice = dict()
        question = None
        for t in range(len(text)):
            choice = ""
            line_cutt = text[t].split("\t")
            line_cutt = ' '.join(line_cutt).split()
          
            if line_cutt[0] in q_number:
                question = ""
                question += text[t]
                if t+1 < len(text):
                    check_newline = text[t+1].split("\t")
                    check_newline = ' '.join(check_newline).split()
                    if check_newline[0] not in ['ก.', 'ข.', 'ค.', 'ง.', 'ก', 'ข', 'ค', 'ง']:
                        question += '\n'+text[t+1]
                exercise_content[question] = None
               
            elif line_cutt[0] in ['ก.', 'ข.', 'ค.', 'ง.', 'ก', 'ข', 'ค', 'ง',]:
                for c in line_cutt[1:]:
                    choice += " "+c
              
                if t+1 < len(text):
                    check_newline = text[t+1].split("\t")
                    check_newline = ' '.join(check_newline).split()
                    if check_newline[0] not in ['ก.', 'ข.', 'ค.', 'ง.', 'ก', 'ข', 'ค', 'ง'] and \
                    check_newline[0] not in q_number:
                        choice += '\n'+text[t+1]
                      
                tempt_choice[line_cutt[0]] = choice
               
                if len(tempt_choice) == 4:
                    exercise_content[question] = tempt_choice
                    tempt_choice = dict()
     
        return render_template('exercise.html', content = exercise_content, title = text[0])

@app.route('/learn_type', methods=['GET','POST'])
def learn_type():
    global learntype
    learntype[current_user.email] = request.form['learntype']
    response = "Learning type : "+str(learntype[current_user.email])
    return jsonify({'response':response})