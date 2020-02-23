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
    userid = User.query.filter_by(email=current_user.email).first().id
    exerciseDB = Exercise.query.filter_by(user_id=userid).all()
    chapter_sum = dict()
    allchapter_varkscore = dict()
    for cid in chapter:
        vark_chapter = dict()
        #print("Chapter :", cid)
        for tobj in Topic.query.filter_by(chapter_id=cid).all():
            exercise_list = Exercise.query.filter_by(user_id=userid, topic_id=tobj.id).all()
            if exercise_list:
                #print("Topic : ",tobj.number)
                for exobj in exercise_list:
                    if tobj.number != "P" and tobj.number != "T" :
                        if exobj.learntype == "-":
                            continue
                        if exobj.learntype not in vark_chapter:
                            vark_chapter[exobj.learntype] = [int(exobj.getpoint), int(exobj.fullpoint)]
                        else:
                            plusscore = vark_chapter[exobj.learntype][0] + int(exobj.getpoint)
                            allscore = vark_chapter[exobj.learntype][1] + int(exobj.fullpoint)
                            vark_chapter[exobj.learntype] = [plusscore, allscore]
                        #print(exobj.learntype, " : ", exobj.getpoint, "/", exobj.fullpoint)
                        #print(vark_chapter)
                    elif tobj.number == "T":
                        test_past = (int(exobj.getpoint)/int(exobj.fullpoint))*100
                        if test_past >= 50:
                            chapter_percent = dict()
                            # more that chapter 1, calculate sum of vark from chapter1 to current chapter.
                            if cid > 1:
                                vark_score = dict()
                                allchapter_varkscore[cid] = vark_chapter
                                for prevch in allchapter_varkscore:
                                    for vark in allchapter_varkscore[prevch]:
                                        if vark not in vark_score:
                                            topic_getpoint = allchapter_varkscore[prevch][vark][0]
                                            topic_fullpoint = allchapter_varkscore[prevch][vark][1]
                                            vark_score[vark] = [topic_getpoint, topic_fullpoint]
                                        else:
                                            topic_getpoint = allchapter_varkscore[prevch][vark][0]
                                            topic_fullpoint = allchapter_varkscore[prevch][vark][1]
                                            topic_pluspoint = vark_score[vark][0] + topic_getpoint
                                            topic_plusfull = vark_score[vark][1] + topic_fullpoint
                                            vark_score[vark] = [topic_pluspoint, topic_plusfull]

                                for vark in vark_score:
                                    percent = ( vark_score[vark][0]/ vark_score[vark][1])*100
                                    #print(vark," : ",percent, " %")
                                    chapter_percent[vark] = int(percent)
                                chapter_sum[cid] = chapter_percent

                            #chapter 1 vark percent
                            else:
                                for vark in vark_chapter:
                                    percent = ( vark_chapter[vark][0]/ vark_chapter[vark][1])*100
                                    #print(vark," : ",percent, " %")
                                    chapter_percent[vark] = int(percent)
                                allchapter_varkscore[cid] = vark_chapter
                                chapter_sum[cid] = chapter_percent
    # [getpoint, fullpoint]                        
    # {1: {'V': [3, 10], 'A': [0, 10], 'R': [13, 20], 'K': [0, 5]}, 2: {'R': [3, 5], 'V': [2, 5], 'A': [4, 5]}}
    #print(allchapter_varkscore)

    # vark percent of each chapters
    #print(chapter_sum)           
    """
    for ex in exerciseDB:
        db_topic = Topic.query.filter_by(id=ex.topic_id).first()
        print('Chapter : ', db_topic.chapter_id)
        topic_vark_score = Exercise.query.filter_by(user_id=userid, topic_id = ex.topic_id).all()
        for vark in topic_vark_score:
            print(vark.learntype, " : ", vark.getpoint, "/", vark.fullpoint)"""
    return render_template('index.html', title = "VARK", chapter=chapter, topic=topic, content=content,\
    Exercise=Exercise, User=User, Topic=Topic, chapter_sum = chapter_sum)

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

@app.route('/display_exercise', methods=['GET', 'POST'])
def display_exercise():
    if request.method == 'POST':
        # display excercise
        # question number for check question line in text.
        q_number = []
        for num in range(1,20):
            q_number.append(str(num))
            q_number.append(str(num)+'.')
            for num2 in range(1,20):
                for num3 in range(1,20):
                    q_number.append(str(num)+"."+str(num2)+"."+str(num3))

        # extract exercise file
        testfile= request.form['testfile']

        # keep chapter id and topic id for query in database.
        chapterid = request.form['chapterid']
        topicid = request.form['topicid']
        learntype = request.form['learntype']

        pdf = pdfplumber.open("varkapp/"+testfile)
        print(testfile)
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

        return render_template('exercise.html', content = exercise_content, title = text[0], testfile=testfile,\
                                chapterid=chapterid, topicid=topicid, learntype=learntype)

@app.route('/submit_exercise', methods=['GET', 'POST'])
def submit_exercise():

    #receive answer from template
    if request.method == 'POST':
        #print("Submit")
        # Request get from template
        quiz_number = request.form.get('quiz_number')
        testfile = request.form.get('testfile')
        chapterid = request.form.get('chapterid')
        topicid = request.form.get('topicid')
        learntype = request.form.get('learntype')
        if learntype == "":
                learntype = "-"

        select_choice = []
        for select in range(1, int(quiz_number)+1):
            select_choice.append(request.form['choice'+str(select)].replace(".",""))
        
        # get anwser file path
        file_path = testfile.split("/")
        del file_path[-1]
        answer_file = "varkapp/"
        for p in range(len(file_path)):
            answer_file += file_path[p]+"/"
            
        for file in glob.glob(answer_file+"/*.txt"):
            answer_file = file

        # read answer in text file
        #Text_file = open(answer_file, 'r', encoding='utf-8-sig')
        Text_file = open(answer_file, 'r', encoding='utf-8')
        answer_choice = []
        for check_c in Text_file:
            
            check_c = check_c.replace("\n","")
         
            if len(check_c.split()) > 1:
                ans, topic = check_c.split()
            else:
                ans = check_c
            #print(ans)
            answer_choice.append(ans)
        
        # check score
        full_point = len(answer_choice)
        get_points = 0
        for ans in range(len(answer_choice)):
            if select_choice[ans] == answer_choice[ans]:
                get_points += 1
        
        # commit to database
        db_topicid = Topic.query.filter_by(chapter_id=chapterid, number=topicid).first().id
        userid = User.query.filter_by(email=current_user.email).first().id
        
        # Add to Exercise table
        exerciseDB = Exercise.query.filter_by(user_id=userid, topic_id=db_topicid).first()
        # if this exercise have done before --> update score
        if exerciseDB:
            exercis_topic = Exercise.query.filter_by(user_id=userid, topic_id=db_topicid).all()
            update_score = False
            for ext in exercis_topic:
                if ext.learntype == learntype:
                    update_score = True

            if update_score:
                percent = (get_points/full_point) * 100
                exerciseDB.learntype = learntype
                exerciseDB.getpoint = get_points
                exerciseDB.percent = percent
                db.session.commit()
                print("Update database.")
                print(Exercise.query.filter_by(user_id=userid, topic_id=db_topicid).first())
            else:
                percent = (get_points/full_point) * 100
                exerciseDB = Exercise(learntype=learntype, fullpoint=full_point, getpoint=get_points,percent=percent,\
                                        user_id=userid, topic_id=db_topicid)
                db.session.add(exerciseDB)
                db.session.commit()
                print(Topic.query.filter_by(id=db_topicid).first(), " : Submit")

        # add new exercise score
        else:
            percent = (get_points/full_point) * 100
            exerciseDB = Exercise(learntype=learntype, fullpoint=full_point, getpoint=get_points,percent=percent,\
                                    user_id=userid, topic_id=db_topicid)
            db.session.add(exerciseDB)
            db.session.commit()
            print(Topic.query.filter_by(id=db_topicid).first(), " : Submit")

        # Exercise Result
        #print("############## Result ######################")
        #print("User : ",  User.query.filter_by(email=current_user.email).first().firstname)
        #print("Select : ", select_choice)
        #print("Answer : ", answer_choice)
        #print("Learn type : ", learntype)
        #print("correct : ", get_points)

        return redirect(url_for('index'))