from flask import Flask
from database import db 
from controllers import controller

#create app
app = Flask(__name__)
#configures dataabase
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eventmaster.db'
#initialize database
db.init_app(app)

controller(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)