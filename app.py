from flask import Flask
from database import User, db 
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

        admin_user_exists = User.query.filter_by(user_type='Admin').first()

        if not admin_user_exists:
            master_account = User(
                username= "Admin",
                user_firstname="Sys",
                user_lastname="Adm",
                user_email="admin@eventmaster.co.uk",
                user_pass_hash="hashed_password_here",
                user_type="Admin",
            ) 

            db.session.add(master_account)
            db.session.commit()
            print("System set up and admin account successfully generated")

    app.run(debug=True)