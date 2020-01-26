from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import glob
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/vark_db1.db'
db = SQLAlchemy(app)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    chapters = db.relationship('Chapter', backref='subject', lazy=True)
    def __repr__(self):
        return f"Subject('{self.name}')"

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

    topics = db.relationship('Topic', backref='chapter', lazy=True)

    def __repr__(self):
        return f"Chapter('{self.name}', '{self.number}')"

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    number = db.Column(db.String, nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    contents = db.relationship('Content', backref='topic', lazy=True)

    def __repr__(self):
        return f"Topic('{self.name}', '{self.number}')"

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(250), nullable=False)
    c_type = db.Column(db.String(10), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
   
    def __repr__(self):
        return f"Content('{self.file_name}','{self.c_type}')"

def create_varkdb():

# Table 1 Subject
    path = "static/การสร้างสื่อดิจิทัล/"

# Table 2 Chapter
    # {1: chapter1 name, 2: chapter2 name, ...}
    chapter = dict()
    ch_id = 1
    for ch in glob.glob(path+"*"):
        ch_name = os.path.basename(os.path.normpath(ch))
        chapter[ch_id] = ch_name
        ch_id += 1

# Table 3 Topic
    # [{Pretest : name, 1.1 : name}]
    topic = []
    for ch in glob.glob(path+"*"):
        ch_topic = dict()
        for tp in glob.glob(ch+"/*"):
            tp_folder = os.path.basename(os.path.normpath(tp))
            tp_folder = tp_folder.split("_")[1]

            tp_id = ""
            tp_name = ""
            if tp_folder == "แบบทดสอบก่อนเรียน":
                tp_id = "P"
                tp_name = tp_folder
            elif tp_folder == "แบบทดสอบหลังเรียน":
                tp_id = "T"
                tp_name = tp_folder
            else:
                
                tp_id = tp_folder.split()[0]
                topic_name = tp_folder.split()[1:]
                for pn in range(len(topic_name)):
                    tp_name += topic_name[pn]
                    if pn+1 < len(topic_name):
                        tp_name += " "

            ch_topic[tp_id] = tp_name

        topic.append(ch_topic)
                
# Table 4 Content
    # [{'P': path},
    #  {'V' : path, 'A' : path, 'R': path , 'K' : path, 'E' : path},
    # {'T' : path },
    # ]
    content = []
    for ch in glob.glob(path+"*"):
        for tp in glob.glob(ch+"/*"):
            sub_content = dict()
            k = []
            for cont in glob.glob(tp+"/*"):
                file_name =  os.path.basename(os.path.normpath(cont))
                file_path = cont.replace("\\","/")
                if 'Ans' not in file_name:
                    if 'PreCh' in file_name:
                        sub_content['P'] = file_path
                    elif 'V' in file_name:
                        sub_content['V'] = file_path
                    elif 'A' in  file_name:
                        sub_content['A'] = file_path
                    elif 'R' in  file_name:
                        sub_content['R'] = file_path
                    elif 'K' in  file_name:
                        k.append(file_path)
                    elif 'Exercise' in file_name:
                        for ex in glob.glob(cont+"/*"):
                            ex_name = os.path.basename(os.path.normpath(ex))
                            if 'Exer' in ex_name and 'Ans' not in ex_name:
                                sub_content['E'] = ex.replace("\\","/")
                    elif 'PostCh' in file_name:
                        sub_content['T'] = file_path

            # sorted swf file.        
            if k:
                sub_content['K'] = sorted(k)

            # add content of each topic to list.
            type_sequence = ['V', 'A', 'R', 'K', 'E']
            if 'P' in sub_content or 'T' in sub_content:
                content.append(sub_content)
            else:
                sorted_content = dict()
                for seq in type_sequence:
                    sorted_content[seq] = sub_content[seq]
                content.append(sorted_content)


# Commit to Database

    # Table 1 Subject
    db.create_all()
    subject = Subject(name="การสร้างสื่อดิจิทัล")
    db.session.add(subject)

    # Table 2 Chapter
    subject = Subject.query.filter_by(name='การสร้างสื่อดิจิทัล').first()
    for c in chapter:
        db.session.add(Chapter(name=chapter[c], number=c, subject_id=subject.id))
    
    # Table 3 Topic
    chapter = Chapter.query.all()
    index = 0
    for c in chapter:
        for t in topic[index]:
            db.session.add(Topic(name=topic[index][t], number=t, chapter_id=c.id))
        index += 1
    
    # Table 4 Content
    topic = Topic.query.all()
    index = 0
    for t in topic:
        for c in content[index]:
            if c == 'K':
                for part in content[index][c]:
                    db.session.add(Content(file_name=part, c_type=c, topic_id=t.id))
            else:
                
                db.session.add(Content(file_name=content[index][c], c_type=c, topic_id=t.id))
        index += 1
    
    print(Content.query.all())
    db.session.commit()

def get_content():
    db.create_all()
    subject = Subject.query.first()
    chapter = Chapter.query.all()
    topic = Topic.query.all()
    chapters = dict()
    topics = []
    contents = []
    for c in chapter:
        chapters[c.number] = c.name
        dict_top = dict()
        for t in c.topics:
            dict_top[t.number] = t.name
            dict_cont = dict()
            k = 1
            for ct in t.contents:
                if ct.c_type == 'K':
                    dict_cont[ct.c_type+str(k)] = ct.file_name
                    k += 1
                else:
                    dict_cont[ct.c_type] = ct.file_name
            contents.append(dict_cont)
                  
        topics.append(dict_top)

    return chapters, topics, contents

create_varkdb()