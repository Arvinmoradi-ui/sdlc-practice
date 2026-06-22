import os 
from flask import (app, flash, logging, render_template, request, redirect, session, url_for, flash)
from database import (db, User, Lessons, Signups )
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import (secure_filename)

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
            form_user_type = request.form.get('user_type')
            
            #encrypts the password here
            encrypted_password = generate_password_hash(password, method="pbkdf2:sha256")

            new_user = User(
                username=form_username,
                user_firstname=form_firstname,
                user_middlename=form_middlename,
                user_lastname=form_lastname,
                user_email=form_email,
                user_pass_hash=encrypted_password,
                user_type = form_user_type
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
    @app.route("/trainings", methods=['GET', 'POST'])
    def trainings():
        
        if 'user_id' not in session:
            return redirect(url_for('login'))

        current_user_type = session.get('user_type') 
        
        if request.method == 'POST':
            if current_user_type not in ['Admin', 'Teacher']:
                flash("Unauthorised Action: You do not have permission to create trainings.", "error")
                return redirect(url_for('trainings'))

            form_name = request.form.get('lessonname')
            form_desc = request.form.get('lesson_desc')
            form_date_str = request.form.get('date_and_time')
            form_spaces = request.form.get('num_spaces')
            form_price = request.form.get('base_price')
            
            #teacehrs would be self assigned but an admin can basically
            # choose whatever teacehr they want
            if current_user_type == 'Admin':
                assigned_teacher_id = request.form.get('teacher_id')
            else:
                assigned_teacher_id = session['user_id']

            from datetime import datetime
            form_date = datetime.strptime(form_date_str, '%Y-%m-%dT%H:%M')
            
            new_lesson = Lessons(
                lessonname=form_name,
                lesson_desc=form_desc,
                date_and_time=form_date,
                num_spaces=int(form_spaces),
                base_price=float(form_price),
                teacher_id=assigned_teacher_id
            )
            
            try:
                db.session.add(new_lesson)
                db.session.commit()
                flash("Training session successfully created!", "success")
                return redirect(url_for('trainings', view='manage'))
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {str(e)}", "error")
                return redirect(url_for('trainings'))
        
        # view for admins
        if current_user_type == 'Admin':
            current_view = request.args.get('view', 'create')
            manage_list = Lessons.query.all()
            teacher_list = User.query.filter_by(user_type='Teacher').all()
            return render_template('trainings.html', current_view=current_view, manage_list=manage_list, teacher_list=teacher_list)
            
        #view for teachers
        elif current_user_type == 'Teacher':
            current_view = request.args.get('view', 'create')
            manage_list = Lessons.query.filter_by(teacher_id=session['user_id']).all()
            return render_template('trainings.html', current_view=current_view, manage_list=manage_list)
            
        #view for students
        elif current_user_type == 'Student':
            current_view = request.args.get('view', 'enrolled')
            my_signups = Signups.query.filter_by(student_id=session['user_id']).all()
            return render_template('trainings.html', current_view=current_view, my_signups=my_signups)
    
    #routing for individual pages for each training session
    @app.route("/hub/<int:lesson_id>")
    def training_hub(lesson_id):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        lesson = Lessons.query.filter_by(lesson_id=lesson_id).first()

        if not lesson:
            flash("Training session not found", "error")
            return redirect(url_for('trainings'))
        
        from database import Materials
        materials = Materials.query.filter_by(lesson_id=lesson_id).all()

        return render_template('training_hub.html', lesson=lesson, materials=materials)
    
    #routing for students to upload files 

    app.config['uploads_folder'] = 'static/uploads'

    @app.route("/upload_material/<int:lesson_id>", methods=['POST'])
    def upload_material(lesson_id):
        if 'user_id' not in session or session.get('user_type') not in ['Admin', 'Teacher']:
            flash("Unauthorised Action", "error")
            return redirect(url_for('login'))
        
        uploaded_file = request.files.get('lesson_file')

        if uploaded_file and uploaded_file.filename != '':
            filename = secure_filename(uploaded_file.filename)

            if not os.path.exists(app.config['uploads_folder']):
                os.makedirs(app.config['uploads_folder'])
            
            file_path = os.path.join(app.config['uploads_folder'], filename)
            uploaded_file.save(file_path)

            from database import Materials
            new_files = Materials(file_name=filename, file_path=file_path, lesson_id=lesson_id)

            db.session.add(new_files)
            db.session.commit()
            flash("Files successfully uploaded!", "success")
        else:
            flash("no file selected", "error")
        
        return redirect(url_for('training_hub', lesson_id=lesson_id))




    @app.route("/registrations", methods=['GET', 'POST'])
    def registrations():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        current_user_type = session.get('user_type')

        if request.method == 'POST':
            if current_user_type != 'Student':
                flash("Only students can book tickets.", "error")
                return redirect(url_for('registrations'))
            
            #grab the form data for the trainings
            lesson_id = request.form.get('lesson_id')
            ticket_type = request.form.get('ticket_type')
            dietary_info = request.form.get('dietary_req')
            special_info = request.form.get('special_req')
            lesson_info = Lessons.query.filter_by(lesson_id=int(lesson_id)).first()
            ticket_price = lesson_info.base_price
            if ticket_type == 'VIP':
                ticket_price = lesson_info.base_price * 1.5
            elif ticket_type == 'Early Bird':
                ticket_price = lesson_info.base_price * 0.8

            #create the new entry to signups defaulting to pending
            new_signup = Signups(
                student_id=session['user_id'],
                lessons_id=lesson_id,
                ticket_type=ticket_type,
                money_paid=ticket_price,
                pay_status='Pending',
                dietary_req=dietary_info,
                Special_req=special_info
            )

            try:
                db.session.add(new_signup)
                db.session.commit()
                flash("Registration successful! Please complete your payment.", "success")
                return redirect(url_for('registrations', view='my_regs'))
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {str(e)}", "error")
                return redirect(url_for('registrations'))
        

        if current_user_type in ['Admin', 'Teacher']:
            current_view = request.args.get('view', 'all')
            if current_view == 'Pending':
                filtered_signups = Signups.query.filter_by(pay_status='Pending').all()
                dynamic_title = 'Pending Approvals'
            elif current_view == 'completed':
                filtered_signups = Signups.query.filter_by(pay_status='Completed').all()
                dynamic_title = 'Completed Payments'
            else:
                filtered_signups = Signups.query.all()
                dynamic_title = "Master Student List"

            return render_template('registrations.html', all_signups=filtered_signups, current_view=current_view, page_title=dynamic_title)
        
        elif current_user_type == 'Student':
            current_view = request.args.get('view', 'browse')

            if current_view =='browse':
                available_lessons = Lessons.query.all()
                return render_template('registrations.html', current_view=current_view, available_lessons=available_lessons)
            
            elif current_view == 'my_regs':
                my_signups = Signups.query.filter_by(student_id=session['user_id']).all()
                return render_template('registrations.html', current_view=current_view, my_signups=my_signups)
            
            elif current_view == 'book':
                lesson_id = request.args.get('lesson_id')
                lesson_to_book = Lessons.query.filter_by(lesson_id=lesson_id).first()
                return render_template('registrations.html', current_view=current_view, lesson=lesson_to_book)
