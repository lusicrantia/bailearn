from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user  
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask import abort


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

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.String(20))
    due_date = db.Column(db.Date)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)

class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Colum(db.Text, nullable= False)
    category = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default= datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    
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

@app.route('/brain_dump/update/<int:id>', methods=['POST'])
@login_required
def update_brain_dump(id):
    dump = db.get_or_404(Brain_dump, id)  
    content = request.form.get('content', '').strip()

    if content:
        dump.content = content
        db.session.commit()
        flash("Brain dump updated!", "success")
    else:
        flash("Content cannot be empty.", "warning")

    return redirect(url_for('brain_dump'))


@app.route('/brain_dump/delete/<int:id>', methods=['POST'])
@login_required
def delete_brain_dump(id):
    dump = db.get_or_404(Brain_dump, id) 
    db.session.delete(dump)
    db.session.commit()
    
    flash("Brain dump deleted.", "info")
    return redirect(url_for('brain_dump'))


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


@app.route('/decision_journal/update/<int:id>', methods=['POST'])
@login_required
def update_decision(id):

    journal = Decision_journal.query.get_or_404(id)
   
    if request.method == 'POST':

        title = request.form.get('title', '').strip()
        decision = request.form.get('decision', '').strip()
        reason = request.form.get('reason', '').strip()
        outcome = request.form.get('outcome', '').strip()
        solution = request.form.get('solution', '').strip()

        if not title or not decision or not  reason or not outcome or not solution:
            flash('All fields are required to fill in')
            return redirect(url_for('decision_journal', id=id))

        journal.title = title
        journal.decision = decision
        journal.reason = reason
        journal.outcome = outcome
        journal.solution = solution

        db.session.commit()

        flash('Decision has been updated', 'success')
        return redirect(url_for('decision_journal'))

    return render_template('update_decision.html', journal=journal)


@app.route('/decision_journal/delete/<int:id>', methods=['POST'])
@login_required
def delete_decision(id):

    journal = Decision_journal.query.get_or_404(id)

    db.session.delete(journal)
    db.session.commit()

    flash('Decision has been deleted!', 'success')

    return redirect(url_for('decision_journal'))


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


@app.route('/flashcard/update/<int:id>', methods=['POST'])
@login_required
def update_flashcard(id):
    card = db.get_or_404(Flashcard, id)

    if card.user_id != current_user.id:
        abort(403)

    question = request.form.get('question', '').strip()
    answer = request.form.get('answer', '').strip()

    if question and answer:
        card.question = question
        card.answer = answer
        db.session.commit()
        flash("Flashcard updated!", "success")
    else:
        flash("Both question and answer are required.", "warning")

    return redirect(url_for('flashcard'))


@app.route('/flashcard/delete/<int:id>', methods=['POST'])
@login_required
def delete_flashcard(id):
    card = db.get_or_404(Flashcard, id)

    if card.user_id != current_user.id:
        abort(403)

    db.session.delete(card)
    db.session.commit()
    flash("Flashcard deleted.", "success")

    return redirect(url_for('flashcard'))

@app.route('/task_manager', methods=['GET', 'POST'])
@login_required
def task_manager():

    if request.method == 'POST':

        title = request.form.get('title', ' ').strip()
        description = request.form.get('description', ' ').strip()
        subject = request.form.get('subject', ' ').strip()
        priority = request.form.get('priority', ' ').strip()
        due_date = request.form.get('due_date')

        if not title or not description or not subject or not priority or not due_date:
            flash('All fields are required to fill in')
            return redirect(url_for('task_manager'))

        task = Task(title=title, description=description, subject=subject, priority=priority, due_date=datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else None, user_id=current_user.id)

        db.session.add(task)
        db.session.commit()

        flash('Task successfully added!', 'success')

        return redirect(url_for('task_manager'))

    tasks = Task.query.filter_by(
        user_id=current_user.id
    ).order_by(Task.created_at.desc()).all()

    return render_template('task_manager.html', tasks=tasks)
    

@app.route('/task_manager/update/<int:id>', methods=['POST'])
@login_required
def update_task(id):

    task = db.get_or_404(Task, id)

    title = request.form.get('title', ' ').strip()
    description = request.form.get('description', ' ').strip()
    subject = request.form.get('subject', ' ').strip()
    priority = request.form.get('priority', ' ').strip()
    due_date = request.form.get('due_date')

    if title or not description or not subject or not priority or not due_date:
        flash('All fields are required to fill in', 'success')
        return redirect(url_for('task_manager'))


    if title and description and subject and priority and due_date:
        task.title = title
        task.description = description
        task.subject = subject
        task.priority = priority
        task.due_date = due_date
        db.session.commit()

    return redirect(url_for('task_manager'))

@app.route('/task_manager/delete/<int:id>', methods=['POST'])
@login_required
def delete_task(id):

    task = db.get_or_404(Task, id)

    db.session.delete(task)
    db.session.commit()

    return redirect(url_for('task_manager'))

@app.route('/note', methods=['GET', 'POST'])
@login_required
def note():

    if request.form.get == 'POST':

        title = request.form.get('title', ' ').strip()
        content = request.form.get('content', ' ').strip()
        category = request.form.get('category', ' ').strip()

        if title and content and category:
            note = Notes(title=title, content=content, category=category, user_id=current_user.id)
            






with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
