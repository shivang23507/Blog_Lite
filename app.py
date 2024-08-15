from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_login import UserMixin, login_user, logout_user
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite"
app.config["SECRET_KEY"] = "ENTER YOUR SECRET KEY"
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.init_app(app)

class User(db.Model, UserMixin):
    __tablename__="User"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(250), nullable = False, unique = True)
    password = db.Column(db.String(250), nullable = False)

class TodO(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(200), nullable = False)
    desc = db.Column(db.String(500), nullable = False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.Column(db.String(250), nullable = False)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"

class Follow(db.Model):
    __tablename__ = "follow"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(250), nullable=False)
    follower = db.Column(db.String(250), nullable=False)
    followers = db.Column(db.Integer, default=0)
    following = db.Column(db.Integer, default=0)
    status = db.Column(db.Boolean, default=False)

db.init_app(app)

with app.app_context():
    db.create_all()


@login_manager.user_loader
def loader_user(user_id):
    return User.query.get(user_id)

@app.route('/register', methods=["GET", "POST"])
def register():
    message = ""
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if password == "" or password == None :
            message = "Enter password"
            return render_template("error.html")

        if username == "" or username == None :
            message = "Enter Username"
            return render_template("register.html", message=message)
            
        if user:
            message = "Username already exits"
            return render_template("register.html", message=message)
        
        newUser = User(username = username, password = password)
       
        db.session.add(newUser)
        db.session.commit()
        
        return redirect(url_for("login"))

    return render_template("register.html", message = message)


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if username == "" or username == None :
            message = "Enter Username"
            return render_template("login.html", message=message)

        if password == "" or None:
            message = "Enter password"
            return render_template("error.html")

        if user == None:
            message =  "Not a user. Please register first."
            return render_template("register.html", message=message)
        else:
            if user.password == password:
                username = user.username
                return redirect(url_for("dashboard", username = username))
            else:
                message = "Wrong password"
                return render_template("login.html", message=message)
    else:
        return render_template("login.html")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route('/update/<int:sno>/<string:username>', methods = ["GET", "POST"])
def update(sno, username):
    if request.method == "GET":
        todo = TodO.query.filter_by(sno = sno).first()
        return render_template("update.html", todo = todo, username = username)
    elif request.method == "POST":
        title = request.form['title']
        desc = request.form["desc"]
        todo = TodO.query.filter_by(sno = sno).first()
        todo.title = title
        todo.desc = desc
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for("dashboard", username = username))

@app.route('/delete/<int:sno>/<string:username>')
def delete(sno,username):
    todo = TodO.query.filter_by(sno = sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("dashboard", username = username))

@app.route('/view/<int:sno>/<string:username>', methods = ["GET", "POST"])
def view(sno, username):
    if request.method == "GET":
        todo = TodO.query.filter_by(sno = sno).first()
        return render_template("view.html", todo = todo, username = username)
    elif request.method == "POST":
        title = request.form['title']
        desc = request.form["desc"]
        todo = TodO.query.filter_by(sno = sno).first()
        todo.title = title
        todo.desc = desc
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for("dashboard", username = username))

@app.route('/visit/<string:user_name>/<string:username>', methods = ["GET", "POST"])
def visit(user_name, username):
    if request.method == "POST":
        title = request.form['title']
        desc = request.form["desc"]
        todo = TodO(title = title, desc = desc, user = user_name)
        db.session.add(todo)
        db.session.commit()
    allTodo = TodO.query.all()
    print(allTodo)
    return render_template("visit.html", allTodo = allTodo, user_name = user_name, username = username)

@app.route("/search/<string:username>", methods=["GET", "POST"])
def search(username):
    if request.method == "POST":
        user_name = request.form.get("username")
        user = User.query.filter_by(username=user_name).first()

        if user == None:
            error =  "Not a user"
            return error
        else:
            user_name = user.username
            return redirect(url_for("visit", user_name = user_name, username = username))
    else:
        return redirect(url_for("search", username = username))

@app.route('/visit_view/<int:sno>/<string:user_name>/<string:username>', methods = ["GET", "POST"])
def visit_view(sno, user_name, username):
    if request.method == "GET":
        todo = TodO.query.filter_by(sno = sno).first()
        return render_template("visit-view.html", todo = todo, user_name = user_name, username = username)

@app.route('/dashboard/<string:username>', methods = ["GET", "POST"])
def dashboard(username):
    if request.method == "POST":
        title = request.form['title']
        desc = request.form["desc"]
        todo = TodO(title = title, desc = desc, user = username)
        db.session.add(todo)
        db.session.commit()
    allTodo = TodO.query.all()
    print(allTodo)
    followers_count = Follow.query.filter_by(user=username, status=True).count()
    following_count = Follow.query.filter_by(follower=username, status=True).count()
    return render_template("dashboard.html", allTodo = allTodo, username = username, followers_count=followers_count, following_count=following_count)

@app.route('/followers/<string:user_name>/<string:username>', methods=["GET", "POST"])
def followers(user_name, username):
    folli = Follow.query.filter_by(user=user_name, follower=username).first()
    if not folli:
        folli = Follow(user=user_name, follower=username)
        db.session.add(folli)
        db.session.commit()

    if request.method == "POST":
        if not folli.status:
            folli.followers += 1
            folli.status = True
        else:
            folli.followers -= 1
            folli.status = False
        db.session.commit()
        return redirect(url_for('followers', user_name=user_name, username=username))

    # Calculate followers and following
    followers_count = Follow.query.filter_by(user=user_name, status=True).count()
    following_count = Follow.query.filter_by(follower=user_name, status=True).count()

    allfoll = Follow.query.all()
    return render_template("followers.html", user_name=user_name, username=username, followers_count=followers_count, following_count=following_count, folli=folli)

@app.route('/add/<string:username>', methods = ["GET", "POST"])
def add(username):
    if request.method == "POST":
        title = request.form['title']
        desc = request.form["desc"]
        todo = TodO(title = title, desc = desc, user = username)
        db.session.add(todo)
        db.session.commit()
    allTodo = TodO.query.all()
    print(allTodo)
    return render_template("add.html", allTodo = allTodo, username = username)

if __name__ == "__main__":
    app.run(debug = True)