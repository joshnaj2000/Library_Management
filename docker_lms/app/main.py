import pymongo
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Optional



class User(BaseModel):
    fname: Optional[str] = None
    lname: Optional[str] = None
    age: Optional[int] = None
    email: Optional[str] = None
    password: Optional[str] = None
    borrowed_books:Optional[list]=None



class Book(BaseModel):
    isbn: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[str] = None
    availability: Optional[int] = None

app = FastAPI()

class LibraryManagement:

    def __init__(self):
        self.connectionString = "mongodb+srv://joshnaj123:joshna%40123@librarymanagementsystem.2dn2jpw.mongodb.net/Library_management_system"
        self.myclient = pymongo.MongoClient(self.connectionString)
        self.db = self.myclient["Library_management_System"]
        try:
            self.myclient.server_info()
            print("Connection started successfully")
            if self.myclient and self.db is not None:
                print("Connection established successfully")
            else:
                print("Exiting program due to connection failure")
        except pymongo.errors.ConnectionFailure as e:
            print(e)

# lib = LibraryManagement()

@app.post("/insert-user/{user_id}")
def insert_document_user(user_id: int, user: User, lib: LibraryManagement = Depends()):
    try:
        existing_user = lib.db.user.find_one({"id": user_id})
        if existing_user:
            print("User already exists")
        else:
            user_data = user.dict()
            user_data["id"] = user_id
            lib.db.user.insert_one(user_data)
            return { "User inserted"}
    except Exception as e:
        print(e)

@app.post("/insert-book/{book_id}")
def insert_document_book(book_id: int, book: Book, lib: LibraryManagement=Depends()):
    try:
        existing_book = lib.db.book.find_one({"book_id": book_id})
        if  existing_book:
            print("Book already exists")
        else:
            book_data = book.dict()
            book_data["book_id"] = book_id
            lib.db.book.insert_one(book_data)
            return {"Book inserted "}
    except Exception as e:
        print(e)
        

@app.get("/get-user/{user_id}",response_model=User)
def get_user(user_id:int, lib:LibraryManagement=Depends()):
        try:
            user_details = lib.db.user.find_one({"id":user_id})
            if not user_details:
                return {"user_details not found"}
            else:
                return user_details
        except Exception as e:
            print(e)
        
@app.get("/get-book/{book_id}",response_model=Book)
def get_book(book_id:int , lib : LibraryManagement=Depends()):
    try:
        book_details = lib.db.book.find_one({"book_id":book_id})
        if not book_details:
            return {"Book not found"}
        else:
            return book_details
    except Exception as e:
        print(e)


@app.put("/update-user/{user_id}", response_model=User)
def update_user(user_id: int, user: User, lib: LibraryManagement = Depends()):
    try:
        user_details = lib.db.user.find_one({"id": user_id})
        if not user_details:
            return {"User not exists"}
        update_data = {}
        if user.fname is not None:
            update_data["fname"] = user.fname
        if user.lname is not None:
            update_data["lname"] = user.lname
        if user.age is not None:
            update_data["age"] = user.age
        if user.email is not None:
            update_data["email"] = user.email
        lib.db.user.update_one({"id": user_id}, {"$set": update_data})
        updated_user = lib.db.user.find_one({"id": user_id})
        return updated_user
    except Exception as e:
        print(e)

@app.put("/update-book/{book_id}")
def update_book(book_id :int , book:Book , lib : LibraryManagement=Depends()):
    try:
        book_details = lib.db.book.find_one({"book_id": book_id})
        if not book_details:
            return {"Book not exists"}
        update_data = {}
        if book.isbn is not None:
            update_data["isbn"] = book.isbn
        if book.title is not None:
            update_data["title"] = book.title
        if book.author is not None:
            update_data["author"] = book.author
        if book.year is not None:
            update_data["year"] = book.year
        if book.availability is not None:
            update_data["availability"] = book.availability
        lib.db.book.update_one({"book_id": book_id}, {"$set": update_data})
        lib.db.book.find_one({"id": book_id})
        return {"Book Updated "}
    except Exception as e:
        print(e)


@app.delete("/delete-user/{user_id}")
def delete_user(user_id: int, lib: LibraryManagement = Depends()):
    try:
        user_details = lib.db.user.find_one({"id": user_id})
        if user_details:
            if 'borrowed_books' in user_details:
                return_book(lib, user_id, user_details['borrowed_books'])               
            lib.db.user.delete_one(user_details)
            return {"User deleted successfully"}
        else:
            return {"User not exists"}
    except Exception as e:
        print(e)
        return {"error": str(e)}

@app.delete("/delete-book/{book_id}")
def delete_book(book_id:int , lib :LibraryManagement=Depends()):
    try:
        book_details = lib.db.book.find_one({"book_id":book_id})
        if book_details:
            lib.db.book.delete_one(book_details)
            return {"Book deleteed Successfully"}
        else:
            return {"Book not found"}
    except Exception as e:
        print(e)


@app.put("/borrow_book/{user_id}")
def borrow_book(user_id: int, book_id: int, lib: LibraryManagement = Depends()):
    try:
        existing_user = lib.db.user.find_one({"id": user_id})

        if existing_user:
            existing_book = lib.db.book.find_one({"book_id": book_id, "availability": {"$gt": 0}})

            if existing_book and existing_book['book_id'] not in existing_user['borrowed_books']:
                lib.db.book.update_one({"book_id": existing_book['book_id'], "availability": {"$gt": 0}}, {"$inc": {"availability": -1}})
                lib.db.user.update_one({"id": user_id}, {"$addToSet": {"borrowed_books": existing_book['book_id']}})
                return {"Book borrowed successfully."}
            else:
                return {"Book not found or not available."}
        else:
            return {"User not found."}
    except Exception as e:
        return {"Error updating book"}



@app.put("/return-book/{user_id}")
def return_book(user_id: int, book_id: int, lib: LibraryManagement = Depends()):
    try:
        existing_user = lib.db.user.find_one({"id": user_id})

        if existing_user:
            existing_book = lib.db.book.find_one({"book_id": book_id})

            if existing_book and existing_book['book_id']  in existing_user['borrowed_books']:
                lib.db.book.update_one({"book_id": existing_book['book_id']}, {"$inc": {"availability": 1}})
                lib.db.user.update_one({"id": user_id}, {"$unset": {"borrowed_books": existing_book['book_id']}})
                return {"Book returned successfully."}
            else:
                return {"Book not found or not available."}
        else:
            return {"User not found."}
    except Exception as e:
        return {"Error updating book"}



































# @app.delete("/delete-user/{user_id}")
# def delete_user(user_id :int ,  lib : LibraryManagement=Depends()):
#     try:
#         user_details = lib.db.user.find_one({"id":user_id})
#         if user_details:
#             # if borrow_book in user_details:
#             #     return_Book()
#             lib.db.user.delete_one(user_details)
#             return { "User deleted successfully"}
#         else:
#             return {"User not exists"}
#     except Exception as e:
#         print(e)















