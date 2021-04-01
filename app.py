from flask import Flask, request, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
from forms import RegisterForm, LoginForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config['SECRET_KEY'] = 'oh-so-secret'
debug = DebugToolbarExtension(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True


connect_db(app)
db.create_all()

@app.route('/')
def home():
    '''redirect to home page'''
    return redirect('/register')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    '''render register template'''
    if 'username' in session:
        return redirect(f"/users/{session['username']}")

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first = form.first_name.data
        last = form.last_name.data
        new_user = User.register(username, password, email, first, last)
        db.session.add(new_user)

        try:
            db.session.commit()
        except:
            form.username.errors.append('Username or email taken.')
            return render_template('register.html', form=form)

        session['username'] = new_user.username
        flash('Welcome! Successfully created account!', 'success')
        return redirect(f'/users/{new_user.username}')

    return render_template('register.html', form = form)


@app.route('/users/<username>')
def show_page(username):
    '''render user show page'''
    if 'username' in session:
        if session['username'] == username:

            user = User.query.get_or_404(username)
            return render_template('show.html', user=user)
        else:
            flash("Cannot view another user's information!", 'warning')
            return redirect('/')
    else:
        flash('Please login!', 'info')
        return redirect('/login')



@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    '''deletes user and any feedback associated with user'''
    if 'username' in session and session['username'] == username:
        user = User.query.get_or_404(username)
        try:
            session.pop('username')
            db.session.delete(user)
            db.session.commit()
            return redirect('/')
        except:
            flash('Unable to delete user!', 'warning')
            return redirect(f'/users/{user.username}')
    else:
        flash('You do not have permission to do that!', 'danger')
        return redirect('/')



@app.route('/login', methods = ['GET', 'POST'])
def login():
    '''render login form'''
    form = LoginForm()
    if 'username' in session:
        return redirect(f"/users/{session['username']}")
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!", "primary")
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form = form)

@app.route('/logout')
def logout():
    '''removes username from session'''
    session.pop('username')
    flash('Goodbye!', 'info')
    return redirect('/')

