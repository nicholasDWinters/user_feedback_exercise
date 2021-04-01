from flask import Flask, request, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
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
            db.session.rollback()
            form.username.errors.append('Username or email taken.')
            return render_template('register.html', form=form)

        session['username'] = new_user.username
        flash('Welcome! Successfully created account!', 'success')
        return redirect(f'/users/{new_user.username}')

    return render_template('register.html', form = form)


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
        
        db.session.delete(user)
        db.session.commit()
        session.pop('username')
        return redirect('/login')
    else:
        flash('You do not have permission to do that!', 'danger')
        return redirect('/')


@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    '''renders the feedback form'''
    form = FeedbackForm()
    user = User.query.get_or_404(username)
    if 'username' not in session:
        flash('You do not have permission to add feedback. Please login.', 'warning')
        return redirect('/login')
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        username = user.username
        feedback = Feedback(title = title, content = content, username = username)
        try:
            db.session.add(feedback)
            db.session.commit()
            flash('Added feedback!', 'success')
            return redirect(f'/users/{user.username}')
        except:
            flash('Unable to add feedback', 'warning')
            return redirect(f'/users/{user.username}')
    return render_template('add_feedback.html', user = user, form = form)


@app.route('/feedback/<int:id>/update', methods=["GET", "POST"])
def edit_feedback(id):
    '''update a specific feedback'''
    feedback = Feedback.query.get_or_404(id)
    form = FeedbackForm(obj = feedback)
    if 'username' not in session:
        flash('Do not have permission to edit', 'warning')
        return redirect('/login')
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        flash('Edited successfully!', 'success')
        return redirect(f"/users/{session['username']}")

    return render_template('edit_feedback.html', feedback = feedback, form = form)

@app.route('/feedback/<int:id>/delete', methods = ["POST"])
def delete_feedback(id):
    '''delete the specified feedback'''
    feedback = Feedback.query.get_or_404(id)

    if session['username'] == feedback.user.username:
        db.session.delete(feedback)
        db.session.commit()
        return redirect(f"/users/{session['username']}")
    else:
        flash('You do not have permission to do that!', 'warning')
        return redirect('/login')

