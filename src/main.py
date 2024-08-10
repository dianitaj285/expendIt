from fastapi import FastAPI,HTTPException,Response,Depends,status
from fastapi.middleware.cors import CORSMiddleware
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.session_verifier import SessionVerifier
from pony.orm import Database, Required, Set, db_session
from database_setup import db
from enum import Enum
import bcrypt
from pydantic import BaseModel, EmailStr
from uuid import UUID,uuid4


app = FastAPI()
origins = [
    "http://localhost:8080", 
    "http://localhost:8000",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

cookie_params = CookieParameters()

cookie = SessionCookie(
    cookie_name="user_session",
    identifier="general_verifier",
    auto_error=True,
    secret_key="ExpendItOnlyOurCookieForSession",
    cookie_params=cookie_params,
)

class SessionData(BaseModel):
    id:int
    name: str
    lastName: str
    email: str
    role_id: int

class LoginData(BaseModel):
    email: str
    password: str

backend = InMemoryBackend[UUID, SessionData]()

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


class UserCreate(BaseModel):
    name: str
    lastName: str
    email: EmailStr
    password: str

class BasicVerifier(SessionVerifier[UUID, SessionData]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: InMemoryBackend[UUID, SessionData],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: SessionData) -> bool:
        """If the session exists, it is valid"""
        return True


verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
)

@app.post("/users/")
async def create_user(user: UserCreate, response: Response):
    with db_session:
        try:
            if User.exists(email=user.email):
                raise HTTPException(status_code=400, detail="Email already registered")
            user_role = Role.get(name="User")
            hashed_password = hash_password(user.password)
            user = User(name=user.name, lastName=user.lastName, email=user.email, password=hashed_password, role_id=user_role.id)
            
            db.commit()  


            session_data=SessionData(id=user.id, name=user.name, lastName=user.lastName, email=user.email, role_id=user_role.id)
            session = uuid4()

            await backend.create(session, session_data)
            cookie.attach_to_response(response, session)
            
            return user
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error creating user: " + str(e))


@app.get("/")
async def root():
    return {"message": "Hello World this is me using python for the first time"}

@app.post("/login/")
async def login(login_data:LoginData, response: Response):
    with db_session:

        user = User.get(email=login_data.email)

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect user information")

        if not verify_password(login_data.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect user information PASSWORDS MISMATCH")

        session = uuid4()

        session_data=SessionData(id=user.id, name=user.name, lastName=user.lastName, email=user.email, role_id=user.role_id.id)  

        await backend.create(session, session_data)
        cookie.attach_to_response(response, session)

        return f"created session for {login_data.email }"

@app.get("/whoami", dependencies=[Depends(cookie)])
async def whoami(session_data: SessionData = Depends(verifier)):
    return session_data

@app.post("/logout")
async def del_session(response: Response, session_id: UUID = Depends(cookie)):
    await backend.delete(session_id)
    cookie.delete_from_response(response)
    return "Logged out was successful"


db.generate_mapping(create_tables=True)

