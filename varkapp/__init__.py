from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = 'b298171a0f08f07bda7e60973c1461f253da4918718584d43c0cc92436326b51'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/vark_db.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

from varkapp import routes