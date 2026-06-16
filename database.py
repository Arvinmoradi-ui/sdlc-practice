from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (Date, String, ForeignKey, Text, DateTime)
from sqlalchemy.orm import (DeclarativeBase, Mapped, backref, mapped_column, relationship)
from datetime import date, datetime
from typing import (List, Optional)

# initialise the database here 
db = SQLAlchemy()

# TABLE 1 - Users shwoing RBCA and authentication

class User(db.Model):
    __tablename__ = 'users'

    #primary key of user id
    user_id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    #username field in table
    username: Mapped[str] = mapped_column(String(50), unique=True)
    #real first name 
    user_firstname: Mapped[str] = mapped_column(String(15), unique=False)
    #real last name
    user_lastname: Mapped[str] = mapped_column(String(15), unique=False)
    #real middle name 
    user_middlename: Mapped[Optional[str]] = mapped_column(String(20), unique=False)
    #user's email
    user_email: Mapped[str] = mapped_column(String(100), unique = True)
    #user's password
    user_pass_hash: Mapped[str] = mapped_column(String(128))
    #user's account type
    user_type: Mapped[str] = mapped_column(String(20), default='Student')

    #relationships
    lessons_taught: Mapped[List["Lessons"]] = relationship(backref="teacher")
    sign_ups: Mapped[List["Signups"]] = relationship(backref ="student")


# TABLE 2 - Training Lessons

class Lessons(db.Model):
    __tablename__ = 'training_lessons'

    #primary key of lesson id
    lesson_id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    #lesson name
    lessonname: Mapped[str] = mapped_column(String(150), unique=False)
    #lesson description
    lesson_desc: Mapped[Optional[str]] = mapped_column(Text)
    #lesson date and time
    date_and_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    #total spaces
    num_spaces: Mapped[int] = mapped_column()
    #teacher id
    teacher_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))

    #relationships
    sign_ups: Mapped[List["Signups"]] = relationship(backref ="lesson")


#TABLE 3 - Signups

class Signups(db.Model):
    ___tablename__ = 'signups'

    #primary key of signup id
    signup_id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    #progress made as a percentage 
    progress: Mapped[int] = mapped_column(default = 0)
    #singup date
    signup_date: Mapped[datetime] =mapped_column(DateTime, default=datetime.utcnow)

    #relationships
    student_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))
    lessons_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))
