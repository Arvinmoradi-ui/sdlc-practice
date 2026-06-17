from flask import (logging, render_template, request, redirect, url_for)
from database import (db, User, Lessons, Signups )
from werkzeug.security import generate_password_hash

def controller(app):

    # home page 
    @app.route("/")
    def home():

        return render_template('home.html')

    #dashboard page
    @app.route("/dashboard")
    def dashboard():


        return render_template('dashboard.html')
    
    #signup routing to connect the form to the database and send off the fields
    @app.route("/signup", methods=["POST"])
    def signup():
        if request.method == "POST":
            form_username = request.form.get('username')
            form_firstname = request.form.get('user_firstname')
            form_middlename = request.form.get('user_middlename')
            form_lastname = request.form.get('user_lastname')
            form_email = request.form.get('user_email')
            password = request.form.get('password')
            
            #encrypts the password here
            encrypted_password = generate_password_hash(password, method="pbkdf2:sha256")

            new_user = User(
                username=form_username,
                user_firstname=form_firstname,
                user_middlename=form_middlename,
                user_lastname=form_lastname,
                user_email=form_email,
                user_pass_hash=encrypted_password
            )

            try: 
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                return f"An error occured: {str(e)}"
            
        return render_template('signup.html')
    
    
    #login page
    @app.route("/login", methods =['GET', 'POST'])
    def login():
        if request.method == 'POST':

            return "logging in"
        return render_template('login.html')
    
    #trainings page
    @app.route("/trainings")
    def trainings():

        return render_template('trainings.html')