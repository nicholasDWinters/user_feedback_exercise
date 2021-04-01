from flask import Flask, request, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
from forms import RegisterForm

app = Flask(__name__)

app.config['SECRET_KEY'] = 'oh-so-secret'
debug = DebugToolbarExtension(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True


connect_db(app)

@app.route('/')
def home():
    '''redirect to home page'''
    return redirect('/register')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    '''render register template'''
    form = RegisterForm()
    return render_template('register.html', form = form)