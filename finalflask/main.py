from flask import Flask,render_template
from flask import request
import pymongo
from pymongo import MongoClient
import json
from bson import json_util

app = Flask(__name__)
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["librarie"]
collection = mydb["books"]
# collection.insert_one({"_id":2,"book_name":"notebook"})


@app.route('/')
def ind():
	return render_template('home.html')

@app.route("/books",methods=["GET"])
def get_books():
    all_books = list(collection.find({}))
    return  json.dumps(all_books, default=json_util.default)
@app.route("/addbooks", methods=["POST"])
def add_books():
    request_payload = request.json 
    books = request_payload['books']
    existing_books = collection.find({"_id":books["name"]})
    if existing_books.count() > 0:
        for ex_books in existing_books:
            old_count = int(ex_books["books_count"])
            addition = int(books['count'])
            updated_books = addition+old_count
            collection.find_one_and_update({"_id":books["name"]}, {"$set": {"books_count": updated_books} }, upsert=True)
    else: 
        collection.insert_one({"_id":books["name"], "books_count":books["count"]})
    return f"books are added to  librarie ."

@app.route("/buybooks", methods=["POST"])
def buy_books():
    request_payload = request.json #if the key doesnt exist, it will return a None
    books = request_payload['books']
    existing_books = collection.find({"_id":books["name"]})

    if existing_books.count() > 0:
        for ex_books in existing_books:
            old_count = int(ex_books["books_count"])
            requirement = int(books['count'])
            
            if requirement>old_count:
                return f"only {old_count} books are remain, you should buy a less book order."
            else:
                remaining_books = old_count-requirement
                collection.find_one_and_update({"_id": books['name']}, {'$set': {"books_count": remaining_books}}, upsert=True)
                return f"Thankyou for buying {requirement} books from my librarie, the total number of {books['name']} books is now {remaining_books}"
    else:
        return f" {books['name']} books is not in the librarie. please try buying another books."

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")

