from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:test@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(350))
    body = db.Column(db.String(5000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "POST":
        blog_title = request.form["title"]
        blog_text = request.formp["body"]
        new_blog = Blog(blog_title, blog_text)
        db.session.add(new_blog)
        db.session.commit()

    blogs = Blog.query.order_by(Blog.id.desc()).all()
    return render_template('blog.html', blogs=blogs)



if __name__ == "__main__":
    app.run()