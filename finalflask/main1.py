from flask import Flask,render_template
from flask import request
import pymongo
from pymongo import MongoClient
import json
from bson.json_util import dumps
from bson import json_util
from pymongo import MongoClient, DESCENDING

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token


app = Flask(__name__)
jwt = JWTManager(app)

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["lab"]
collection = mydb["books"]
user = mydb["User"]

app.config["JWT_SECRET_KEY"] = "this-is-secret-key" #change it

# collection.insert_one({"_id":2,"book_name":"notebook"})


@app.route('/')
def ind():
	return render_template('home.html')

@app.route("/register", methods=["POST"])
def register():
    email = request.form["email"]
    test = user.find_one({"email": email})
    if test:
        return jsonify(message="User Already Exist"), 409
    else:
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        password = request.form["password"]
        user_info = dict(first_name=first_name, last_name=last_name, email=email, password=password)
        user.insert_one(user_info)
        return jsonify(message="User added sucessfully"), 201

@app.route("/login", methods=["POST"])
def login():
    if request.is_json:
        email = request.json["email"]
        password = request.json["password"]
    else:
        email = request.form["email"]
        password = request.form["password"]

    test = user.find_one({"email": email,"password":password})
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message="Login Succeeded!", access_token=access_token), 201
    else:
        return jsonify(message="Bad Email or Password"), 401


@app.route("/books",methods=["GET"])
@jwt_required
def get_books():
    all_books = list(collection.find({}))
    return  json.dumps(all_books, default=json_util.default)

@app.route("/sortcount",methods=["GET"])
def  sortc():
    ords = dumps(mydb.books.find().sort('books_count',DESCENDING))
    return ords

@app.route("/addbooks", methods=["POST"])
@jwt_required
def add_books():
    request_payload = request.json 
    books = request_payload['books']
    existing_books = collection.find({"_id":books["name"]})
    if existing_books.count() > 0:
        for ex_books in existing_books:
            old_count = int(ex_books["books_count"])
            addition = int(books['count'])
            author_name = books['author_name']
            print(author_name)
            updated_books = addition+old_count
            print(updated_books)
            collection.find_one_and_update({"_id":books["name"]}, {"$set": {"books_count": updated_books} }, upsert=True)
    else: 
        collection.insert_one({"_id":books["name"], "books_count":books["count"],"author_name":books["author_name"]})
    return f"books are added to  library"

@app.route("/buybooks", methods=["POST"])
def buy_books():
    request_payload = request.json 
    books = request_payload['books']
    existing_books = collection.find({"_id":books["name"]})

    if existing_books.count() > 0:
        for ex_books in existing_books:
            old_count = int(ex_books["books_count"])
            requirement = int(books['count'])
            author_name = books['author_name']
            
            if requirement>old_count:
                return f"only {old_count} books are remain, you should buy a less book order."
            else:
                remaining_books = old_count-requirement
                collection.find_one_and_update({"_id": books['name']}, {'$set': {"books_count": remaining_books}}, upsert=True)
                return f"Thankyou for buying {requirement} books from my library, the total number of {books['name']} books is now {remaining_books}"
    else:
        return f" {books['name']} books is not in the library. please try buying another books."


@app.route("/remove",methods=["POST"])
def remove_books():
    request_payload = request.json
    books = request_payload['books']
    existing_books = collection.find({"_id":books["name"]})
    if existing_books.count() > 0:
        collection.delete_one({"_id":books["name"], "books_count":books["count"]})
        return f"sucessfully deleted books {books['name']}"
    else:
        return'no files found'

@app.route("/search",methods=["POST",'GET'])
def search_book():
    request_payload = request.json 
    books = request_payload['books']
    name= books.get('author_name')
    author_book = dumps(mydb.books.find({'author_name':{ "$gte": name }}))
    return author_book

#searching by given full name
    # author_book = mydb.books.find_one({'author_name':name})
    # if author_book:
    #     name = author_book.get('_id')
    #     count = author_book.get('books_count') 
    #     return f"files found the book name is  {name} the count is {count}"
    # else:
    #     return'no files found'


@app.route("/listingor",methods=["POST",'GET'])
def lst():
    request_payload = request.json 
    books = request_payload['books']
    name= books.get('author_name')
    bookname = books.get('name')
    alllist = dumps(mydb.books.find({"$or":[{'author_name':name},{'_id':bookname}]}))
    if alllist:
        return alllist
    else:
        return 'no files'
@app.route("/listingand",methods=["POST",'GET'])
def lst1():
    request_payload = request.json 
    books = request_payload['books']
    name= books.get('author_name')
    bookname = books.get('name')
    alllist = dumps(mydb.books.find({"$and":[{'author_name':name},{'_id':bookname}]}))
    if alllist:
        return alllist
    else :
        return 'no files'
if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")

