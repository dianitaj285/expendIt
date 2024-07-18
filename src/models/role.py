from database_setup import db
from pony.orm import Required


class Role(db.Entity):
    name=Required(str, unique=True)

