from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, url_for, request, flash, redirect
from insert_content import InsertSubject, InsertContent
from database import get_content

app = Flask(__name__)
app.config['SECRET_KEY'] = 'b298171a0f08f07bda7e60973c1461f253da4918718584d43c0cc92436326b51'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/vark_db.db'
db = SQLAlchemy(app)
# Anirach Test


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    chapter, topic, content = get_content()
    return render_template('index.html', chapter=chapter, topic=topic, content=content)


@app.route('/insert-content', methods=['GET', 'POST'])
def insert_content():
    sform = InsertSubject()
    form = InsertContent()
    if sform.validate_on_submit():
        subject = sform.subject.data
        return render_template('insert-content.html', title=subject, form=form)

    return render_template('insert-content.html', title="Create subject", sform=sform)


if __name__ == "__main__":
    app.run(debug=True)
