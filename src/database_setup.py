from pony.orm import Database, Required, db_session, select

db = Database()

db.bind(provider='postgres', user='postgres', password='password', host='localhost', database='expendit')

db.generate_mapping(create_tables=True)


class Person(db.Entity):
    name = Required(str)
