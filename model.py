from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import sqlite3

# Create the SQLAlchemy instance
db = SQLAlchemy()


def connect_to_database(database_uri):
    db.init_app(app)  # Initialize the app with the database configuration
    return db


database_name = "book.db"

# Connect to or create the database file
conn = sqlite3.connect("/mnt/c/users/n0044/desktop/code/Library3/book.db")

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

if conn and cursor:
    # You can now execute SQL queries using 'cursor' here
    # For example, create a 'books' table if it doesn't exist
    """cursor.execute('''
            CREATE TABLE IF IT DOESN'T EXISTS book (
                id INTEGER PRIMARY KEY,
                title TEXT,
                author TEXT,
                description TEXT,
                subjects TEXT,
                thumbnail_url BLOB)
                )
        ''')"""
    cursor.execute("SELECT * FROM book")
    print(cursor.fetchall())

    """print("Command execute successfully...")"""
    # commit our command
    conn.commit()

    # Insert a book into the 'book' table
    cursor.execute("INSERT INTO book (title DATATYPE, author DATATYPE, description DATATYPE, subjects DATATYPE, thumbnail_url DATATYPE) VALUES (?, ?)",
                   ("Book Title", "Author Name", "description TEXT", "subjects TEXT", "thumbnail BLOB"))
    conn.commit()

    # Close the database connection when done
    cursor.close()
    conn.close()


"""
def init_db(app):
    with app.app_context():
        db.create_all()
"""

# Define a function to connect to the database


class book(db.Model):
    __tablename__ = "book"  # Defines the table name
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    subjects = db.Column(db.String(255))
    thumbnail_url = db.Column(db.String(255))


def __init__(self, title, author, description=None, subjects=None, thumbnail_url=None):
    # __init__ allows you to create a new object
    self.title = title
    self.author = author
    self.description = description
    self.subjects = subjects
    self.thumbnail_url = thumbnail_url


class User(db.Model):
    __tablename__ = "Login"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


def __init__(self, username, password):
    self.username = username
    self.password = password


# Hash a password before saving it to the database


def hash_password(password):
    return generate_password_hash(password, method='sha256')


def check_password(self, password):
    return check_password_hash(self.password, password)
