from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'rsk-je-zakon'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
#Line below only required once, when creating DB.
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    drinks = db.Column(db.Integer)


#db.create_all()

#some_student = Student(
#            name="Jaka",
#            drinks=0,
#        )
#db.session.add(some_student)
#db.session.commit()

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        new_user = User(
            email=request.form["email"],
            name=request.form["name"],
            password=generate_password_hash(request.form["password"], method='pbkdf2:sha256', salt_length=8)
        )
        if User.query.filter_by(email=request.form["email"]).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect(url_for('domov'))
    return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('That email does not exist, please try again.')
        elif (check_password_hash(pwhash=user.password, password=password)):
            login_user(user)
            return redirect(url_for('domov'))
        else:
            flash('Password incorrect, please try again.')
    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route('/domov', methods=["GET", "POST"])
@login_required
def domov():
    return render_template("domov.html", name=current_user.name, logged_in=True)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/clan/<int:student_id>')
@login_required
def clan(student_id):
    student = Student.query.filter_by(id=student_id).first()
    return render_template("clan.html", logged_in=True, name=student.name, drinks=student.drinks, id=student_id)

@app.route('/edit/<int:student_id>')
@login_required
def edit(student_id):
    print(student_id)
    
    student = Student.query.filter_by(id=student_id).first()
    student.drinks -= 1
    db.session.commit()

    return redirect(url_for('clan', student_id=student_id))


if __name__ == "__main__":
    app.run(debug=True)
