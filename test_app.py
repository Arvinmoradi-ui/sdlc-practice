import unittest
from app import app
from database import Lessons, Signups, User, db 
from werkzeug.security import generate_password_hash

class EventMasterTests(unittest.TestCase):

    #setting up the database
    def setUp(self):
       app.config['TESTING'] = True 
       app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_basic.db'
       self.client = app.test_client()

       with app.app_context():
            db.create_all()
                #creaying a student 
            secure_pass = generate_password_hash("pass123", method="pbkdf2:sha256")
            test_student = User(
                username = "student_one",
                user_firstname = "Peter",
                user_lastname = "Parker",
                user_email = "peter@spidermail.com",
                user_pass_hash = secure_pass,
                user_type= "Student"
                )
            db.session.add(test_student)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    
    # First Test: Authenticaion 
    def testing_valid_user_and_pass(self):
        """ Tests if a valid user and password has been entered and redirects the user"""
        outcome = self.client.post('/login', data={'user_email':"peter@spidermail.com", 'password':"pass123"})
        self.assertEqual(outcome.status_code, 302)

    # Second Test: RBAC showing student cant go to settings
    def testing_student_unallowed_settings(self):
        """Tests that the student cant access restricted pages due to their role not needing to"""
        #log in as student
        self.client.post('/login', data={'user_email':"peter@spidermail.com", 'password':"pass123"})
        #try and access settings page
        outcome = self.client.get('/settings', follow_redirects=True)
        #outcome to see if they were blocked
        self.assertIn(b'Student Dashboard', outcome.data)

    # Third Test: Maths and logic around early bird, VIP ticketing test
    def testing_tickets_priced_correct(self):
        """Tests that Earlybird is 20% less than normal from just inputting a number as a teacher also checking the payment goes to pending and not paid"""
        secure_pass = generate_password_hash("pass123", method="pbkdf2:sha256")
        with app.app_context():
            test_teacher = User(
                    username="teacher_one", user_firstname="Teac", 
                    user_lastname="her", 
                    user_email="teacher@test.com", 
                    user_pass_hash=secure_pass, user_type="Teacher"
                )
            db.session.add(test_teacher)
            db.session.commit()

            test_lesson = Lessons(
                lessonname = "Python Testing",
                num_spaces= 10,
                teacher_id=test_teacher.user_id,
                base_price = 100.00   
            )
            db.session.add(test_lesson)
            db.session.commit()

            target_lesson_id = test_lesson.lesson_id

        self.client.post('/login', data={'user_email':"peter@spidermail.com", 'password':"pass123"})
        self.client.post('/registrations', data={
            'lesson_id': target_lesson_id,
            'ticket_type': 'Early Bird',
            'dietary_req': 'None',
            'special_req': 'None'
        })

        with app.app_context():
            student = User.query.filter_by(username="student_one").first()
            ticket = Signups.query.filter_by(student_id=student.user_id).first()
            self.assertIsNotNone(ticket)
            self.assertEqual(ticket.money_paid, 80)
            self.assertEqual(ticket.pay_status, "Pending")


if __name__ == '__main__':
    unittest.main()

