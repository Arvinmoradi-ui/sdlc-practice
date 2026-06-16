from flask import (logging, render_template, request, redirect, url_for)
from database import (db, User, Lessons, Signups )

def controller(app):

    # home page 
    @app.route("/")
    def home():

        return render_template('home.html')

    #dashboard page
    @app.route("/dashboard")
    def dashboard():


        return render_template('dashboard.html')
    
    @app.route("/signup")
    def signup():

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