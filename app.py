from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.')
            return redirect(url_for('register'))

        new_user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash('Invalid username or password.')
            return redirect(url_for('login'))

        login_user(user)
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    todo_list = Todo.query.all()
    return render_template('index.html', todo_list=todo_list)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)

@app.route("/add", methods=["POST"])
@login_required
def add():
    title = request.form.get("title")
    new_todo = Todo(title=title, complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/update/<int:todo_id>", methods=["GET", "POST"])
@login_required
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    if request.method == "POST":
        new_title = request.form.get("title")
        todo.title = new_title
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("update.html", todo=todo)

@app.route("/complete/<int:todo_id>")
@login_required
def complete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = True
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/uncomplete/<int:todo_id>")
@login_required
def uncomplete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = False
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/delete/<int:todo_id>")
@login_required
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))

@app.route('/')
def index():
    todo_list = Todo.query.all()
    return render_template('index.html', todo_list=todo_list)

@app.route("/completed_tasks")
@login_required
def completed_tasks():
    completed_todos = Todo.query.filter_by(complete=True).all()
    return render_template("completed_tasks.html", todo_list=completed_todos)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
