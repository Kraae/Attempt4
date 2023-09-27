import os
from flask import Flask, session, jsonify, request, redirect, render_template, url_for
from model import Book, hash_password, db, User
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length
import requests


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///book.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_RECORD_QUERIES"] = True
app.config['SQLALCHEMY_ECHO'] = True
app.config['API_KEY'] = "key"

db.init_app(app)


def init_db(app):
    with app.app_context():
        db.create_all()


# key
API_KEY = "AIzaSyCUg3r9gfvDYIa_y33XCA5wobD3S4do8g8"

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create a Book Model


class book(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))

# Function that will search for books in Google Books API


def search_google_book(query):
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query, "key": API_KEY, "fields": "items(id,volumeInfo(title,authors,description,categories,imageLinks/thumbnail))"}

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        book = data.get("items", [])
        # Check if categories, description, or images exist in volumeInfo
        for book in book:
            if "description" not in book.get("volumeInfo", {}):
                book["volumeInfo"]["description"] = "Description not available"
            if "categories" not in book.get("volumeInfo", {}):
                book["volumeInfo"]["categories"] = ["N/A"]
            if "imageLinks" not in book.get("volumeInfo", {}):
                # If no thumbnail present, use a default image
                book["volumeInfo"]["imageLinks"] = {
                    "thumbnail": "https://cdn3.iconfinder.com/data/icons/minecraft-icons/512/Book.png"}
        return book
    else:
        return []


@app.route('/')
def my_index():
    book = book.query.all()
    if 'user_id' in session:
        # User is logged in, perform actions
        return render_template('index.html', book=book)
    return redirect(url_for('login'))


'''
@app.route('/')
def Index():
    if 'user_id' in session:
        # User is logged in, perform actions
        return render_template('index.html')
    return redirect(url_for('login'))
'''
"""
@app.got_first_request
# runs only once when the Flask application is started,
# ensuring that the initialization tasks are executed before the first request is handled.
def initialize():
    # Your code here that requires the app context
    with app.app_context():
        # Initialize the db with the app
        db.init_app(app)
   
        db.create_all()
    # Create initial data or perform any other one-time setup
    # like adding some initial books to the database
        initial_books = [
            Book(title='Book 1', author='Author 1'),
            Book(title='Book 2', author='Author 2'),
            # Add more books as needed
        ]

        for book in initial_books:
            db.session.add(book)

        db.session.commit()
"""

"""
@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title')
    author = request.form.get('author')
    book = Book(title=title, author=author)
    db.session.add(book)
    db.session.commit()
    return redirect(url_for('index'))
"""
# Adds books from API to the database


@app.route('/add_book/<book_id>')
def add_book(book_id):
    google_book = search_google_books(book_id)
    if google_book:
        google_book = google_book[0]
        title = google_book.get("volumeInfo", {}).get("title", "")
        author = ", ".join(google_book.get(
            "volumeInfo", {}).get("authors", []))
        description = request.form['description']
        subjects = request.form['subjects']
        thumbnail_url = request.form['thumbnail_url']

    # Create a new book object and add it to the database
    book = book(title=title, author=author, description=description,
                subjects=subjects, thumbnail_url=thumbnail_url)
    db.session.add(book)
    db.session.commit()
    return redirect(url_for('index'))

# Defines a WTForms form for the edit profile page


class EditForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=6, max=200)])


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    book = book.query.get_or_404(id)
    if request.method == 'POST':
        form = edit()
        if form.validate_on_submit():
            # updates user's profile
            current_user.username = form.username.data
            current_user.password = form.password.data

        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', form=form)


@app.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    book = book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return jsonify(message="Book Removed")


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('search_query')
        book = search_google_book(query)
        thumbnail_url = request.form['thumbnail_url']
        return render_template('search_results.html', book=book, query=query, thumbnail_url=thumbnail_url)

    return render_template('search.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Register user: produce form and handle form submission
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if username is already taken
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists. Please choose another."
        # Hash password before saving it
        hashed_password = hash_password(password)
        # Create a new user with the hashed password
        user = User(username=username, password=hashed_password)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Produce login form or handle login form
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            # If passwords match then the authentication occurs
            # Set up user session and redirect to a secured page
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    logout_user()
    session.pop('user_id', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
