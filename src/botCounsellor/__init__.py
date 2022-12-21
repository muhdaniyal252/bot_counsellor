from flask import Flask,render_template,url_for,flash,redirect,request,abort,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField,TextAreaField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired,Email,EqualTo,Length,ValidationError
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,UserMixin,login_user,current_user,logout_user,login_required
import secrets
from PIL import Image
import os
from flask_marshmallow import Marshmallow
import nltk
# nltk.download('punkt') #done already
# nltk.download('wordnet') #done already
from nltk.stem import WordNetLemmatizer
import json
import pickle
import numpy as np
import random


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost:3306/fypDatabase'


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
loginManager = LoginManager(app)
loginManager.login_view = 'login'
mm = Marshmallow(app)

questions = [
        'What would you like to do in your youth age? (a) help others(b) explore the world(c) make good money(d) build good stuff',
        'What do you think the well done job is?(a) making assets(b) keep the enviroment neat and clean(c) creating something out of material(d) solving a problem skillfully',
        'Ultimate goal in life(a) understand humans perfectly(b) invent something new(c) be president(d) make the world better',
        'Interested in(a) technology(b) learning how computer works(c) intellectual ideas(d) knowing about nature',
        'Normally, you like to do(a) vlogging(b) computing(c) internet surfing(d) think about new ideas',
        'In school, your favourite class involves(a) performing(b) human behavior(c) deep thinking(d) experimenting',
        'help other and delay work/don\'t care (select one)',
        'knowing how machines work/use them anyways (select one)',
        'aimbitious, love coming with own idea/go with the flow (select one)',
        'socializing/stay at home (select one)',
        'concerned about state of enviroment/not (select one)',
        'interested in body healing/not interested (select one)',
        'work with own hands and outdoor/lazy (select one)',
        'interested in graphic designing/not interested (select one)',
        'good with numbers and detials oriented/bad at it (select one)',
        'work with people and lead to final stage/too much for me (select one)',
        'Your friend know you as?(a) organizer(b) goes with gut feelings(c) shows initiative, don\'t need anyone to tell what to do(d) getting job done',
        'what do you think people consider you as?(a) risk taker(b) logical(c) generous, care taker(d) cool headed and curious'
    ]
starts = ['yes','yeah','yup','sure','why not','start','ok','okay']
fields = ['engineering','media','entrepreneur','medical','computer scinece']
fieldval = [0 for _ in range(len(fields))]
questionIndex = -1

def sendSuggestion(field):
    return 'according to my analysis, i think you should go for ' + field.upper() + ' as you undergrad field'


from botCounsellor import routes


