from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (Date, String, ForeignKey, Text, DateTime, Float)
from sqlalchemy.orm import (DeclarativeBase, Mapped, backref, mapped_column, relationship)
from datetime import date, datetime, timezone
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
    #user's biography
    user_bio: Mapped[Optional[str]] = mapped_column(Text)

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
    date_and_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    #total spaces
    num_spaces: Mapped[int] = mapped_column()
    #teacher id
    teacher_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))
    #base price of normal ticket
    base_price: Mapped[float] = mapped_column(Float, default=0.0)


    #relationships
    sign_ups: Mapped[List["Signups"]] = relationship(backref ="lesson")


#TABLE 3 - Signups

class Signups(db.Model):
    __tablename__ = 'signups'

    #primary key of signup id
    signup_id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    #progress made as a percentage 
    progress: Mapped[int] = mapped_column(default = 0)
    #singup date
    signup_date: Mapped[datetime] =mapped_column(DateTime, default=datetime.now(timezone.utc))
    
    #ticket details: type, money paid, pay status, dietary req, other requirements
    ticket_type: Mapped[str] = mapped_column(String(25), default='Standard')
    money_paid: Mapped[Float] = mapped_column(Float, default=0.0)
    pay_status: Mapped[str] = mapped_column(String(25), default='Pending')
    dietary_req: Mapped[Optional[str]] = mapped_column(Text)
    Special_req: Mapped[Optional[str]] = mapped_column(Text)

    #relationships
    student_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))
    lessons_id: Mapped[int] = mapped_column(ForeignKey('training_lessons.lesson_id'))


# formatting and syntax found and used from SQLAlchemy documentation at:
#https://docs.sqlalchemy.org/en/20/orm/quickstart.html
