from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB Connection
def create_connection():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['library']
    return db

db = create_connection()
collection = db['books']

@app.route('/')
def index():
    books = collection.find()
    return render_template('index.html', books=books)

@app.route('/add_book', methods=['POST'])
def add_book():
    book_id = request.form.get('book_id')
    title = request.form.get('title')
    author = request.form.get('author')
    copies = int(request.form.get('copies'))

    if collection.find_one({"book_id": book_id}):
        return "Book ID already exists."
    else:
        book = {
            "book_id": book_id,
            "title": title,
            "author": author,
            "copies": copies
        }
        collection.insert_one(book)
        return redirect(url_for('index'))

@app.route('/update_book', methods=['POST'])
def update_book():
    book_id = request.form.get('book_id')
    title = request.form.get('title')
    author = request.form.get('author')
    copies = request.form.get('copies')
    
    update_fields = {}
    if title:
        update_fields["title"] = title
    if author:
        update_fields["author"] = author
    if copies:
        update_fields["copies"] = int(copies)
    
    if update_fields:
        collection.update_one({"book_id": book_id}, {"$set": update_fields})
        return redirect(url_for('index'))
    return "No fields to update."

@app.route('/delete_book', methods=['POST'])
def delete_book():
    book_id = request.form.get('book_id')
    collection.delete_one({"book_id": book_id})
    return redirect(url_for('index'))

@app.route('/check_out', methods=['POST'])
def check_out():
    book_id = request.form.get('book_id')
    book = collection.find_one({"book_id": book_id})
    
    if not book:
        return "Book ID not found."
    elif book['copies'] <= 0:
        return "No copies available for checkout."
    else:
        collection.update_one({"book_id": book_id}, {"$inc": {"copies": -1}})
        return redirect(url_for('index'))

@app.route('/check_in', methods=['POST'])
def check_in():
    book_id = request.form.get('book_id')
    collection.update_one({"book_id": book_id}, {"$inc": {"copies": 1}})
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
