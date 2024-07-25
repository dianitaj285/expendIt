from fastapi import FastAPI,HTTPException
from pony.orm import Database, Required, Set, db_session
from database_setup import db
from enum import Enum
import bcrypt
from pydantic import BaseModel, EmailStr

app = FastAPI()
db = Database()
db.bind(provider='postgres', user='postgres', password='', host='localhost', database='expendit_dev')


class Currency(Enum):
    COP = "COP"
    USD = "USD"

class Role(db.Entity):
    name=Required(str, unique=True)
    users = Set('User')  

class User(db.Entity):
    name=Required(str, unique=True)
    lastName=Required(str)
    email=Required(str, unique=True)
    password=Required(str)
    role_id=Required(Role)

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

class UserCreate(BaseModel):
    name: str
    lastName: str
    email: EmailStr
    password: str

@app.post("/users/")
async def create_user(user: UserCreate):
    with db_session:
        try:
            if User.exists(email=user.email):
                raise HTTPException(status_code=400, detail="Email already registered")
            user_role = Role.get(name="User")
            hashed_password = hash_password(user.password)
            user = User(name=user.name, lastName=user.lastName, email=user.email, password=hashed_password, role_id=user_role.id)
            return user
        except Exception as e:
            return "Error creating user: " + str(e)


@app.get("/")
async def root():
    return {"message": "Hello World this is me using python for the first time"}




db.generate_mapping(create_tables=True)

