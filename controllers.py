from flask import (flash, logging, render_template, request, redirect, session, url_for, flash)
from database import (db, User, Lessons, Signups )
from werkzeug.security import check_password_hash, generate_password_hash

def controller(app):

    # home page 
    @app.route("/")
    def home():

        return render_template('home.html')

    #dashboard page
    @app.route("/dashboard")
    def dashboard():
        #quick security check
        if 'user_id' not in session: 
            return redirect(url_for('login'))
        
        current_user_id = session['user_id']
        current_user_type = session['user_type']

        #initliase the fields shown on the dash
        admin_events = 0
        admin_attendees = 0 
        admin_revenue = 0
        admin_tasks_list = []
        teacher_lessons = []
        student_signups = []

        if current_user_type == 'Admin':
            admin_events = Lessons.query.count()
            admin_attendees = Signups.query.count()
            revenue_query = db.session.query(db.func.sum(Signups.money_paid)).scalar()
            admin_revenue = revenue_query if revenue_query else 0.0 
            admin_tasks_list = Signups.query.filter_by(pay_status='Pending').limit(10).all()

        elif current_user_type == 'Teacher':
            teacher_lessons = Lessons.query.filter_by(teacher_id=current_user_id).all()

        elif current_user_type == 'Student':
            student_signups = Signups.query.filter_by(student_id=current_user_id).all()

        return render_template('dashboard.html',
                               events_count=admin_events,
                               attendee_count=admin_attendees,
                               revenure_total=admin_revenue,
                               pending_tasks=admin_tasks_list,
                               my_lessons=teacher_lessons,
                               my_signups=student_signups)

    
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
    
    
    #login page
    @app.route("/login", methods =['GET', 'POST'])
    def login():
        if request.method == 'POST':
            login_email = request.form.get('user_email')
            login_pass = request.form.get('password')

            user = User.query.filter_by(user_email=login_email).first()

            if user and check_password_hash(user.user_pass_hash, login_pass):
                session['user_id'] = user.user_id
                session['user_type'] = user.user_type
                return redirect(url_for('dashboard'))
            
            else: 
                flash("Incorrect email or password, please try again.")
                return redirect(url_for('login'))
           
        return render_template('login.html')
    
    #trainings page
    @app.route("/trainings")
    def trainings():

        return render_template('trainings.html')