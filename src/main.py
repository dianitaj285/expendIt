from fastapi import FastAPI
from pony.orm import Database, Required, Set, db_session
from database_setup import db

app = FastAPI()
db = Database()
db.bind(provider='postgres', user='postgres', password='', host='localhost', database='expendit_dev')



@app.get("/")
async def root():
    return {"message": "Hello World this is me using python for the first time"}


class Role(db.Entity):
    name=Required(str, unique=True)
    users = Set('User')  

class User(db.Entity):
    name=Required(str, unique=True)
    email=Required(str, unique=True)
    role_id=Required(Role)


db.generate_mapping(create_tables=True)

