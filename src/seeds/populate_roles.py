from pony.orm import db_session
from os import sys, getcwd
sys.path.insert(1, getcwd())
from database_setup import db
from models.role import Role


@db_session
def populate_roles():
    admin=Role(name='admin')
    user=Role(name='user')
    db.commit()

if __name__ == '__main__':
    populate_roles()    