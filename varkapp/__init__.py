from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'b298171a0f08f07bda7e60973c1461f253da4918718584d43c0cc92436326b51'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/vark_db.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from varkapp import routes