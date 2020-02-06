from varkapp import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(10), unique=False, nullable=False)
    firstname = db.Column(db.String(20), unique=False, nullable=False)
    lastname = db.Column(db.String(20), unique=False, nullable=False)
    age = db.Column(db.String(10), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    user_type = db.Column(db.String(120), unique=False, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    def __repr__(self):
        return f"User('{self.gender}', '{self.firstname}', '{self.lastname}', '{self.age}', '{self.email}')"

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    learntype = db.Column(db.String(10), unique=False, nullable=False)
    fullpoint = db.Column(db.String(10), unique=False, nullable=False)
    getpoint = db.Column(db.String(10), unique=False, nullable=False)
    percent = db.Column(db.String(10), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    def __repr__(self):
        return f"Exercise('{self.learntype}','{self.fullpoint}','{self.getpoint}','{self.percent}','{self.user_id}')"


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
            kfile = dict()
            for ct in t.contents:
                if ct.c_type == 'K':
                    kfile[ct.c_type+str(k)] = ct.file_name
                    k += 1
                else:
                    if kfile:
                        dict_cont['K'] = kfile
                    dict_cont[ct.c_type] = ct.file_name
            contents.append(dict_cont)
                  
        topics.append(dict_top)
  
    return chapters, topics, contents

