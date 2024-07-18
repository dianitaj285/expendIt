from fastapi import FastAPI
from pony.orm import Database, Required, db_session, select

app = FastAPI()
db = Database()
db.bind(provider='postgres', user='postgres', password='', host='localhost', database='expendit_dev')



@app.get("/")
async def root():
    return {"message": "Hello World this is me using python for the first time"}


class Person(db.Entity):
    name = Required(str)


db.generate_mapping(create_tables=True)

