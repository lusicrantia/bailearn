from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user  
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


# Run the application
app = Flask(__name__)


# Creating a database file where the data will be stored
app.config['SECRET_KEY'] = 'project-arvid-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projectyero.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Model

# Creating a database for sql lite
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Brain_dump(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Decision_journal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    decision = db.Column(db.Text, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    outcome = db.Column(db.Text, nullable=False)
    solution = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),  nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    # Check if the user is authenticated
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))

    # Get data from the login form
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists
        user = User.query.filter_by(username=username).first()

        # Verify username and password
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('homepage'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or  not password or not confirm_password:
            flash('All fields are required.', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('register.html')


        new_user = User(
            username=username,
            password=generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logout.')
    return redirect(url_for('homepage'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/brain_dump', methods=['GET', 'POST'])
@login_required
def brain_dump():

    if request.method == 'POST':
        content = request.form.get('content', '').strip()

        if content:
            new_dump = Brain_dump(content=content)

            db.session.add(new_dump)
            db.session.commit()

            flash("Your brain dump has been saved!", "success")
            return redirect(url_for('brain_dump'))

        flash('Write something before saving.', 'warning')

    dumps = Brain_dump.query.order_by(
        Brain_dump.created_at.desc()
    ).all()

    return render_template('brain_dump.html', dumps=dumps)


@app.route('/focus-timer')
@login_required
def focus_timer():
    return render_template('focus_timer.html')


@app.route('/decision_journal', methods=['GET', 'POST'])
@login_required
def decision_journal():

    if request.method == 'POST':

        title = request.form.get('title', '').strip()
        decision = request.form.get('decision', '').strip()
        reason = request.form.get('reason', '').strip()
        outcome = request.form.get('outcome', '').strip()
        solution = request.form.get('solution', '').strip()

        if not title or not decision or not reason:
            flash('All fields are required to fill in')
            return redirect(url_for('decision_journal'))

        entry = Decision_journal(title=title, decision=decision, reason=reason, outcome=outcome, solution=solution)

        db.session.add(entry)
        db.session.commit()

        flash('Decision has been added', 'success')
        return redirect(url_for('decision_journal'))

    journals = Decision_journal.query.order_by(Decision_journal.created_at.desc()).all()

    return render_template('decision_journal.html', journals=journals)


@app.route('/flashcard', methods=['GET', 'POST'])
@login_required
def flashcard():

    if request.method == 'POST':

        question = request.form.get('question', '').strip()
        answer = request.form.get('answer', '').strip()

        if question and answer:

            card = Flashcard(
                question=question,
                answer=answer,
                user_id=current_user.id
            )

            db.session.add(card)
            db.session.commit()

            flash('Flashcard created successfully', 'success')
            return redirect(url_for('flashcard'))

        flash('All fields are required to fill in', 'warning')

    cards = Flashcard.query.filter_by(
        user_id=current_user.id
    ).order_by(Flashcard.created_at.desc()).all()

    return render_template('flashcard.html', cards=cards)


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
