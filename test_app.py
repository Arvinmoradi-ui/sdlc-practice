import unittest
from app import app
from database import db, Use 
from werkzeug.security import generate_password_hash

class EventMasterTests(unittest.TestCase):

    #setting up the database
    def setUp(self):
       app.config['TESTING'] = True 
       app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_basic.db'
       self.client = app.test_client()

       with app.app_context():
           db.create_all()

           secure_pass = generate_password_hash("pass123", method="pbkdf2:sha256")
           test_