from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:test@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'ABCDEF'

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(350))
    body = db.Column(db.String(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, author):
        self.title = title
        self.body = body
        self.author = author

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(35))
    password = db.Column(db.String(35))
    blogs = db.relationship('Blog', backref = 'author')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')


@app.route('/blog', methods=["POST", "GET"])
def blog():
    valid = True
    title_error = ""
    body_error = ""
    if request.method == "POST":
        blog_title = request.form["title"]
        blog_text = request.form["body"]
        if blog_title == "":
            valid = False
            title_error = "Please enter a title"
        if blog_text == "":
            valid = False
            body_error = "Please enter a body"
        if valid != True:
            return render_template('newpost.html', title_error=title_error, body_error=body_error)
        user = User.query.filter_by(username = session['user']).first()
        new_blog = Blog(blog_title, blog_text, user)
        db.session.add(new_blog)
        db.session.commit()
        return redirect('/blog?q={}'.format(new_blog.id))
    if request.args.get('user'):
        userid = request.args.get('user')
        user = User.query.get(userid)
        un = user.username
        blogs = user.blogs
        return render_template('singleUser.html', username = un, blogs=blogs)

    if request.args.get('q'):
        blogid= request.args.get('q')
        blog = Blog.query.get(blogid)
        return render_template('post.html', title=blog.title, body=blog.body)
    blogs = Blog.query.order_by(Blog.id.desc()).all()
    return render_template('blog.html', blogs=blogs)

@app.route('/newpost')
def newpost():
    return render_template('newpost.html', title="New Post")

@app.route('/post')
def post():
    blogid= request.args.get('q')
    blog = Blog.query.get(blogid)
    return render_template('post.html', title=blog.title, body=blog.body)

@app.route('/')
def base():
    return redirect('/index')


@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        passwordc = request.form['passwordc']
        u_err = ""
        pw_err = ""
        pwc_err = ""

        user = User.query.filter_by(username = username).first()
        if user:
            u_err = "That username already exists"
        else:
            if not 3 < len(username) < 35:
                u_err = "Username must be between 3 and 35 characters"
        if password != passwordc:
            pw_err = "Passwords must match"
            pwc_err = "Passwords must match"
        if not 3 < len(password) < 35:
            pw_err = "Password must be between 3 and 35 characters"


        if u_err == "" and pw_err == "" and pwc_err == "":
            user = User(username, password)
            db.session.add(user)
            db.session.commit()
            session['user'] = username
            return redirect("/newpost")
        else:
            return render_template("signup.html", title="Signup", username=username, user_error=u_err, pw_error=pw_err, pwc_error=pwc_err)
    else:
        return render_template("signup.html", title="Signup")


@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username = username).first()
        if not user:
            flash("Username doesn't exist")
        else:
            if user.password != password:
                flash("Password is incorrect")
            else:
                session['user'] = username
                return render_template('/newpost', title="New Post")
    return render_template("login.html", title="Log In")

@app.route('/index')
def indexx():
    users = User.query.order_by(User.username).all()

    return render_template('index.html', users = users)

@app.route('/logout')
def logout():
    del session['user']
    return redirect('login.html')


if __name__ == "__main__":
    app.run()